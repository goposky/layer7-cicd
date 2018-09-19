# CA API Gateway (Layer7) CICD

This repo is intended to provide a simple way to spin up CA API Gateway environments on your laptop using docker containers. This can be used for local development, experimentation, or educational purposes. The setup also allows you to create a Jenkins pipeline to migrate policies easily across your various gateway environments.

#### Prequisites
- Git is installed on your PC. See https://git-scm.com
- Docker is installed on your PC. See https://docs.docker.com/install \
Note for windows users: On a windows machine you will need to install docker for windows which will disable virtualbox. You can toggle between Hyper-V and Virtualbox by following this page: https://gist.github.com/BergWerkGIS/11eb186f471f7b91cd793372b3f50de5 \
Also, once installed, in Docker preferences, disable the "Start docker when you log in" option.
- You have a valid CA API gateway developer license

#### Setup
This section describes preparatory steps which need to be done one time. The commands listed here are in `bash`. If you are on a Windows PC, use equivalent windows command wherever applicable.

Clone this repo and change directory into the repo. 
```bash
git clone https://gitlab.com/goposky/layer7-cicd.git
cd layer7-cicd
```
Note: If you are behind a corporate proxy you might need to specify the proxy url in your git config.
```
git config --global http.proxy http://proxyuser:proxypwd@proxy.server.com:proxy.port
git config --global https.proxy https://proxyuser:proxypwd@proxy.server.com:proxy.port
```

All commands from now on are run from within this repo base directory.\
Next, copy your CA API license file to the right location and rename it to `license.xml`.
```bash
cp <path-to-your-license-file> gateway/docker/license.xml
```
Next, copy the GMU utility (script and jar files) into the `gmu/gmu-docker` directory. Once copied, the directory should have contents as listed below:
```bash
README.md                       # this README file
gmu                             # the GMU script renamed
lib                             # contains jars required by GMU
GatewayMigrationUtility.jar     # the main GMU jar
```

Next, build the gmu-slave docker image.
```bash
docker build gmu -t gmu-slave   # Builds gmu-slave image
docker images                   # Lists built images
```
The setup is now complete.
#### Spin up the environment(s)
Within the `gateway` directory is a `docker-compose.yml` file which defines the containers that can be spun up as part of this setup. You can list the defined services by running the following command.
```bash
$ docker-compose -f gateway/docker-compose.yml config --services | sort
gateway-dev
mysql-dev
gateway-prd
gateway-tst
gmu-slave
jenkins
nginx-stub
```
As you can see in the output, the following services are defined:
- 3 gateway containers representing different environments
- A mysql container that will persist state of the gateway-dev
- A jenkins container
- A gmu container that would act as a Jenkins slave
- An nginx-stub container to serve as stub for automated tests.

To spin up the dev gateway and the gmu container, specify those services in the `docker-compose up` command.
```bash
docker-compose -f gateway/docker-compose.yml up -d gateway-dev mysql-dev gmu-slave  # Spins up the specified containers
docker ps   # Shows running containers
```
#### Browse gateway using Policy Manager
There are 2 ways to do this:
1. Using Policy Manager client
2. Using Java web start\
   First ensure that Java version 1.8 or below is intalled on your PC, along with the Java Web Start program.
   ```bash
   javaws gateway/manager.jnlp
   ```
Login to Policy Manager with the default credentials (which you can find within the docker-compose.yml file).

#### Use the GMU (Gateway Management Utility) to manage your gateways
The GMU utility is packaged into a docker image (refer `gmu/Dockerfile`) and the `gmu-slave` container uses this image. We can use this container to run adhoc GMU commands as well, without needing to install the GMU tool locally on your PC. This container also functions as a Jenkins slave in our CICD setup.\

With the `gmu-slave` container running, we may run the commands the following way:
```bash
docker exec -it gmu-slave gmu <command>
# where gmu-slave is the gmu-slave container name
```
It can be handy to set an alias to the above command. For bash:
```bash
alias gmu="docker exec -it gmu-slave gmu"
```
Note that the local directory `gmu/mnt` will be now mounted within the gmu-slave container in the location `~/mnt`. We can use this local directory to supply the gmu argument properties file, import bundle, and to store the output of gmu commands. An example `dev-argFile.properties` file is supplied in the directory to use with the `gateway-dev` gateway.\
\
Loading a policy to the gateway:
```bash
gmu migrateIn -z mnt/<gmu-argument-properties-filename> --bundle mnt/<import-bundle-xml-filename> --results mnt/<results-xml-filename> --destFolder /ziggo
```
Browsing the gateway:
```bash
gmu browse -z mnt/<gmu-argument-properties-filename> -r -showIds
```
The output should list all the deployed services, policies and folders.\

When you are done, you can shutdown all the containers by running the following.
```bash
docker-compose -f gateway/docker-compose.yml down
```

#### Setup Jenkins
If you want to implement CICD with your gateway environments you need Jenkins. Jenkins can be run with the following command. 
```bash
docker-compose -f gateway/docker-compose.yml up -d jenkins
```
Jenkins configuration will be persisted on restart of container, since everything is stored in the mounted directory `../jenkins-home`. Ensure that you have the following plugins installed:
1. Blue Ocean 
2. Build Timeout 
3. Build Trigger Badge Plugin 
4. Console Badge 
5. Email Extension Plugin 
6. embeddable-build-status 
7. Gitlab Authentication plugin 
8. Gitlab Hook Plugin 
9. Gitlab Logo Plugin 
10. Gitlab Merge Request Builder 
11. Gitlab Plugin 
12. LDAP Plugin 
13. PAM Authentication plugin 
14. Pipeline 
15. Pipeline: Github Groovy Libraries 
16. Role-based Authorization Strategy 
17. SSH Slaves plugin 
18. Timestamper 
19. Violation Comments to GitLab Plugin 
20. Violation Comments to GitLab Plugin 
21. Workspace Cleanup Plugin

TODO: Pipeline setup

#### Full pipeline demo
To spin up the environments with all containers mentioned in the previous section, run the following command:
(Note: Spinning up all the containers defined in the docker-compose this way will cause docker to use up a lot of system resources. You might want to tweak the memory settings under Docker preferences on your PC.)
```bash
docker-compose -f gateway/docker-compose.yml up -d
```

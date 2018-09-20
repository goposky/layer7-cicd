# CA API Gateway (Layer7) local development environment with CI/CD

This repo is intended to provide a simple way to spin up CA API Gateway environments on your laptop using docker containers. This can be used for local development, experimentation, or educational purposes. The setup also allows you to create a Jenkins pipeline to migrate policies easily across your various gateway environments.

## Prequisites
- Git is installed on your PC. See https://git-scm.com
- Docker is installed on your PC. See https://docs.docker.com/install \
Note for windows users: On a windows machine you will need to install docker for windows which will disable virtualbox. You can toggle between Hyper-V and Virtualbox by following this page: https://gist.github.com/BergWerkGIS/11eb186f471f7b91cd793372b3f50de5 \
In Docker preferences, disable the "Start docker when you log in" option as buggy behaviour has been noticed with Docker on system startup.
- Java 1.8 is installed on your PC. Newer version does not work well with the Policy Manager web start.
  Download from here: http://www.oracle.com/technetwork/java/javase/downloads/java-archive-javase8-2177648.html
- You have a valid CA API gateway developer license

Note: Most of the steps listed below involve using a command-line terminal. The commands listed here were written and tested in a `bash` terminal. If you are using a non-bash terminal (for example, the Windows command prompt), use the equivalent commands wherever applicable.

## Setup
This section describes preparatory steps which need to be done one time.

Clone this repo and change directory into the repo. 
```bash
git clone https://gitlab.com/goposky/layer7-cicd.git
cd layer7-cicd
```
Note: If you are behind a corporate proxy you might need to specify the proxy url in your git config as follows.
```
git config --global http.proxy http://<proxyuser>:<proxypwd>@<proxy.server>:<proxy.port>
git config --global https.proxy https://<proxyuser>:<proxypwd>@<proxy.server>:<proxy.port>
```

All commands from now on are run from within this repo base directory.\
Next, copy your CA API Gateway license file to the `license` directory and rename it to `license.xml`.
```bash
cp <path-to-your-license-file> license/license.xml
```
Next, copy the GMU utility (script and jar files) into the `gmu` directory. Once copied, the directory should have contents as listed below:
```bash
README.md                       # a README file
lib                             # directory containing jars required by GMU
GatewayMigrationUtility.jar     # the main GMU jar
GatewayMigrationUtility.sh      # the GMU shell script for Unix
GatewayMigrationUtility.bat     # the GMU bat script for Windows
```
Append the `PATH` environment variable with the `gmu` directory path.\
Next, build the gmu-slave docker image. This step is required only if you intend to use run the Jenkins pipeline demo.
```bash
docker build . -t gmu-slave     # Builds gmu-slave image
docker images                   # Lists built images
```
Note: The GMU tool is non-sharable and usage is associated with your CA API Gateway license.\
The setup is now complete.
## Spin up the environment
The `docker-compose.yml` file defines the containers that can be spun up as part of this setup. You can list the defined services by running the following command.
```bash
$ docker-compose config --services
gateway-dev
mysql-dev
gateway-prd
gateway-tst
jenkins
gmu-slave
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
docker-compose up -d gateway-dev mysql-dev   # Spins up the specified containers
docker ps   # Shows running containers
```
Note: To persist the state of the dev gateway upon restart, it is configured to use a msyql database (refer `docker-compose.yml`) instead of in-memory database. Therefore we need to also spin up the `mysql-dev` container along with the `gateway-dev` container.
### Browse gateway using Policy Manager
There are 2 ways to do this:
1. Using Policy Manager fat client
2. Using Java web start
   ```bash
   javaws manager.jnlp
   ```
Login to Policy Manager with the default credentials, which you can find within the `docker-compose.yml` file. Connect with `localhost` on the port that is mapped to gateway port 8443 (also configured within `docker-compose.yml`). For example, for the `gateway-dev` this is port 8441.

### Use the GMU (Gateway Management Utility) to manage your gateways
The `workspace` directory may be used to supply the gmu argument properties file, import bundle, and to store the output of gmu commands. An example `dev-argFile.properties` file is supplied in the directory to use with the `gateway-dev` gateway.\
Loading a policy to the gateway:
```bash
GatewayMigrationUtility.sh migrateIn -z workspace/<gmu-argument-properties-filename> \
                                     --bundle workspace/<import-bundle-xml-filename> \
                                     --results workspace/<results-xml-filename> \
                                     --destFolder /ziggo
```
Browsing the gateway:
```bash
GatewayMigrationUtility.sh browse -z workspace/<gmu-argument-properties-filename> -r -showIds
```
The output should list all the deployed services, policies and folders.

When you are done, you can shutdown the containers by running the following.
```bash
docker-compose down
```

## CI/CD demo with Jenkins
TODO: Following section is incomplete.

If you want to implement CICD with your gateway environments you need Jenkins. Jenkins can be run with the following command. 
```bash
docker-compose up -d jenkins
```
Jenkins configuration will be persisted on restart of container, since everything is stored in the mounted directory `jenkins`. Ensure that you have the following plugins installed:
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

The `gmu-slave` container uses the `gmu-slave` image we built in the setup section. This container also functions as a Jenkins slave in our CICD setup. Spin up the gmu slave.
```bash
docker-compose up -d gmu-slave
```

To spin up the environments with all containers mentioned in the previous section, run the following command:
```bash
docker-compose up -d
```
Note: Spinning up all the containers defined in the docker-compose this way will cause docker to use up a lot of system resources. You might want to tweak the memory settings under Docker preferences on your PC.

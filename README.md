# CA API Gateway (Layer7) CICD
------------------------------
This repo is intended to provide a simple way to spin up CA API Gateway environments on your laptop using docker containers. This can be used for local development, experimentation, or educational purposes. The setup also allows you to create a Jenkins pipeline to migrate policies easily across your various gateway environments.

#### Prequisites
- Git is installed on your PC. See https://git-scm.com
- Docker is installed on your PC. See https://docs.docker.com/install \
(Note for windows users: On a windows machine you will need to install docker for windows which will disable virtualbox. You can toggle between Hyper-V and Virtualbox by following this page: https://gist.github.com/BergWerkGIS/11eb186f471f7b91cd793372b3f50de5)
- You have a valid CA API gateway developer license

#### Setup 
Clone this repo and change directory into the repo. 
```
git clone https://gitlab.com/goposky/layer7-cicd.git
cd layer7-cicd
```
All commands from now on are run from within this repo base directory.\
Next, copy your CA API license file to the right location and rename it to `license.xml`
```
cp <path-to-your-license-file> gateway/docker/license.xml
```

#### Spin up the environment(s)
Within the `gateway` folder is a `docker-compose.yml` file which defines the containers that can be spun up as part of this setup. You can list the defined services by running the following command.
```
$ docker-compose -f gateway/docker-compose.yml config --services | sort
gateway-dev
gateway-prd
gateway-tst
gmu-slave
jenkins
nginx-stub
```
As you can see in the output, the following services are defined:
- 3 gateway containers representing different environments
- A jenkins container
- A gmu container that would act as a Jenkins slave
- An nginx-stub container to serve as stub for automated tests.

To spin up the environments with all containers mentioned in the previous section, run the following command:
```
docker-compose -f gateway/docker-compose.yml up -d
```
To bring down the environments, run:
```
docker-compose -f gateway/docker-compose.yml down
```
To spin up a single gateway and the gmu container, specify those services in the `docker-compose up` command.
```
docker-compose -f gateway/docker-compose.yml up -d gateway-dev gmu-slave
```
#### Browse gateway using policy manager
```
javaws gateway/manager.jnlp
```
Java webstart opens the policy manager login screen. Login with the default credentials (which you can find within the docker-compose.yml file).

#### Use the GMU (Gateway Management Utility) to manage your gateways
The GMU utility is packaged into a docker image and the `gmu-slave` container uses this image. This container functions as a Jenkins slave in our CICD setup. We can use this container to run adhoc commands as well, without needing to install the GMU tool locally on your PC.\
Once, the `gmu-slave` container is running, we may run the commands the following way:
```
docker exec -it gateway_gmu-slave_1 gmu <command>
# where gateway_gmu-slave_1 is the gmu-slave container name
```
It can be handy to set an alias as follows:
```
alias gmu="docker exec -it gateway_gmu-slave_1 gmu"
```
Loading a policy to the gateway:
```
gmu migrateIn -z /usr/local/gmu/mnt/argFile.properties --bundle <path-of-bundle-xml-to-import> --results /usr/local/gmu/mnt/results.xml --destFolder /ziggo
# Note that we supply the properties file via a local directory that is mounted into the container. The mounted volume is described in the docker-compose.yml. The same mounted volume is used to save the results file.
```
Browsing the gateway:
```
gmu browse -z /usr/local/gmu/mnt/argFile.properties -r -showIds
```
The output should list all the deployed services, policies and folders.

#### Setup Jenkins
If you want to implement CICD with your gateway environments you need Jenkins. Jenkins can be run with the following command. 
```
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


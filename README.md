# CA API Gateway (Layer7) CICD
------------------------------
This repo is intended to provide a simple way to spin up CA API Gateway environments on your laptop using docker containers. This can be used for local development, experimentation, or educational purposes. The setup also allows you to create a Jenkins pipeline to migrate policies easily across your various gateway environments.

#### Prequisites
- Git is installed on your PC. See https://git-scm.com
- Docker is installed on your PC. See https://docs.docker.com/install \
(Note for windows users: On a windows machine you will need to install docker for windows which will disable virtualbox. You can toggle between Hyper-V and Virtualbox by following this page: https://gist.github.com/BergWerkGIS/11eb186f471f7b91cd793372b3f50de5)
- You have a valid CA API gateway developer license

#### Setup demo environment 
Clone this repo and change directory into the repo. 
```
git clone https://gitlab.com/goposky/layer7-cicd.git
cd layer7-cicd
```
All commands from now on are run from within this repo base directory.\
Next, copy your CA API license file to the right location and rename it to `license.xml`
```
cp <path-to-your-license-file> gateway/license/license.xml
```

#### Explaining the demo environment
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

#### Run gateway environments
To spin up the demo environment with all containers mentioned in the previous section, run the following command.
```
docker-compose -f gateway/docker-compose.yml up -d
```
However, if you prefer to run only 1 or few of the components, you can spin up just that specific container by specifying in the `docker-compose up` command.\
To spin up a single gateway and the gmu container, run the following command.
```
docker-compose -f gateway/docker-compose.yml up -d gateway-dev gmu-slave
```
#### Browse gateway using policy manager
```
javaws gateway/manager.jnlp
```
Java webstart opens the policy manager login screen. Login with the default credentials.
#### Use the GMU (Gateway Management Utility) to manage your gateways
First set gmu in your PATH.
```
export PATH=$PATH:<path to the gmu directory>
```
Loading a policy to the gateway:
```
gmu migrateIn -z gmu/argFile.properties --bundle gateway/build/demo-bundle.xml --results gmu/results.xml --destFolder /ziggo
```
Browsing the gateway:
```
gmu browse -z gmu/argFile.properties -r -showIds
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


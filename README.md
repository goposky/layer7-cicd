# Layer7 CICD demo
----------------

## Prequisites
- Git is installed on your PC.
- Docker is installed on your PC.\
Note for windows users: On a windows machine you will need to install docker for windows which will disable virtualbox. You can toggle between Hyper-V and Virtualbox by following this page:  
https://gist.github.com/BergWerkGIS/11eb186f471f7b91cd793372b3f50de5

## Directory listing
`./src` - Source code (including directory structure) for all services on all gateways\
`./gmu` - Gateway Management Utility\
`./gateway` - Gateway installation files (docker)\
`./scripts` - contains bash scripts with helpful gmu commands


## Setup demo environment 
Clone this repo and change directory into the repo. 
```
git clone https://gitlab.com/goposky/layer7-cicd.git
cd layer7-cicd
```
All commands in the following sections are run from the repo base directory.

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
As you can see, there are 3 gateway containers representing different environments, a jenkins container, a gmu container (that would act as a Jenkins slave), and an nginx-stub container to serve as stub for automated tests.

#### Run gateway environments
To spin up the demo environment with all containers mentioned in the previous section, run the following command.
```
docker-compose -f gateway/docker-compose.yml up -d
```
If you prefer to run only 1 or few of the components, you can spin up just that specific container by specifying in the `docker-compose up` command.\
```
docker-compose -f gateway/docker-compose.yml up -d gateway-dev gmu-slave # Runs 1 gateway environment and the gmu container
```
#### Browse gateway using policy manager
```
javaws gateway/manager.jnlp
```
Java webstart opens the policy manager login screen. Login with the default credentials.
#### Set gmu in your path:
```
export PATH=$PATH:<path to the gmu directory>
```
#### Load demo policy using gmu
```
gmu migrateIn -z gmu/argFile.properties --bundle gateway/build/demo-bundle.xml --results gmu/results.xml --destFolder /ziggo
```
#### Browse gateway using gmu
```
gmu browse -z gmu/argFile.properties -r -showIds
```
The output should list all the deployed services, policies and folders.

#### Setup Jenkins
Jenkins can be run with the following command. 
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


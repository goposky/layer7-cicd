# Layer7 CICD demo
----------------

## Directory listing
`./src` - Source code (including directory structure) for all services on all gateways  
`./gmu` - Gateway Management Utility  
`./gateway` - Gateway installation files (docker)  
`./pipeline` - Jenkinsfile and other pipeline components  


## Setup demo environment
### Run gateway
`docker-compose -f gateway/docker-compose.yml up -d` 
### Open policy manager
`javaws gateway/manager.jnlp`
Login with the default credentials
### Set gmu in your path:
`export PATH=$PATH:<path to the gmu directory>`  
### Load demo policy using gmu
`gmu migrateIn -z gmu/argFile.properties --bundle gateway/build/demo-bundle.xml --results gmu/results.xml --destFolder /ziggo`
### Browse gateway using gmu
`gmu browse -z gmu/argFile.properties -r -showIds`


## Setup Jenkins pipeline
From the repo base directory, run jenkins:
`docker run -d -v pipeline:/var/jenkins_home -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts`

Install following plugins:
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



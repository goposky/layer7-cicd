FROM goposky/jenkins-ssh-slave:alpine

COPY --chown=jenkins:jenkins ./gmu-docker/ /home/jenkins/gmu/
ENV PATH "$PATH:/home/jenkins/gmu"


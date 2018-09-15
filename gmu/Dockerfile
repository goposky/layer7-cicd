FROM jenkinsci/ssh-slave
LABEL maintainer="mail@goposky.com"
# copy gmu directory and set in path
COPY --chown=jenkins:jenkins ./gmu-docker /home/jenkins/gmu
ENV PATH "$PATH:/home/jenkins/gmu"

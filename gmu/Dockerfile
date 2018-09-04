FROM jenkinsci/slave:alpine
# copy gmu directory to path
COPY ./gmu-docker /usr/local/gmu
USER root
RUN chown -R jenkins:jenkins /usr/local/gmu
USER jenkins
ENV PATH "$PATH:/usr/local/gmu"

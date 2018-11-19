#!/usr/bin/python3

properties = open("/home/amresh/Projects/ziggo/layer7/gitlab.com/layer7-cicd/workspace/dev-argFile.properties", "r")

port = None
username = None
host = None

with properties as fp:
    for line in fp:
        if "port" in line:
            port = line[line.rindex("=") + 1:]
        if "username" in line:
            username = line[line.rindex("=") + 1:]
        if "host" in line:
            host = line[line.rindex("=") + 1:]
        

print("url: " + "https://" + host.strip() + ":" + port.strip())
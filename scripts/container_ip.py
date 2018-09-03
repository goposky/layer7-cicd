#!/usr/bin/python3.6
import os
import argparse
import fnmatch

from prettytable import PrettyTable

parser  = argparse.ArgumentParser(
            description = "Script to get a ip addresses of multiple running containers"
        )
parser.add_argument("-n", "--name", help="the name of the container to get the ip address from, wildcards in the name are supported to get a list. This should be in quotes.", required=True)
args = parser.parse_args()

# Get a list of current running containers, and filter through this using the given name filter
running_containers_cmd = "docker ps --format \"{{.Names}}\""
running_containers = (os.popen(running_containers_cmd).read()).splitlines()

pattern = args.name
matches = fnmatch.filter(running_containers, pattern)

table = PrettyTable()
table.field_names = ["Name", "IPAddress"]
table.align["Name"] = "l"
table.align["IPAddress"] = "r"

for match in matches:
    container_ip_cmd = "docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + match + ""
    container_ip = os.popen(container_ip_cmd).read().rstrip('\r\n')
    table.add_row([match, container_ip])

print(table)

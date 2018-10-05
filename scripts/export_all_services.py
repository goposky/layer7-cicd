#!/usr/bin/python3

import os
import argparse
import pathlib
import subprocess
import re

from prettytable import PrettyTable

parser = argparse.ArgumentParser(
    description="Exports all services from a layer 7 gateway into the git structure"
)
parser.add_argument("-z", "--argFile", required=True, help="The properties file for reading args.")
parser.add_argument("-p", "--plaintextEncryptionPassphrase", required=True,  help="Plaintext passphrase for encryption. Use the prefix '@file:' to read passphrase from a file.")
parser.add_argument("-o", "--output", required=True, help="Directory of the provider to export to")
args = parser.parse_args()



gmu_services_cmd = "gmu list --argFile " +  args.argFile + " --type SERVICE --hideProgress"
gmu_services = os.popen(gmu_services_cmd).read()

# List services
version_regexp = re.compile("v[0-9]")
for line in gmu_services.splitlines():
    fields = line.split("\t")
    if len(fields) == 2:
        service_id = fields[0]
        service_name = fields[1]
        if version_regexp.search(service_name):
            # Sanitize service names, converting / into _ and removing *
            # Ideally should be a naming convention which should dissallow this
            service_name = service_name.replace("/", "_")
            service_name = service_name.replace("*", "")

            service_version = version_regexp.findall(service_name)[0]
            print(str(service_name) + "\t" + str(service_version))

            # Create directories
            pathlib.Path(args.output + "/conf/" + service_name + "_" + service_version).mkdir(parents=True, exist_ok=True)
            pathlib.Path(args.output + "/doc/" + service_name + "_" + service_version).mkdir(parents=True, exist_ok=True)
            pathlib.Path(args.output + "/src/" + service_name + "_" + service_version).mkdir(parents=True, exist_ok=True)

            # Run the export
            gmu_migrateOut_cmd = "gmu migrateOut --argFile " + args.argFile + " --service " + service_id + " --plaintextEncryptionPassphrase " + args.plaintextEncryptionPassphrase + " --dest " + args.output + "/src/" + service_name + "_" + service_version + "/" + service_name + ".xml"

            gmu_migrateOut = subprocess.Popen(gmu_migrateOut_cmd, stdout=subprocess.PIPE, shell=True)
            (output, err) = gmu_migrateOut.communicate()
            gmu_migrateOut_status = gmu_migrateOut.wait()

            # Template the service
            gmu_template_cmd = "gmu template --bundle " + args.output + "/src/" + service_name + "_" + service_version + "/" + service_name + ".xml" + " --template " + args.output + "/conf/" + service_name + "_" + service_version + "/" + service_name + ".properties"

            gmu_template = subprocess.Popen(gmu_template_cmd, stdout=subprocess.PIPE, shell=True)
            (output, err) = gmu_template.communicate()
            gmu_template_status = gmu_template.wait()

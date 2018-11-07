#!/usr/bin/python3

import os
import re
import argparse
import pathlib
import subprocess
import traceback

parser = argparse.ArgumentParser(
    description="Exports services from a layer 7 gateway into the git structure")
parser.add_argument("-z", "--argFile", required=True,
                    help="The properties file for connecting to the local gateway")
parsergroup = parser.add_mutually_exclusive_group(required=True)
parsergroup.add_argument(
    "--all", help="Exports all services", action='store_true')
parsergroup.add_argument(
    "-i", "--serviceid", help="ID of specific service to be exported")
parser.add_argument_group(parsergroup)
parser.add_argument("-p", "--plaintextEncryptionPassphrase", required=False,
                    help="Plaintext passphrase for encryption. Use the prefix '@file:' to read passphrase from a file")
parser.add_argument("-o", "--output", required=True,
                    help="Local path to git repo of provider. The script output export will be placed here")
parser.add_argument("-g", "--gateway", required=True,
                    help="Name of the target gateway")
parser.add_argument("-a", "--action", required=False,
                    help="Mapping action: [New, Update, Existing, ForceNew,Delete, Ignore, NewOrExisting, NewOrUpdate,DeleteOrIgnore]")
args = parser.parse_args()

gmu_all = os.popen("gmu browse --argFile " + args.argFile +
                       " --recursive --showIds --hideProgress").read()

gmu_services = list()

if args.serviceid:
    searchstring = args.serviceid.strip()
else:
    searchstring = "^service"

for line in gmu_all.splitlines():
    if re.search(searchstring, line):
        gmu_services.append(line)

services = list()

for line in gmu_services:
    fields = line.split("\t")
    if fields[2] != "Gateway REST Management Service":
        gw_object = {"type": fields[0].strip(
        ), "id": fields[1].strip(), "object": fields[2].strip()}
        print(str(gw_object))
        services.append(gw_object)

try:
    # Export services, assuming the service names have no / or * in them
    for item in services:
        # The name of the service is the string following the last / character
        servicename = item.get(
            "object")[item.get("object").rindex("/") + 1:]
        servicepath = item.get("object")[:item.get("object").rindex("/")]

        # Determine the directories structure for the export
        conf_dir = args.output + "/" + servicename + "/" + args.gateway + "/conf/"
        test_dir = args.output + "/" + servicename + "/" + args.gateway + "/test"
        src_dir = args.output + "/" + servicename + "/" + args.gateway + "/src/"
        docs_dir = args.output + "/" + servicename + "/docs/"
        # Create the above directories
        pathlib.Path(conf_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(test_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(src_dir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(docs_dir).mkdir(parents=True, exist_ok=True)

        # Run the export
        if args.plaintextEncryptionPassphrase:
            gmu_migrateOut = subprocess.Popen("gmu migrateOut --argFile " + args.argFile + " --service " + item.get("id") + " --plaintextEncryptionPassphrase " +
                                              args.plaintextEncryptionPassphrase + " --dest " + "\"" + src_dir + "\"" + "/" + "\"" + servicename + "\"" + ".xml", stdout=subprocess.PIPE, shell=True)
        else:
            gmu_migrateOut = subprocess.Popen("gmu migrateOut --argFile " + args.argFile + " --service " + item.get(
                "id") + " --dest " + "\"" + src_dir + "\"" + "/" + "\"" + servicename + "\"" + ".xml", stdout=subprocess.PIPE, shell=True)
        (output, err) = gmu_migrateOut.communicate()
        gmu_migrateOut_status = gmu_migrateOut.wait()

        # Create a mapping file if action parameter is specified
        if args.action:
            gmu_mapping = subprocess.Popen("gmu manageMappings --type SERVICE" + " --action " + args.action + " --bundle " + "\"" + src_dir + servicename +
                                           ".xml" + "\"" + " --outputFile " + "\"" + src_dir + servicename + "-mapping.xml" + "\"", stdout=subprocess.PIPE, shell=True)
            (output, err) = gmu_mapping.communicate()
            gmu_mapping_status = gmu_mapping.wait()

        # Template the service
        gmu_template = subprocess.Popen("gmu template --bundle " + "\"" + src_dir + "\"" + "/" + "\"" + servicename + "\"" + ".xml" +
                                        " --template " + "\"" + conf_dir + "\"" + "/" + "\"" + servicename + "\"" + ".properties", stdout=subprocess.PIPE, shell=True)
        (output, err) = gmu_template.communicate()
        gmu_template_status = gmu_template.wait()

        # Add folder property
        service_properties = open(
            conf_dir + "/" + servicename + ".properties", "a")
        service_properties.write("service.folderpath=/" + servicepath)
        service_properties.close()

        print(servicename + " - " + servicepath)


except Exception as e:
    print("Error processing: " + item.get("object"))
    traceback.print_exc()
    pass

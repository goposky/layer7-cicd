#!/usr/bin/python3

import os
import argparse
import pathlib
import subprocess
import traceback

parser = argparse.ArgumentParser(description="Exports all services from a layer 7 gateway into the git structure")
parser.add_argument("-z", "--argFile", required=True, help="The properties file for reading args.")
parser.add_argument("-p", "--plaintextEncryptionPassphrase", required=False,  help="Plaintext passphrase for encryption. Use the prefix '@file:' to read passphrase from a file.")
parser.add_argument("-o", "--output", required=True, help="Directory of the provider to export to")
parser.add_argument("-g", "--gateway", required=True, help="Name of the gateway")
parser.add_argument("-a", "--action", required=False, help="Mapping action: [New, Update, Existing, ForceNew,Delete, Ignore, NewOrExisting, NewOrUpdate,DeleteOrIgnore]")
args = parser.parse_args()

gmu_services = os.popen("gmu browse --argFile " + args.argFile + " --recursive --showIds --hideProgress").read()
services = list()

for line in gmu_services.splitlines():
    fields = line.split("\t")
    if len(fields) == 3 and fields[2] != "Gateway REST Management Service":
        gw_object = {"type": fields[0].strip(), "id": fields[1].strip(), "object": fields[2].strip()}
        services.append(gw_object)

try:
    # Export services, assuming the service names have no / or * in them
    for item in services:
        if item.get("type") == "service":
                # The name of the service is the string following the last / character
                service_name = item.get("object")[item.get("object").rindex("/") + 1:]
                service_path = item.get("object")[:item.get("object").rindex("/")]

                # Create the directories to export to
                conf_dir = args.output + "/" + service_name + "/" + args.gateway + "/conf/"
                test_dir = args.output + "/" + service_name + "/" + args.gateway + "/test"
                src_dir = args.output + "/" + service_name + "/" + args.gateway + "/src/"
                docs_dir = args.output + "/" + service_name + "/docs/"

                pathlib.Path(conf_dir).mkdir(parents=True, exist_ok=True)
                pathlib.Path(test_dir).mkdir(parents=True, exist_ok=True)
                pathlib.Path(src_dir).mkdir(parents=True, exist_ok=True)
                pathlib.Path(docs_dir).mkdir(parents=True, exist_ok=True)

                # Run the export
                if args.plaintextEncryptionPassphrase:
                    gmu_migrateOut = subprocess.Popen("gmu migrateOut --argFile " + args.argFile + " --service " + item.get("id") + " --plaintextEncryptionPassphrase " + args.plaintextEncryptionPassphrase + " --dest " + "\"" + src_dir + "\"" + "/" + "\"" + service_name + "\"" + ".xml", stdout=subprocess.PIPE, shell=True)
                else:
                    gmu_migrateOut = subprocess.Popen("gmu migrateOut --argFile " + args.argFile + " --service " + item.get("id") + " --dest " + "\"" + src_dir + "\"" + "/" + "\"" + service_name + "\"" + ".xml", stdout=subprocess.PIPE, shell=True)
                (output, err) = gmu_migrateOut.communicate()
                gmu_migrateOut_status = gmu_migrateOut.wait()

                # Create a mapping file if action parameter is specified
                if args.action:
                    gmu_mapping = subprocess.Popen("gmu manageMappings --type SERVICE" + " --action " + args.action +  " --bundle " + "\"" + src_dir + service_name + ".xml" + "\"" + " --outputFile " + "\"" + src_dir + service_name + "-mapping.xml" + "\"", stdout=subprocess.PIPE, shell=True)
                    (output, err) = gmu_mapping.communicate()
                    gmu_mapping_status = gmu_mapping.wait()


                # Template the service
                gmu_template = subprocess.Popen("gmu template --bundle " + "\"" + src_dir + "\"" + "/" + "\"" + service_name + "\"" + ".xml" + " --template " + "\"" + conf_dir + "\"" + "/" + "\"" + service_name + "\"" + ".properties", stdout=subprocess.PIPE, shell=True)
                (output, err) = gmu_template.communicate()
                gmu_template_status = gmu_template.wait()
                
                # Add folder property
                service_properties = open(conf_dir + "/" + service_name + ".properties", "a")
                service_properties.write("service.folderpath=/" + service_path)
                service_properties.close()

                print(service_name + " - " + service_path)


except Exception as e:
    print("Error processing: " + item.get("object"))
    traceback.print_exc()
    pass

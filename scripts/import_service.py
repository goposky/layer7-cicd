#!/usr/bin/python3

import os
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Import a service from the checked out git project into the gateway")
parser.add_argument("-z", "--argFile", required=True, help="The properties file for reading args.")
parser.add_argument("-p", "--plaintextEncryptionPassphrase", required=True, help="Plaintext passphrase for encryption. Use the prefix '@file:' to read passphrase from a file.")
parser.add_argument("-r", "--results", required=True, help="Results file of migration operations.")
parser.add_argument("-b", "--bundle", required=True, help="Bundle to import")
args = parser.parse_args()


# Read the folderpath from the properties file
base_folder = args.bundle[:args.bundle.rindex("/src")]
file_name = os.path.basename(args.bundle)[:os.path.basename(args.bundle).rindex(".")]

service_folderpath = None

with open(base_folder + "/conf/" + file_name + ".properties") as fp:
    for cnt, line in enumerate(fp):
        if "service.folderpath" in line:
            service_folderpath = line

service_folderpath = service_folderpath[service_folderpath.rindex("=") + 1:]

gmu_migrateIn_cmd = "gmu migrateIn --argFile " + args.argFile + " --results " + args.results + " --bundle " + args.bundle + " --destFolder " + service_folderpath + " --map " + base_folder + \
    "/src/" + file_name + "-mapping.xml" + " --template " + base_folder + "/conf/" + file_name + ".properties" + " --plaintextEncryptionPassphrase " + args.plaintextEncryptionPassphrase

gmu_migrateIn = subprocess.Popen(gmu_migrateIn_cmd, stdout=subprocess.PIPE, shell=True)
(output, err) = gmu_migrateIn.communicate()
gmu_migrateIn_status = gmu_migrateIn.wait()

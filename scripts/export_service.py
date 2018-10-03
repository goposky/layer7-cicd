#!/usr/bin/python3

import os
import argparse
import pathlib
import subprocess

from prettytable import PrettyTable

parser = argparse.ArgumentParser(
            description = "Script to list and export layer 7 services...because why not"
        )
parser.add_argument("-b", "--browse", help="browse, defaults to all, otherwise specify either folder, service or policy")
parser.add_argument("-a", "--arg", help="gateway argument file")
parser.add_argument("-i", "--id", help="id to export")
parser.add_argument("-o", "--output", help="output path to export to, this should be directory path until the name of the gateway")
parser.add_argument("-n", "--name", help="service file name to save as, .xml will be appended to the file so don't include this")

args = parser.parse_args()

if args.browse:
    gmu_browse_cmd = "gmu browse --recursive --showIds --hideProgress " + "--argFile " + args.arg
    gmu_browse = os.popen(gmu_browse_cmd).read()

    table = PrettyTable()
    table.field_names = ["TYPE", "ID", "PATH"]
    table.align["TYPE"] = "l"
    table.align["ID"] = "l"
    table.align["PATH"] = "l"

    # List services
    for line in gmu_browse.splitlines():
        fields = line.split("\t")
        if len(fields) == 3:
            if fields[0].strip() == args.browse:
                table.add_row([fields[0].strip(),fields[1].strip(),fields[2].strip()])
            elif args.browse == "all":
                table.add_row([fields[0].strip(),fields[1].strip(),fields[2].strip()])

    # Export a given service
    print(table)

elif args.browse is None:
    # Create directory if it doesn't exist
    pathlib.Path(args.output+ "/conf").mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.output+ "/doc").mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.output+ "/src").mkdir(parents=True, exist_ok=True)

    gmu_migrateOut_cmd = "gmu migrateOut --argFile " + args.arg +" --service " + args.id + " --plaintextEncryptionPassphrase @file:/home/amresh/Projects/ziggo/encryptm.txt --dest " + args.output + "/src/" + args.name + ".xml"

    # Run the export
    gmu_migrateOut = subprocess.Popen(gmu_migrateOut_cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = gmu_migrateOut.communicate()
    gmu_migrateOut_status = gmu_migrateOut.wait()

    # Template the service
    gmu_template_cmd = "gmu template --bundle " + args.output + "/src/" + args.name + ".xml" + " --template " + args.output + "/conf/" + args.name + ".properties"
    gmu_template = subprocess.Popen(gmu_template_cmd, stdout=subprocess.PIPE, shell=True)
    gmu_template_status = gmu_template.wait()

#!/usr/bin/python3

import xml.etree.ElementTree as ET
import requests
import os
import pathlib
import subprocess
import argparse
from tqdm import tqdm
requests.packages.urllib3.disable_warnings()


class Gateway:
    def __init__(self, gateway, argFile, username, password, restmanUrl, namespaces):
        self.gateway = gateway
        self.argFile = argFile
        self.username = username
        self.password = password
        self.restmanUrl = restmanUrl
        self.namespaces = namespaces

    # Create directory structure
    def createDirs(self, outputDir, bundleName):
        confDir = outputDir + "/" + bundleName + "/" + self.gateway + "/conf/"
        testDir = outputDir + "/" + bundleName + "/" + self.gateway + "/test/"
        srcDir = outputDir + "/" + bundleName + "/" + self.gateway + "/src/"
        docsDir = outputDir + "/" + bundleName + "/" + "/docs/"

        pathlib.Path(confDir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(testDir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(srcDir).mkdir(parents=True, exist_ok=True)
        pathlib.Path(docsDir).mkdir(parents=True, exist_ok=True)

        return {"conf": confDir, "test": testDir, "src": srcDir, "doc": docsDir}

    # FIXME: convert this method to use restman api
    # Makes a list of the gmu browse command output
    def browse(self):
        gmuBrowse = os.popen("gmu browse --argFile " + self.argFile + " --recursive --showIds --hideProgress").read()
        listing = list()

        for line in gmuBrowse.splitlines():
            fields = line.split("\t")
            if len(fields) == 3 and fields[2] != "Gateway REST Management Service":
                item = {"type": fields[0].strip(), "id": fields[1].strip(), "path": fields[2].strip()}
                listing.append(item)
        return listing

    # Gets the bundle
    def getBundle(self, resourceType, id):
        endpoint = self.restmanUrl + "/1.0/bundle"
        parameters = {resourceType: id, "includeDependencies": "true"}
        bundle = requests.get(url=endpoint, auth=(self.username, self.password), params=parameters, verify=False)
        return bundle.text

    # Get the buildingblock policies
    def getBuildingBlocks(self, bundle):
        tree = ET.parse(bundle)
        root = tree.getroot()

        policyDetail = root.findall("l7:References/l7:Item/l7:Resource/l7:Policy/l7:PolicyDetail", self.namespaces)
        policies = {}
        for detail in policyDetail:
            folderId = detail.attrib.get("folderId")
            policyId = detail.attrib.get("id")
            name = detail.find("l7:Name", self.namespaces).text

            details = [name, folderId]
            policies[policyId] = details

        return policies

    # Adds mapping for building block policies for a given folder. This will create any folders if they are non existant
    def extendMapping(self, buildingBlockPolicies, bundle):
        tree = ET.parse(bundle)
        root = tree.getroot()
        bundle = ET.ElementTree()

        mappings = root.findall("l7:Mappings/l7:Mapping", self.namespaces)

        for mapping in mappings:
            for prefix, url in self.namespaces.items():
                ET.register_namespace(prefix, url)
            srcId = mapping.get("srcId")
            if(srcId in buildingBlockPolicies):
                properties = ET.Element("l7:Properties")
                propertiesMapBy = ET.SubElement(properties, "l7:Property")
                stringValueMapBy = ET.SubElement(propertiesMapBy, "l7:StringValue")
                propertiesMapBy.set("key", "MapBy")
                stringValueMapBy.text = "path"

                propertiesMapTo = ET.SubElement(properties, "l7:Property")
                stringValueMapTo = ET.SubElement(propertiesMapTo, "l7:StringValue")
                propertiesMapTo.set("key", "MapTo")
                stringValueMapTo.text = "/buildingBlocks/" + buildingBlockPolicies[srcId][0]
                mapping.insert(0, properties)

        bundle._setroot(root)
        return bundle

    # Exports all the bundles for the given type, or bundle for the given ids
    # FIXME: pretty print xml when writing out
    def exportBundle(self, exportList, outputDir, exportType="service", bundleId=None):
        # When no bundle id is provided, we export all
        if bundleId is None:
            progressbar = tqdm(list(filter(lambda bundle: bundle.get("type") == exportType, exportList)))
            for item in progressbar:
                progressbar.set_description(" exporting: " + item.get("path"))
                # The name of the export type is the string following the last / character
                name = item.get("path")[item.get("path").rindex("/") + 1:]
                path = item.get("path")[:item.get("path").rindex("/")]

                # Create the directories to export to
                dirs = self.createDirs(outputDir=outputDir, bundleName=name)

                # Get the bundle by calling the rest api
                bundle = self.getBundle(exportType, item.get("id"))

                tree = ET.fromstring(bundle)
                bundleXml = ET.ElementTree()
                for prefix, url in self.namespaces.items():
                    ET.register_namespace(prefix, url)

                root = tree.find("l7:Resource/l7:Bundle", self.namespaces)
                bundleXml._setroot(root)
                bundleXml.write(dirs.get("src") + name + ".xml", encoding="utf-8", xml_declaration=True)

                # Create a mapping file with default action set to NewOrExisting
                os.popen("gmu manageMappings --type " + exportType.upper() + " --action NewOrExisting --bundle " "\"" +
                         dirs.get("src") + name + ".xml" + "\"" + " --outputFile " + "\"" + dirs.get("src") + name + "-mapping.xml" + "\"")

                # Adjust mapping file for building block policies to map by name and path to building blocks folder
                mappingAdjustedBundle = self.extendMapping(buildingBlockPolicies=self.getBuildingBlocks(dirs.get("src") + name + ".xml"), bundle=dirs.get("src") + name + ".xml")
                mappingAdjustedBundle.write(dirs.get("src") + name + ".xml", encoding="utf-8", xml_declaration=True)

                # Template the service
                template = subprocess.Popen("gmu template --bundle " + "\"" + dirs.get("src") + "\"" + "/" + "\"" + name + "\"" + ".xml" + " --template " +
                                            "\"" + dirs.get("conf") + "\"" + "/" + "\"" + name + "\"" + ".properties", stdout=subprocess.PIPE, shell=True)
                (output, err) = template.communicate()
                template.wait()

                # Add folder path property
                properties = open(dirs.get("conf") + name + ".properties", "a")
                properties.write("service.folderpath=/" + path)
                properties.close()
        # Export the bundle for the given id
        elif bundleId is not None:
            progressbar = tqdm(list(filter(lambda bundle: bundle.get("type") == exportType and bundle.get("id") == bundleId, exportList)))
            for item in progressbar:
                progressbar.set_description(" exporting: " + item.get("path"))
                if item.get("id") == bundleId and item.get("type") == exportType:
                    # The name of the export type is the string following the last / character
                    name = item.get("path")[item.get("path").rindex("/") + 1:]
                    path = item.get("path")[:item.get("path").rindex("/")]

                    # Create the directories to export to
                    dirs = self.createDirs(outputDir=outputDir, bundleName=name)

                    # Get the bundle by calling the rest api
                    bundle = self.getBundle(exportType, item.get("id"))

                    tree = ET.fromstring(bundle)
                    bundleXml = ET.ElementTree()
                    for prefix, url in self.namespaces.items():
                        ET.register_namespace(prefix, url)

                    root = tree.find("l7:Resource/l7:Bundle", self.namespaces)
                    bundleXml._setroot(root)
                    bundleXml.write(dirs.get("src") + name + ".xml", encoding="utf-8", xml_declaration=True)

                    # Create a mapping file with default action set to NewOrExisting
                    os.popen("gmu manageMappings --type " + exportType.upper() + " --action NewOrExisting --bundle " "\"" +
                             dirs.get("src") + name + ".xml" + "\"" + " --outputFile " + "\"" + dirs.get("src") + name + "-mapping.xml" + "\"")

                    # Adjust mapping file for building block policies to map by name and path to building blocks folder
                    mappingAdjustedBundle = self.extendMapping(buildingBlockPolicies=self.getBuildingBlocks(dirs.get("src") + name + ".xml"), bundle=dirs.get("src") + name + ".xml")
                    mappingAdjustedBundle.write(dirs.get("src") + name + ".xml", encoding="utf-8", xml_declaration=True)

                    # Template the service
                    template = subprocess.Popen("gmu template --bundle " + "\"" + dirs.get("src") + "\"" + "/" + "\"" + name + "\"" + ".xml" + " --template " +
                                                "\"" + dirs.get("conf") + "\"" + "/" + "\"" + name + "\"" + ".properties", stdout=subprocess.PIPE, shell=True)
                    (output, err) = template.communicate()
                    template.wait()

                    # Add folder path property
                    properties = open(dirs.get("conf") + name + ".properties", "a")
                    properties.write("service.folderpath=/" + path)
                    properties.close()

    # Import a bundle
    def importBundle(self, outputDir, bundleName, results=None):
        confDir = outputDir + "/" + bundleName + "/" + self.gateway + "/conf/"
        srcDir = outputDir + "/" + bundleName + "/" + self.gateway + "/src/"

        if results is None:
            results = bundleName + "-results.xml"

        # Read the folderpath from the properties file
        folderPath = None
        with open(confDir + bundleName + ".properties") as fp:
            for line in fp:
                if "service.folderpath" in line:
                    folderPath = line[line.rindex("=") + 1:]
        gmuImport = subprocess.Popen("gmu migrateIn --argFile " + self.argFile + " --results " + results + " --bundle " + "\"" + srcDir + "/" + bundleName + ".xml" + "\"" + " --destFolder " +
                                     folderPath + " --map " + "\"" + srcDir + bundleName + "-mapping.xml" + "\"" + " --template " + "\"" + confDir + bundleName + ".properties" + "\"", stdout=subprocess.PIPE, shell=True)
        (output, err) = gmuImport.communicate()
        gmuImport.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports and imports policies from and to a layer 7 gateway.")
    parser.add_argument("action", choices=["import", "export", "exportAll"])
    parser.add_argument("-z", "--argFile", required=True, help="The properties file for reading args.")
    parser.add_argument("-d", "--dest", required=True, help="Directory of the provider from which to import or export to.")
    parser.add_argument("-g", "--gateway", required=True, help="Name of the gateway.")
    parser.add_argument("-u", "--username", required=True, help="Username for connecting to the gateway.")
    parser.add_argument("-p", "--password", required=True, help="Password for connecting to the gateway.")
    parser.add_argument("-w", "--restman", required=True, help="Path to REST Management interface.")
    parser.add_argument("-i", "--id", required=False, help="Id of the bundle to export.")
    parser.add_argument("-r", "--results", required=False, default=None, help="Results file of migration operations, if not supplied, the default location will be used from which this script is being run.")
    parser.add_argument("-n", "--name", required=False, help="Name of the bundle to import, without the file extension")
    args = parser.parse_args()

    namespaces = {"l7": "http://ns.l7tech.com/2010/04/gateway-management"}
    gateway = Gateway(argFile=args.argFile, username=args.username, password=args.password, namespaces=namespaces, gateway=args.gateway, restmanUrl=args.restman)

    if args.action == "exportAll":
        gateway.exportBundle(exportList=gateway.browse(), outputDir=args.dest)
    elif args.action == "export":
        gateway.exportBundle(exportList=gateway.browse(), outputDir=args.dest, bundleId=args.id)
    elif args.action == "import":
        gateway.importBundle(outputDir=args.dest, bundleName=args.name, results=args.results)

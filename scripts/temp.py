#!/usr/bin/python3

import xml.etree.ElementTree as ET
import requests
import os
import pathlib
import subprocess


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
        parameters = {resourceType: id}
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
            for item in exportList:
                if item.get("type") == exportType and bundleId is None:
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
            for item in exportList:
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
    def importBundle(self, outputDir, bundleName, results):
        confDir = outputDir + "/" + bundleName + "/" + self.gateway + "/conf/"
        srcDir = outputDir + "/" + bundleName + "/" + self.gateway + "/src/"

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
    argfile = "/home/amresh/Projects/ziggo/layer7/gitlab.com/layer7-cicd/workspace/dev-argFile.properties"
    restmanurl = "https://gateway-dev:8443/restman"
    username = "admin"
    password = "password"
    namespaces = {"l7": "http://ns.l7tech.com/2010/04/gateway-management"}
    gateway = "NL_BSS"
    gw = Gateway(argFile=argfile, username=username, password=password, restmanUrl=restmanurl, namespaces=namespaces, gateway=gateway)

    # gw.exportAll(exportList=gw.browse(), outputDir="/home/amresh/Projects/ziggo/layer7/gitlab.com/bsl")

    # gw.exportBundle(bundleId="3911f4f9e80f49fc93d6ff92e534dd16", exportList=gw.browse(), outputDir="/home/amresh/Projects/ziggo/layer7/gitlab.com/bsl")

    gwTst = Gateway(argFile="/home/amresh/Projects/ziggo/layer7/gitlab.com/layer7-cicd/workspace/tst-argFile.properties", restmanUrl="https://gateway-tst:8443/restman",
                    username="admin", password="password", namespaces={"l7": "http://ns.l7tech.com/2010/04/gateway-management"}, gateway="NL_BSS")

    gwTst.importBundle(outputDir="/home/amresh/Projects/ziggo/layer7/gitlab.com/bsl", bundleName="Peal Adress", results="res.xml")


# # Get the folder id
# def getFolderId(username, password, restmanUrl, folderName):
#     foldersEndpoint = restmanUrl + "/1.0/folders?name=" + folderName
#     folder = requests.get(url=foldersEndpoint, auth=(username, password), verify=False)
#     return folder.text


# def exportAll(listing, exportType, outputDir, gateway, username, password, restmanUrl, namespaces):
#     for item in listing:
#         if item.get("type") == exportType:
#             # The name of the export type is the string following the last / character
#             name = item.get("path")[item.get("path").rindex("/") + 1:]
#             path = item.get("path")[:item.get("path").rindex("/")]

#             # Create the directories to export to
#             confDir = outputDir + "/" + name + "/" + gateway + "/conf/"
#             testDir = outputDir + "/" + name + "/" + gateway + "/test/"
#             srcDir = outputDir + "/" + name + "/" + gateway + "/src/"
#             docsDir = outputDir + "/" + name + "/" + "/docs/"

#             pathlib.Path(confDir).mkdir(parents=True, exist_ok=True)
#             pathlib.Path(testDir).mkdir(parents=True, exist_ok=True)
#             pathlib.Path(srcDir).mkdir(parents=True, exist_ok=True)
#             pathlib.Path(docsDir).mkdir(parents=True, exist_ok=True)

#             # Get the bundle by calling the rest api
#             endpoint = restmanUrl + "/1.0/bundle"
#             parameters = {item.get("type"): item.get("id")}
#             bundle = requests.get(url=endpoint, auth=(username, password), params=parameters, verify=False)

#             tree = ET.fromstring(bundle.text)
#             bundleXml = ET.ElementTree()
#             for prefix, url in namespaces.items():
#                 ET.register_namespace(prefix, url)

#             root = tree.find("l7:Resource/l7:Bundle", namespaces)
#             bundleXml._setroot(root)
#             bundleXml.write(srcDir + name + ".xml", encoding="utf-8", xml_declaration=True)

#             # Create a mapping file with default action set to NewOrExisting
#             os.popen("gmu manageMappings --type " + exportType.upper() + " --action NewOrExisting --bundle " "\"" +
#                      srcDir + name + ".xml" + "\"" + " --outputFile " + "\"" + srcDir + name + "-mapping.xml" + "\"")

#             # Add mapping to map to building blocks folder
#             # buildingBlocks = getBuildingBlocks(bundleXml,namespaces,)


# folderid=getFolderId("admin","password","https://gateway-tst:8443/restman","buildingBlocks")
# print(folderid)
# # e = exportAll(browse("../workspace/tst-argFile.properties"), "service", "/home/amresh/Projects/ziggo/layer7/gitlab.com/bsl", "NL_BSS",
# #               "admin", "password", "https://gateway-tst:8443/restman", {"l7": "http://ns.l7tech.com/2010/04/gateway-management"})

# # bundle = getBundle("admin","password","https://gateway-tst:8443/restman","service","e73aa375c92bf77a0b52a366672b0306")
# # # tree = ET.parse(bundle)
# # root=ET.fromstring(bundle)

# # ns = {"l7":"http://ns.l7tech.com/2010/04/gateway-management"}
# # root = root.find("l7:Resource/l7:Bundle",ns)

# # bundle=ET.ElementTree()
# # ET.register_namespace("l7", "http://ns.l7tech.com/2010/04/gateway-management")
# # bundle._setroot(root)
# # bundle.write("out.xml",encoding="utf-8",xml_declaration=True)

# # browse = browse("../workspace/tst-argFile.properties")
# # for it in browse:
# #     print(it)

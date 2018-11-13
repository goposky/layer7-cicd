#!/usr/bin/python3


import xml.etree.ElementTree as ET
import requests


# Get the buildingblock policies based on their folder id
def getBuildingBlocks(xmlContents, namespaces, folderId):
    tree = ET.parse(xmlContents)
    root = tree.getroot()

    policyDetail = root.findall("l7:References/l7:Item/l7:Resource/l7:Policy/l7:PolicyDetail", namespaces)
    policies = {}
    for idx, detail in enumerate(policyDetail):
        folderId = detail.attrib.get("folderId")
        policyId = detail.attrib.get("id")
        name = detail.find("l7:Name", namespaces).text

        details = [name, folderId]
        policies[policyId] = details

    return policies


# Get the folder id
def getFolderId(username, password, restmanUrl, folderName):
    foldersEndpoint = restmanUrl + "/1.0/folders?name=" + folderName
    folder = requests.get(url=foldersEndpoint, auth=(username, password), verify=False)
    return folder.text


# Gets the bundle
def getBundle(username, password, restmanUrl, resourceType, id):
    endpoint = restmanUrl + "/1.0/bundle"
    parameters = {resourceType: id}
    bundle = requests.get(url=endpoint, auth=(username, password), params=parameters, verify=False)
    return bundle.text


# Adds mapping for building block policies for a given folder. This will create any folders if they are non existant
def extendMapping(buildingBlockPolicies, xmlContents, namespaces):
    tree = ET.parse(xmlContents)
    root = tree.getroot()
    bundle = ET.ElementTree()

    mappings = root.findall("l7:Mappings/l7:Mapping", namespaces)

    for mapping in mappings:
        for prefix, url in namespaces.items():
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


# def getServices(username, password, restmanUrl):


namespaces = {"l7": "http://ns.l7tech.com/2010/04/gateway-management"}
folders = ET.parse("dep.xml")
root = folders.getroot()

refdict = {}
references = root.findall("l7:Resource/l7:DependencyList/l7:Reference/l7:Dependencies/l7:Dependency", namespaces)
for reference in references:
    rId = reference.find("l7:Id", namespaces).text
    rName = reference.find("l7:Name", namespaces).text
    refdict[rId] = rName

deps = root.findall("l7:Resource/l7:DependencyList/l7:Dependencies/l7:Dependency", namespaces)
nested = root.findall("l7:Resource/l7:DependencyList/l7:Dependencies/l7:Dependency/l7:Dependencies/l7:Dependency", namespaces)

# print(refdict)

# for d in deps:
#     did = d.find("l7:Id", namespaces).text
#     dname = d.find("l7:Name", namespaces).text
#     dtype = d.find("l7:Type", namespaces).text

#     nested = d.findall("l7:Dependencies/l7:Dependency", namespaces)
#     for n in nested:
#         nid = n.find("l7:Id", namespaces).text
#         nname = n.find("l7:Name", namespaces).text
#         ntype = n.find("l7:Type", namespaces).text
#         fpath = ""
#         fullpath = ""
#         if(ntype == "FOLDER"):
#             fpath = dname + "/" + nname
#         elif(ntype == "SERVICE"):
#             fullpath = dname + "/" + nname
#         totalpath = fpath + "/" + fullpath
#         if(len(totalpath) > 1):
#             print(totalpath)

# dependencies = root.findall("l7:Resource/l7:DependencyList/l7:Dependencies/l7:Dependency", namespaces)
# references = root.findall("l7:Resource/l7:DependencyList/l7:Reference/l7:Dependencies/l7:Dependency", namespaces)

# reflist = list()
# for r in references:
#     rname = r.find("l7:Name", namespaces).text
#     rtype = r.find("l7:Type", namespaces).text
#     rid = r.find("l7:Id", namespaces).text
#     ref = {"id": rid, "type": rtype, "name": rname}
#     reflist.append(ref)

# depList = list()

# for d in dependencies:
#     dname = d.find("l7:Name", namespaces).text
#     dtype = d.find("l7:Type", namespaces).text
#     did = d.find("l7:Id", namespaces).text

#     nested = d.findall("l7:Dependencies/l7:Dependency", namespaces)
#     for n in nested:
#         nid = n.find("l7:Id", namespaces).text
#         ntype = n.find("l7:Type", namespaces).text
#         nname = n.find("l7:Name", namespaces).text

#         dep = {"id": did, "type": dtype, "name": dname, "depid": nid, "deptype": ntype, "depname": nname}
#         depList.append(dep)


# services = list()
# for it in depList:
#     # path=""
#     fid=""
#     if(it.get("deptype")=="SERVICE"):
#         path = it.get("name") + "/" + it.get("depname")
#         fid = it.get("id")
#     for x in depList:
#         if(x.get("depid")==fid):
#             path = x.get("name") + "/" + path
#             print(path)

referenceList = list()
references = root.findall("l7:Resource/l7:DependencyList/l7:Reference/l7:Dependencies/l7:Dependency", namespaces)
for ref in references:
    refId = ref.find("l7:Id", namespaces).text
    refType = ref.find("l7:Type", namespaces).text
    refName = ref.find("l7:Name", namespaces).text
    ref = {"id": refId, "type": refType, "name": refName}
    referenceList.append(ref)

dependenciesList = list()
dependencies = root.findall("l7:Resource/l7:DependencyList/l7:Dependencies/l7:Dependency", namespaces)
for dep in dependencies:
    depId = dep.find("l7:Id", namespaces).text
    depType = dep.find("l7:Type", namespaces).text
    depName = dep.find("l7:Name", namespaces).text

    nestedDependencies = dep.findall("l7:Dependencies/l7:Dependency", namespaces)
    for ndep in nestedDependencies:
        ndepId = ndep.find("l7:Id", namespaces).text
        ndepType = ndep.find("l7:Type", namespaces).text
        ndepName = ndep.find("l7:Name", namespaces).text
        dep = {"depId": depId, "depType": depType, "depName": depName, "nestedId": ndepId, "nestedType": ndepType, "nestedName": ndepName}
        dependenciesList.append(dep)

for dItem in dependenciesList:
    for nItem in dependenciesList:
        if(dItem.get("nestedId") == nItem.get("depId")):
            path = dItem.get("depName") + "/" + nItem.get("depName")
            print(path)

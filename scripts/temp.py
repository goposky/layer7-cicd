#!/usr/bin/python3


import xml.etree.ElementTree as ET
import requests


def getBuildingBlocks(xmlContents, namespaces, folderId):
    tree = ET.parse(xmlContents)
    root = tree.getroot()

    policyDetail = root.findall("l7:References/l7:Item/l7:Resource/l7:Policy/l7:PolicyDetail", namespaces)
    policies = {}
    for idx, detail in enumerate(policyDetail):
        folderId = detail.attrib.get("folderId")
        policyId = detail.attrib.get("id")
        name = detail.find("l7:Name", namespaces).text

        # details = [name, policyId, folderId]
        details = [name, folderId]
        policies[policyId] = details

    return policies


def getFolderId(username, password, restmanUrl, folderName):
    foldersEndpoint = restmanUrl + "/1.0/folders?name=" + folderName
    folder = requests.get(url=foldersEndpoint, auth=(
        username, password), verify=False)
    return folder.text


def getBundle(username, password, restmanUrl, resourceType, id):
    endpoint = restmanUrl + "/1.0/bundle"
    parameters = {resourceType: id}
    bundle = requests.get(url=endpoint, auth=(
        username, password), params=parameters, verify=False)
    return bundle.text


bb = getBuildingBlocks(xmlContents="input/consent.xml",namespaces={"l7": "http://ns.l7tech.com/2010/04/gateway-management"},folderId="985b4aeeb083ede7d9330256c83b987c")
# for val in bb.items():
#     print(val)

consent = ET.parse("input/consent.xml",parser=None)

root = consent.getroot()
namespaces = {"l7": "http://ns.l7tech.com/2010/04/gateway-management"}
mappings = root.findall("l7:Mappings/l7:Mapping",namespaces)

for m in mappings:
    ET.register_namespace("l7","http://ns.l7tech.com/2010/04/gateway-management")
    action = m.get("action")
    srcId = m.get("srcId")
    if(srcId in bb):
    # if(srcId=="a5af7a23ab001c063ef535db8188ad65"):
        properties=ET.Element("l7:Properties")

        propertiesMapBy=ET.SubElement(properties,"l7:Property")
        stringValueMapBy=ET.SubElement(propertiesMapBy,"l7:StringValue")
        propertiesMapBy.set("key","MapBy")
        stringValueMapBy.text="path"

        propertiesMapTo=ET.SubElement(properties,"l7:Property")
        stringValueMapTo=ET.SubElement(propertiesMapTo,"l7:StringValue")
        propertiesMapTo.set("key","MapTo")
        stringValueMapTo.text="/buildingBlocks/" + bb[srcId][0]
        m.insert(0,properties)
# ET.dump(root)

out = ET.ElementTree()
out._setroot(root)
out.write("out.xml",encoding="UTF-8",short_empty_elements=False)

# properties = ET.Element("l7:Properties")
# prop = ET.SubElement(properties,"l7:Property")
# stringvalue = ET.SubElement(prop,"l7:StringValue")
# prop.set("key","MapBy")
# stringvalue.text="path"

# propMapTo=ET.SubElement(properties,"l7:Property")
# stringvalueMapTo=ET.SubElement(propMapTo,"l7:StringValue")
# propMapTo.set("key","MapTo")
# stringvalueMapTo.text="/buildingBlocks"

# ET.dump(properties)

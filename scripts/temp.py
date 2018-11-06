#!/usr/bin/python3

import collections
import xml.etree.ElementTree as ET


def getBuildingBlocks(xmlContents, namespaces, folderId):
    tree = ET.parse(xmlContents)
    root = tree.getroot()

    policyDetail = root.findall("l7:References/l7:Item/l7:Resource/l7:Policy/l7:PolicyDetail", namespaces)
    policies = {}
    for idx,detail in enumerate(policyDetail):
        folderId = detail.attrib.get("folderId")
        policyId = detail.attrib.get("id")
        name = detail.find("l7:Name", namespaces).text
        
        details = [name, policyId, folderId]
        policies[idx] = details

    return policies

test = getBuildingBlocks(xmlContents = "../NL_BSS/src/Akana_USMS_service_SOAP_v1.xml",namespaces = {"l7": "http://ns.l7tech.com/2010/04/gateway-management"},folderId = "985b4aeeb083ede7d9330256c83b987c")
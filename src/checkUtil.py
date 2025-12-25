from __future__ import (absolute_import, division,print_function)
import maya.cmds as cmds
from .SPLib import editAttrs,editTransform

def checkParam(topNode =None,nodeTypes = [],ignorNodeTypes = [],attrs = []):
    result = []

    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    for nodeType in nodeTypes:
        allNodes = editTransform.listTypeNodes(nodeType,topNode = topNode,fullpath =True,ignorNodeTypes = ignorNodeTypes)

        for node in allNodes:
            for attr in attrs:
                attrName = attr["attrName"]
                checkValues = attr["value"]

                if type(checkValues) != list:
                    checkValues = [checkValues]

                targetAttrs = editAttrs.getFlattenAttr(node,[attrName])
                
                for targetAttr,checkValue in zip(targetAttrs,checkValues):
                    if cmds.objExists(node + "."+targetAttr) ==False:
                        continue
                    
                    value = cmds.getAttr(node + "."+targetAttr)                    

                    if attr["equal"] == "==":
                        if type(value) == float:
                            if round(value,5) == checkValue:
                                if node not in result:
                                    result.append(node)
                                continue

                        else:
                            if value == checkValue:
                                if node not in result:
                                    result.append(node)
                                continue
                    if attr["equal"] == "!=":
                        if type(value) == float:
                            if round(value,5) != checkValue:
                                if node not in result:
                                    result.append(node)
                                continue

                        else:
                            if value != checkValue:
                                if node not in result:
                                    result.append(node)
                                continue
    return result

def checkLockedParam(topNode =None,nodeTypes = ["transform"],ignorNodeTypes = [],attrs = ["t","r","s"]):
    result = []

    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    for nodeType in nodeTypes:
        allNodes = editTransform.listTypeNodes(nodeType,topNode = topNode,fullpath =True,ignorNodeTypes = ignorNodeTypes)

        for node in allNodes:
            for attr in attrs:
                targetAttrs = editAttrs.getFlattenAttr(node,attr)
                
                for targetAttr in targetAttrs:
                    if cmds.objExists(node + "."+targetAttr) ==False:
                        continue

                    if cmds.getAttr(node + "." + targetAttr, l =True):
                        if node not in result:
                            result.append(node)
                        continue                        

    return result

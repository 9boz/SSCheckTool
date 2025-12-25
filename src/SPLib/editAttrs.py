from __future__ import (absolute_import, division,print_function, unicode_literals)

import maya.cmds as cmds
##-----------------------------------------------
##get & set
##-----------------------------------------------
def listAttrs(node,keyable,unkeyable,longName = False):
    attrs = []

    unKeyableAttrs = cmds.listAttr(node,channelBox =True) or []
    keyableAttrs = cmds.listAttr(node,keyable =True) or []
    
    if keyable:

        for attr in keyableAttrs:
            attrName = cmds.attributeQuery(attr, node=node, longName=longName,  shortName = not longName)
            attrs.append(attrName)

    if unkeyable:
        for attr in unKeyableAttrs:
            attrName = cmds.attributeQuery(attr, node=node, longName=longName,  shortName = not longName)
            attrs.append(attrName)

    return attrs
##-----------------------------------------------
##get & set
##-----------------------------------------------
def getFlattenAttr(target,attrs = []):
    targetAttrs = []
    
    for attr in attrs:
        if cmds.attributeQuery(attr,node = target,exists =True) ==False:

            if cmds.objExists(target + "." + attr):
                targetAttrs.append(attr)
            
            continue

        childrenAttrs = cmds.attributeQuery(attr,node = target,listChildren =True)        
        
        if childrenAttrs == None or len(childrenAttrs) == 0:
            targetAttrs.append(attr)

        else:
            targetAttrs.extend(childrenAttrs)

    return targetAttrs

##set
def setAttrState(targets,attrs,lock,hide,keyable):
    for target in targets:
        targetAttrs = getFlattenAttr(target,attrs)

        for attr in targetAttrs:
            if cmds.objExists(target + "." + attr) == False:
                print("cant find " + target + "." + attr)
                continue
            
            #lock
            cmds.setAttr(target + '.'+ attr, lock = lock)

            if hide == True:
                cmds.setAttr(target + '.'+ attr,  channelBox = False, keyable = False)
            else :
                cmds.setAttr(target + '.'+ attr, channelBox = True, keyable = True)
                cmds.setAttr(target + '.'+ attr, keyable = keyable)

def setAttrNodes(nodes,valueDict,force):
    for node in nodes:
        for attr in list(valueDict.keys()):

            locked = cmds.getAttr(node + "." + attr,lock =True)
            
            if locked and force == False:
                continue

            cmds.setAttr(node + "." + attr,lock = False)
            cmds.setAttr(node + "." + attr,valueDict[attr])
            cmds.setAttr(node + "." + attr,lock = locked)

def setAttrType(nodeTypes,valueDict,force):
    for nodeType in nodeTypes:
        nodes = cmds.ls(type = nodeType) or []
        
        setAttrNodes(nodes,valueDict,force)

def setAttrHierarchy(topNodes,nodeType,valueDict,force):
    for topNode in topNodes:
        nodes = cmds.listRelatives(topNode,ad =True,type = nodeType) or []
        setAttrNodes(nodes,valueDict,force)

def resetMultiIndex(node,attr):
    indexes = cmds.getAttr(node +"."+ attr, mi = True) or []
    for i in indexes:
        cmds.removeMultiInstance(node +"."+ attr + "[" + str(i) + "]")

def getTransformLimit(node):
    limitDict = {}

    for attr in ["Trans","Rot","Scale"]:
        for axis in "XYZ":
            if cmds.getAttr(node + ".min"+attr+axis+"LimitEnable"):
                limitDict["min"+attr+axis+"LimitEnable"] = True
                limitDict["min"+attr+axis+"Limit"] = cmds.getAttr(node + ".min"+attr+axis+"Limit")
            
            if cmds.getAttr(node + ".max"+attr+axis+"LimitEnable"):
                limitDict["max"+attr+axis+"LimitEnable"] = True
                limitDict["max"+attr+axis+"Limit"] = cmds.getAttr(node + ".max"+attr+axis+"Limit")

    return limitDict

def setEnumAttr(node,attr,value):        
    enumString = cmds.attributeQuery(attr.split(".")[-1], node = node, listEnum =True)[0]    
    enumList = enumString.split(":")

    if value not in enumList:
        return None
    
    cmds.setAttr(node + "."+attr,enumList.index(value))

def getEnumAttr(node,attr):        
    enumString = cmds.attributeQuery(attr.split(".")[-1], node = node, listEnum =True)[0]    
    enumList = enumString.split(":")
    
    index = cmds.getAttr(node + "."+attr)

    return enumList[index]

##-----------------------------------------------------
##connect
##-----------------------------------------------------
def disconnectInputs(target,attrs):
    attrs = getFlattenAttr(target,attrs)

    for attr in attrs:
        curInput = cmds.listConnections(target + "." + attr, s =True, d =False,p=True)

        if curInput == None:
            continue

        cmds.disconnectAttr(curInput[0], target + "." + attr)
        

def connectAttrZip(source,target,sourceAttrs,targetAttrs,f =True):
    sourceAttrs = getFlattenAttr(source,sourceAttrs)
    targetAttrs = getFlattenAttr(target,targetAttrs)
    
    for sourceAttr,targetAttr in zip(sourceAttrs,targetAttrs):           
        cmds.connectAttr(source + "." + sourceAttr,target + "." + targetAttr, f =f)

def connectAttrMerge(source,target,attr,mode = "multi"):
    curInput = cmds.listConnections(target + "."+attr, s=True,d =False, p =True,skipConversionNodes=True) 
    
    if curInput != None:
        multiVis = cmds.createNode("floatMath")

        if mode == "multi":
            cmds.setAttr(multiVis + ".operation",2)

        elif mode == "add":
            cmds.setAttr(multiVis + ".operation",0)

        cmds.connectAttr(curInput[0],multiVis + ".floatA")
        cmds.connectAttr(source,multiVis + ".floatB")
        cmds.connectAttr(multiVis + ".outFloat",target + "."+attr,f =True)

    else:
        cmds.connectAttr(source,target + "."+attr)


##-----------------------------------------------------
##drivenkey
##-----------------------------------------------------
def setDrivenKey(drivenValueDict,driver,driverValue,inTngent = "flat",outTangent = "flat"):
    for targetAttr in list(drivenValueDict.keys()):        
        cmds.setDrivenKeyframe(targetAttr, cd = driver , itt = inTngent, ott = outTangent, dv = driverValue, v = float(drivenValueDict[targetAttr]))
        cmds.refresh()
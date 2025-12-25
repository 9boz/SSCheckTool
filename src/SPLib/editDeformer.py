from __future__ import (absolute_import, division,print_function, unicode_literals)

import os
import maya.cmds as cmds
from . import editTransform,editString
from xml.etree import ElementTree

##ComponentTag------------------------------------------------------------

def getComponentTagExp(deformer):
    compTagDict = {}
    index = cmds.deformer(deformer,q =True,gi=True)
    outputShapes = cmds.deformer(deformer,q =True,g=True)

    for i,outputShape in zip(index,outputShapes): 
        outputTransform = editTransform.getTransformNode([outputShape])[0]

        expression = cmds.getAttr(deformer+".input["+str(i)+"].componentTagExpression")
        
        compTagDict[outputTransform] = {
                                        "expression":expression,
                                        "index":i
                                        }

    return compTagDict

def setComponentTagExp(target,deformer,tagExp):
    compTagDict = getComponentTagExp(deformer)

    if target not in list(compTagDict.keys()):
        print(deformer + "  donot effected  " + target)
        return

    cmds.setAttr(
                deformer+".input["+str(compTagDict[target]["index"])+"].componentTagExpression",
                tagExp,
                type = "string"
    )


##skinCluster----------------------------------------------------
def getInfluence(skinNode):
    infs = cmds.skinCluster(skinNode, q =True, inf =True)    
    return infs

def getSkinCluster(node):
    history = cmds.listHistory(node,pruneDagObjects =True)    
    skinNode = cmds.ls(history,type = "skinCluster") or None
    
    if skinNode != None:
        return skinNode[0]

    return None

def createSkinCluster(object,joints,nodeName = None):
    if nodeName == None:
        nodeName = object + "_SC"

    if cmds.objExists(nodeName) ==False:
        cmds.skinCluster(joints,object,normalizeWeights = 1,toSelectedBones =True,name = nodeName)[0]

    return nodeName

def addInfs(target,joints):
    skinNode = getSkinCluster(target)

    if skinNode == None:
        skinNode = createSkinCluster(target,joints)

    curInfs = getInfluence(skinNode)
    toAddInfs = list(set(joints) - set(curInfs))
    
    for inf in toAddInfs:
        cmds.skinCluster(skinNode, e =True, ai = inf, weight = 0)

    return

def addMiirorInfs(target,leftSuffix,rightSuffix):
    skinNode = getSkinCluster(target)

    if skinNode == None:
        return
    
    curInfs = getInfluence(skinNode)

    toAddInfs = []
    for inf in curInfs:
        mirrorInf = inf.replace(leftSuffix,rightSuffix)

        if cmds.objExists(mirrorInf):
            if mirrorInf not in curInfs:
                toAddInfs.append(mirrorInf)
    
        mirrorInf = inf.replace(rightSuffix,leftSuffix)

        if cmds.objExists(mirrorInf):
            if mirrorInf not in curInfs:
                toAddInfs.append(mirrorInf)

    for inf in toAddInfs:
        cmds.skinCluster(skinNode, e =True, ai = inf, weight = 0)

    return

def matchInfs(source,target):
    sourceSkinNode = getSkinCluster(source)
    targetSkinNode = getSkinCluster(target)
    
    sourceAddInfs = []
    
    if sourceSkinNode == None:
        return targetSkinNode,sourceAddInfs

    sourceInfs = getInfluence(sourceSkinNode)

    if targetSkinNode == None:
        targetSkinNode = createSkinCluster(target,sourceInfs)
    
    else:
        targetInfs = getInfluence(targetSkinNode)
        allInf = set(sourceInfs) | set(targetInfs)

        targetAddInfs = list(allInf - set(targetInfs))
        sourceAddInfs = list(allInf - set(sourceInfs))

        for inf in targetAddInfs:
            cmds.skinCluster(targetSkinNode, e =True, ai = inf, weight = 0)
        
        for inf in sourceAddInfs:
            cmds.skinCluster(sourceSkinNode, e =True, ai = inf, weight = 0)

    return targetSkinNode,sourceAddInfs

def removeInfs(skinNode,infs):
    for inf in infs:
        cmds.skinCluster(skinNode,e =True, removeInfluence = inf)

def removeUnuseInfs(skinNode):
    allInf =  cmds.skinCluster(skinNode,q =True, influence =True)
    weightedInf= cmds.skinCluster(skinNode,q =True, weightedInfluence =True)
    removeInf = list(set(allInf) - set(weightedInf))
    removeInfs(skinNode,removeInf)

def setSkinWeightList(wieghtList,mesh,skinNode,jointList):
    shape = cmds.listRelatives(mesh,type = "shape")[0]    
    componentType = "vtx"

    if cmds.nodeType(shape) == "nurbsSurface":
        componentType = "cv"

    elif cmds.nodeType(shape) == "nurbsCurve":
        componentType = "cv"

    elif cmds.nodeType(shape) == "lattice":
        componentType = "pt"

    for i in range(0,len(wieghtList)):
        transformValue = []
        
        for joint,value in zip(jointList,wieghtList[i]):
            transformValue.append((joint,value))

        cmds.skinPercent(
                            skinNode,
                            mesh + '.'+componentType+'['+str(i)+']',
                            transformValue = transformValue
                        )

def getSkinWeightList(skinNode):
    wieghtList = []

    vtxIndex = cmds.getAttr(skinNode + ".weightList", mi =True)
    jointIndex = cmds.getAttr(skinNode + ".matrix", mi =True)

    for i in vtxIndex:
        vtxWeight = []
        
        for ii in jointIndex:            
            weight = cmds.getAttr(skinNode + ".weightList["+str(i)+"].weights["+str(ii)+"]")
            vtxWeight.append(weight)

        wieghtList.append(vtxWeight)

    return wieghtList

def resetBindMatrix(target):
    skinNode = getSkinCluster(target)

    if skinNode == None:
        return

    infs = getInfluence(skinNode)

    for i in range(0,len(infs)):
        curMatrix = cmds.getAttr(infs[i] + ".worldInverseMatrix[0]")        
        cmds.setAttr(skinNode + ".bindPreMatrix["+str(i)+"]",curMatrix,type = "matrix")

def exportSkinWeight(path,node,ext = "xml",cleanup = True,makeDir = True,fileName = None):
    if cmds.nodeType(node) != "transform":
        return

    skinNode = getSkinCluster(node)

    if skinNode == None:
        return

    if cleanup:
        removeUnuseInfs(skinNode)

    if skinNode != node + "_SC":
        skinNode = cmds.rename(skinNode, node + "_SC")

    if fileName == None:
        fileName = node + "_skinWeight." + ext
    else:
        fileName = fileName + "." + ext

    if os.path.exists(path) ==False:
        os.makedirs(path)
        
    cmds.deformerWeights(fileName, path = path, deformer = skinNode, format = ext.upper(),ex = True)

    return fileName

def importSkinWeight(path,fileName):
    ext = fileName.split(".")[-1]
    allInfsDict = {}

    if ext == "xml":
        tree = ElementTree.parse(path + fileName)
        root = tree.getroot()    

        for e in root.findall('weights'):
            inf = e.get("source")
            shape = e.get("shape")
            node = e.get("deformer")

            if node in allInfsDict.keys():
                allInfsDict[node]["infs"].append(inf)
                
            else:
                allInfsDict[node] = {
                                        "infs":[inf],
                                        "shape":shape
                }

    for skinNode in allInfsDict.keys():
        allInfs = allInfsDict[node]["infs"]
        shape = allInfsDict[node]["shape"]
        if cmds.objExists(skinNode) == False:
            skinNode = createSkinCluster(shape,allInfs,skinNode)

        addInfs(shape,allInfs)
        cmds.dgeval(skinNode)

        if len(allInfs) != 1:
            cmds.deformerWeights(fileName, path = path, deformer = skinNode, method = "index",im = True)
            cmds.skinCluster(skinNode,e =True,forceNormalizeWeights = True)

def exportSkinWeightHierarchy(topNode,exportDirPath):
    meshNodes = editTransform.listTypeNodes("mesh",topNode = topNode)

    for meshNode in meshNodes:
        exportSkinWeight(exportDirPath,meshNode,ext = "xml",cleanup = True)

def mirrorSkinCluster(source,target,leftSuffix,rightSuffix,overWrite =False):
    sourceSkinNode = getSkinCluster(source)
    if sourceSkinNode == None:
        return

    ##export temp
    path = cmds.internalVar(userAppDir=True) + 'temp/'
    fileName = "tempWeight"
    index = 0
    while os.path.exists(path + fileName + ".xml"):
        index += 1
        fileName = "tempWeight"+str(index).zfill(2)

    tmpFileName = exportSkinWeight(path,source,ext = "xml",cleanup = True,makeDir = True,fileName=fileName)
        
    targetShape = cmds.listRelatives(target,type = "shape")[0]

    from xml.etree import ElementTree
    tree = ElementTree.parse(path+tmpFileName)
    root = tree.getroot()    
    targetInfs = []

    for e in root.findall('weights'):
        targetInf = e.get("source")

        mirrorInf = targetInf
        if targetInf.find(leftSuffix) != -1:
            mirrorInf = targetInf.replace(leftSuffix,rightSuffix)
        
        elif targetInf.find(rightSuffix) != -1:
            mirrorInf = targetInf.replace(rightSuffix,leftSuffix)

        targetInfs.append(mirrorInf)
        e.set("source",mirrorInf)
        e.set("shape",targetShape)
        e.set("deformer",target + "_SC")
    
    tree.write(path + tmpFileName, encoding='UTF-8')

    if getSkinCluster(target) == None:        
        print("set mirrorWeight......"+ source + " to " + target)
        importSkinWeight(path,tmpFileName)  
    else:
        if overWrite:            
            addInfs(target,targetInfs)
            print("set mirrorWeight......"+ source + " to " + target)
            importSkinWeight(path,tmpFileName)

        else:
            print("already binded >> " + target)
    
    os.remove(path+tmpFileName)

def substituteSkinCluster(source,target,replaceInfDict,infPrefix="",overWrite =False):
    sourceSkinNode = getSkinCluster(source)
    if sourceSkinNode == None:
        return

    ##export temp
    path = cmds.internalVar(userAppDir=True) + 'temp/'

    index = 0
    fileName = "tempWeight"

    while os.path.exists(path + fileName + ".xml"):
        index += 1
        fileName = "tempWeight"+str(index).zfill(2)

    tmpFileName = exportSkinWeight(path,source,ext = "xml",cleanup = True,makeDir = True,fileName=fileName)
    targetShape = cmds.listRelatives(target,type = "shape")[0]

    tree = ElementTree.parse(path+tmpFileName)
    root = tree.getroot()    
    targetInfs = []

    for e in root.findall('weights'):
        targetInf = e.get("source")

        for searchString in list(replaceInfDict.keys()):                        
            targetInf = targetInf.replace(searchString,replaceInfDict[searchString])

        targetInf = editString.addPrefix(infPrefix,targetInf)        
        targetInfs.append(targetInf)
        e.set("source",targetInf)
        e.set("shape",targetShape)
        e.set("deformer",target + "_SC")
    
    tree.write(path + tmpFileName, encoding='UTF-8')

    if getSkinCluster(target) == None:        
        print("set skinWeight......"+ source + " to " + target)
        importSkinWeight(path,tmpFileName)  

    else:
        if overWrite:            
            addInfs(target,targetInfs)
            print("set skinWeight......"+ source + " to " + target)
            importSkinWeight(path,tmpFileName)

        else:
            print("already binded >> " + target)
    
    os.remove(path+tmpFileName)

def transportSkinWeight(source,targets):
    targetTransfroms = []
    targetTransfroms = editTransform.getTransformNode(targets)    
    tempAddInfs = []
    for targetTransfrom in targetTransfroms:
        targetSkinNode,sourceAddInfs = matchInfs(source,targetTransfrom)
        tempAddInfs = list(set(tempAddInfs) & set(sourceAddInfs))

    sourceSkinNode = getSkinCluster(source)

    if sourceSkinNode == None:
        return
    
    for target in targets:
        nodeType = cmds.nodeType(target)

        ##target == component
        if nodeType == "mesh" or nodeType == "nurbsCurve" or nodeType == "nurbsSurface" or nodeType == "lattice":
            cmds.select(source,r=True)
            cmds.select(target,add=True)
            cmds.copySkinWeights(
                                    sampleSpace = 0,
                                    noMirror = True,
                                    smooth = False,
                                    normalize =True,
                                    surfaceAssociation = "closestPoint",
                                    influenceAssociation = ["name","closestJoint","closestBone"]
                                )

        ##target == transform
        else:
            cmds.select(source,r=True)
            cmds.select(target,add=True)
            targetSkinNode = getSkinCluster(target)
            cmds.copySkinWeights(
                                    sampleSpace = 0,
                                    noMirror = True,
                                    smooth = False,
                                    normalize =True,
                                    surfaceAssociation = "closestPoint",
                                    influenceAssociation = ["name","closestJoint","closestBone"],
                                    ss = sourceSkinNode,
                                    ds = targetSkinNode
                                )
        print("transport skinWeight......"+ source + " to " + target)

    removeInfs(sourceSkinNode,tempAddInfs)
    cmds.select(cl =True)

##other deformer-----------------------------------------------------------------------------------------
def getDeformer(node,deformerType):
    history = cmds.listHistory(node,pruneDagObjects =True)    
    deformNodes = cmds.ls(history,type = deformerType) or None
    
    if deformNodes != None:
        return deformNodes
    
    return deformNodes

def exportDeformerWeight(path,targets,deformerType):
    deformerAttrDict = {
        "tension":["smoothingIterations","smoothingStep","inwardConstraint","outwardConstraint","squashConstraint","stretchConstraint","relative","shearStrength","bendStrength","pinBorderVertices"],
        "deltaMush":["smoothingIterations","smoothingStep","inwardConstraint","outwardConstraint","distanceWeight","displacement","pinBorderVertices"],
        "ffd":[],
        "sine":["amplitude","wavelength","offset","dropoff","lowBound","highBound"]
    }

    deformNodes = []
    for node in targets:
        if cmds.nodeType(node) != "transform":
            continue

        node_deformNodes = getDeformer(node,deformerType)
        if node_deformNodes == None:
            continue
        
        for deformNode in node_deformNodes:
            if deformNode not in deformNodes:
                deformNodes.append(deformNode)

    for deformNode in deformNodes:        
        fileName = deformNode + "_"+deformerType+"Weight.py"   
        deformerSet = cmds.listConnections(deformNode + ".message",d =True, s =False)[0]
        deformerSet = cmds.ls(deformerSet,type = "objectSet")[0]
        deformer_members = cmds.sets(deformerSet, q =True)
        deformer_members = cmds.ls(deformer_members,fl =True)
        deformer_members.sort()
        
        weightString = ""

        if deformerType in deformerAttrDict.keys():
            attrs = deformerAttrDict[deformerType]

            for attr in attrs:
                value  = cmds.getAttr(deformNode + "." + attr)
                weightString += "cmds.setAttr( \""+deformNode+"."+attr+"\","+str(value)+")\n"

        for deformer_member in deformer_members:            
            weight = cmds.percent(deformNode,[deformer_member],q=True,v=True)[0]          
            weightString += "cmds.percent( \""+deformNode+"\",[\""+deformer_member+"\"],v="+str(weight)+")\n"
        
        f = open(path + fileName, "w")
        f.write(weightString)
        f.close()

##blendShape-----------------------------------------------------------------------------------------
def deducePoint(outputPoint,samplePoint,editPoint):
    for i in range(0,100):
        if editTransform.getVector(samplePoint,outputPoint).length() < 0.0001:
            return
                        
        for axis in ["x","y","z"]:			
            distance = editTransform.getVector(samplePoint,outputPoint).length() 
                        
            if axis == "x":
                posValue = [distance*0.5,0.0,0.0]
                negValue = [distance*-0.5,0.0,0.0]
                    
            elif axis == "y":
                posValue = [0.0,distance*0.5,0.0]
                negValue = [0.0,distance*-0.5,0.0]
                    
            elif axis == "z":
                posValue = [0.0,0.0,distance*0.5]
                negValue = [0.0,0.0,distance*-0.5]
                    
            cmds.xform(editPoint, os =True, r =True, t = posValue)
            tmpDistancePosi = editTransform.getVector(samplePoint,outputPoint).length() 
                
            cmds.xform(editPoint, os =True, r =True, t = negValue)
                
            cmds.xform(editPoint, os =True, r =True, t = negValue)
            tmpDistanceNega = editTransform.getVector(samplePoint,outputPoint).length() 
                        
            cmds.xform(editPoint, os =True, r =True, t = posValue)
                                    
            if tmpDistancePosi > tmpDistanceNega:
                cmds.xform(editPoint, os =True, r =True, t = negValue)
                
            elif tmpDistancePosi < tmpDistanceNega:				
                cmds.xform(editPoint, os =True, r =True, t = posValue)

def generateCollectShape(outputMesh,editMesh,targetMesh):
    shape = cmds.listRelatives(outputMesh,type = "shape")
    
    componentType = "vtx[*]"

    if cmds.nodeType(shape[0]) == "nurbsSurface":
        componentType = "cv[*]"
    elif cmds.nodeType(shape[0]) == "nurbsCurve":
        componentType = "cv[*]"

    cmds.select(cl =True)
    cmds.select(outputMesh + "."+componentType,r=True)
    vtxNum = cmds.ls(sl = True, fl =True)
    cmds.select(cl =True)
    
    i = 0
    for distPoint in vtxNum:
        component = distPoint.split(".")[-1]
        samplePoint = editMesh + "." + component
        effectPoint = targetMesh + "." + component
        deducePoint(distPoint,samplePoint,effectPoint)                
        i = i+1
    

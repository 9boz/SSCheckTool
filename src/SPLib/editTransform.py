from __future__ import (absolute_import, division,print_function, unicode_literals)

import maya.cmds as cmds
import maya.api.OpenMaya as om
from . import editAttrs
##----------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------
##positions
##----------------------------------------------------------------------------------------------
def getPosition(target):
    nodeType = cmds.nodeType(target)
    
    if nodeType == "joint" or nodeType == "transform" or nodeType == "ikHandle" or nodeType == "place3dTexture":
        # return cmds.xform(target , q =True , ws = True, t =True)
        return cmds.xform(target , q =True , ws = True, rotatePivot =True)

    elif nodeType == "mesh" or nodeType == "nurbsCurve" or nodeType == "nurbsSurface" or nodeType == "lattice":
        return cmds.xform(target , q =True , ws = True, t =True)

def getRotation(target):
    return cmds.xform(target , q =True , ws = True, ro =True)

def getBBox(targets):
    totalBBox = []
    
    for target  in targets:
        nodeType = cmds.nodeType(target)
        bbox = [0,0,0,0,0,0]

        if nodeType == "joint":
            bbox = cmds.xform(target , q =True , ws = True, t =True)
            bbox.extend(cmds.xform(target , q =True , ws = True, t =True))
    
        elif nodeType == "transform":
            bbox = cmds.xform(target, q =True,boundingBox =True)
        
        elif nodeType == "mesh" or nodeType == "nurbsCurve" or nodeType == "nurbsSurface" or nodeType == "lattice":
            bbox = cmds.xform(target, q =True,boundingBox =True,ws=True)

        if len(totalBBox) == 0:
            totalBBox = list(bbox)
        
        else:
            for i in range(0,3):
                if totalBBox[i] > bbox[i]:
                    totalBBox[i] = bbox[i]
            
            for i in range(3,6):                
                if totalBBox[i] < bbox[i]:
                    totalBBox[i] = bbox[i]
        
    return totalBBox

def getBBoxCenter(targets):
    totalBBox = getBBox(targets)

    if len(totalBBox) == 0:
        return [0,0,0]
        
    return [(totalBBox[0] + totalBBox[3])/2.0,(totalBBox[1] + totalBBox[4])/2.0,(totalBBox[2] + totalBBox[5])/2.0]    

def getAveragePosition(targets):
    centerPosition = om.MVector(0,0,0)

    for target in targets:        
        position = om.MVector(getPosition(target)) 
        centerPosition = centerPosition + position
    
    if len(targets) != 0:
        centerPosition = centerPosition *(1.0/len(targets))

    return centerPosition

def getDivisionPositions(startPoint,endPoint,division):
    vectorA = om.MVector(getPosition(startPoint))

    directVector = getVector(startPoint,endPoint)
    length = directVector.length() / (division+1)
    normalDirectVector = directVector.normal()

    divisionVectors = []
    for i in range(0,division):
        divLength = length*(i+1)

        divisionVectors.append(vectorA + (normalDirectVector*divLength))
    
    return divisionVectors

def getChNodeTransform(target):
    chNodes = cmds.listRelatives(target,type="transform",fullPath =True) or []
    chNodesPosition = {}

    for node in chNodes:
        chNodesPosition[node] = {"position":getPosition(node),"rotation":getRotation(node)}

    return chNodesPosition

def restoreChNodeTransform(chNodesPosition):
    for node in list(chNodesPosition.keys()):
        cmds.xform(node ,ws =True , t = chNodesPosition[node]["position"])
        cmds.xform(node ,ws =True , ro =chNodesPosition[node]["rotation"])

def snapPosition(source,target,keepCh,axis = "xyz",position = None):
    if keepCh:
        chNodesPosition = getChNodeTransform(target)

    curPosition = getPosition(target)

    if position == None:
        position = getPosition(source)
    
    distPosition = list(curPosition)

    if "x" in axis:
        distPosition[0] = position[0]
    if "y" in axis:
        distPosition[1] = position[1]
    if "z" in axis:
        distPosition[2] = position[2]

    cmds.xform(target, ws =True, t =distPosition)

    if keepCh:
        restoreChNodeTransform(chNodesPosition)

    return

def snapRotation(source,target,keepCh):
    if keepCh:
        chNodesPosition = getChNodeTransform(target)

    rotation = getRotation(source)
    cmds.xform(target, ws =True, ro = rotation)

    if cmds.nodeType(target) == "joint":
        cmds.makeIdentity(target,apply = True,r =1)
        
    if keepCh:
        restoreChNodeTransform(chNodesPosition)

    return

def mirrorMatrix(source,pivot,mirrorAxis):        

    nodeType = cmds.nodeType(source)
    
    if nodeType == "joint" or nodeType == "transform" or nodeType == "ikHandle" or nodeType == "place3dTexture":
        curMatrix = om.MMatrix(cmds.xform(source , q =True , ws = True, matrix =True))
    elif nodeType == "mesh" or nodeType == "nurbsCurve" or nodeType == "nurbsSurface" or nodeType == "lattice":
        position = getPosition(source)
        curMatrix = om.MTransformationMatrix(om.MMatrix.kIdentity).setTranslation(om.MVector(position),om.MSpace.kWorld).asMatrix()
    
    if mirrorAxis == "x":
        mirrorScale = [-1.0,1.0,1.0]
    elif mirrorAxis == "y":
        mirrorScale = [1.0,-1.0,1.0]
    elif mirrorAxis == "z":
        mirrorScale = [1.0,1.0,-1.0]

    mirrorScaleMatrix = om.MTransformationMatrix(om.MMatrix.kIdentity).setScale(mirrorScale,om.MSpace.kWorld).asMatrix()

    if pivot == "world" or pivot == None:
        pivotMatrix = om.MMatrix.kIdentity
    else:
        pivotMatrix = om.MMatrix(cmds.xform(pivot , q =True , ws = True, matrix =True))
    
    pivotMatrix_inverse = pivotMatrix.inverse()
    dist_matrix = curMatrix * pivotMatrix_inverse * mirrorScaleMatrix * pivotMatrix

    dist_matrix = om.MTransformationMatrix(dist_matrix).setScale([1.0,1.0,1.0],om.MSpace.kWorld).asMatrix()    
    dist_matrix = om.MTransformationMatrix(dist_matrix).setScale([-1.0,-1.0,-1.0],om.MSpace.kObject).asMatrix()    
    dist_matrix = om.MTransformationMatrix(dist_matrix).setScale([1.0,1.0,1.0],om.MSpace.kWorld).asMatrix()    
    dist_matrix = om.MTransformationMatrix(dist_matrix).setShear([0.0,0.0,0.0],om.MSpace.kWorld).asMatrix()

    return dist_matrix

def getReverseAxisMatrix(targetMatrix,reverseAxis):
        axisScale = [1.0,1.0,1.0]

        for axis in reverseAxis:
            if axis.lower() == "x":
                axisScale[0] = -1.0
            
            elif axis.lower() == "y":
                axisScale[1] = -1.0
            
            elif axis.lower() == "z":
                axisScale[2] = -1.0

        dist_matrix = om.MTransformationMatrix(targetMatrix).setScale(axisScale,om.MSpace.kObject).asMatrix()
        dist_matrix = om.MTransformationMatrix(dist_matrix).setScale([1.0,1.0,1.0],om.MSpace.kWorld).asMatrix()    
        dist_matrix = om.MTransformationMatrix(dist_matrix).setShear([0.0,0.0,0.0],om.MSpace.kWorld).asMatrix()        
        
        return dist_matrix

def getMirrorPosition(source,pivot,mirrorAxis):
    setMatrix = mirrorMatrix(source,pivot,mirrorAxis)
    mirrorPosition = om.MTransformationMatrix(setMatrix).translation(om.MSpace.kWorld)
    
    return mirrorPosition

def getMirrorOrient(source,pivot,mirrorAxis,function,reverseAxis = ""):    
    setMatrix = mirrorMatrix(source,pivot,mirrorAxis)
    
    if function == "behavior":
        mirrorOrient = om.MTransformationMatrix(setMatrix).rotation(False)
        return [om.MAngle(mirrorOrient.x).asDegrees(), om.MAngle(mirrorOrient.y).asDegrees(), om.MAngle(mirrorOrient.z).asDegrees()]        
    
    elif function == "orientation":
        rotation = getRotation(source)
        return rotation
    
    elif function == "revAxis":
        setMatrix = mirrorMatrix(source,pivot,mirrorAxis)
        setMatrix = getReverseAxisMatrix(setMatrix,reverseAxis)
        
        mirrorOrient = om.MTransformationMatrix(setMatrix).rotation(False)
        return [om.MAngle(mirrorOrient.x).asDegrees(), om.MAngle(mirrorOrient.y).asDegrees(), om.MAngle(mirrorOrient.z).asDegrees()]        
    
    elif function == "direction":
        return [0.0,0.0,0.0]

def getJointOrientMatrix(target,inverse = False):
    composeMatrix = cmds.createNode("composeMatrix")

    cmds.setAttr(composeMatrix + ".inputRotate", *cmds.getAttr(target + ".jointOrient")[0])    
    returnMatrix = cmds.getAttr(composeMatrix + ".outputMatrix")
    
    inversematrix = cmds.createNode("inverseMatrix")
    cmds.connectAttr(composeMatrix + ".outputMatrix" , inversematrix + ".inputMatrix")
    returnInvMatrix = cmds.getAttr(inversematrix + ".outputMatrix")

    cmds.delete(composeMatrix)
   
    if inverse:
        return returnInvMatrix

    return returnMatrix

def getParamOnCurve(curve,target):
    curveInfo = cmds.createNode("nearestPointOnCurve")
    cmds.connectAttr(curve + ".worldSpace[0]", curveInfo + ".inputCurve")    
    cmds.setAttr(curveInfo + ".inPosition",*getPosition(target))
    parameter = cmds.getAttr(curveInfo + ".parameter")
    cmds.delete(curveInfo)
    
    return parameter

def getPointOnCurve(curve,parameter,normalaize = False):
    curveInfo = cmds.createNode("pointOnCurveInfo")
    cmds.setAttr(curveInfo + ".turnOnPercentage",normalaize)
    cmds.setAttr(curveInfo + ".parameter",parameter)	
    cmds.connectAttr(curve + ".local",curveInfo + ".inputCurve")
    
    posX = cmds.getAttr (curveInfo + ".positionX")
    posY = cmds.getAttr (curveInfo + ".positionY")
    posZ = cmds.getAttr (curveInfo + ".positionZ")
    cmds.delete(curveInfo)
    
    return [posX,posY,posZ]


def getOtherSideVtx(sourceVtxID,sourceMesh,tagetMesh,pivot = "world",mirrorAxis = "x"):    
    mirrorPosition = getMirrorPosition(sourceMesh + ".vtx["+str(sourceVtxID)+"]",pivot,mirrorAxis)       
    mirrorPositionVector = om.MVector(mirrorPosition)

    meshDagPath = getDagNode(tagetMesh)
    shapeFn = om.MFnMesh(meshDagPath)
    
    space =  om.MSpace.kWorld    
    otherSidePoint,faceID = shapeFn.getClosestPoint(om.MPoint(mirrorPosition),space)

    faceIterator = om.MItMeshPolygon(meshDagPath)
    faceIterator.setIndex(faceID)
    vtxIDs = faceIterator.getVertices()
    faceVtxPositions = faceIterator.getPoints(om.MSpace.kWorld)

    minlength = None
    targetVtxID = None
    for faceVtxPosition,vtxID in zip(faceVtxPositions,vtxIDs):
        targetVector = om.MVector(faceVtxPosition)        
        length = (mirrorPositionVector - targetVector).length()
        
        if minlength == None:
            minlength = length
            targetVtxID = vtxID
        elif minlength > length:
            minlength = length
            targetVtxID = vtxID

    return targetVtxID

def getOtherSideFace(sourceFaceID,sourceMesh,tagetMesh,pivot = "world",mirrorAxis = "x"):    
    meshDagPath = getDagNode(tagetMesh)
    faceIterator = om.MItMeshPolygon(meshDagPath)
    faceIterator.setIndex(sourceFaceID)
    vtxIDs = faceIterator.getVertices()
        
    mirrorFaceIDs = []
    VtxIterator = om.MItMeshVertex(meshDagPath)
    
    for vtxID in vtxIDs:
        mirrorVtxID = getOtherSideVtx(vtxID,sourceMesh,tagetMesh,pivot,mirrorAxis)                
        VtxIterator.setIndex(mirrorVtxID)
        connectedFaceID = VtxIterator.getConnectedFaces()        
        if len(mirrorFaceIDs) == 0:
            mirrorFaceIDs = connectedFaceID
        else:
            mirrorFaceIDs = list(set(mirrorFaceIDs) & set(connectedFaceID))
                
    return mirrorFaceIDs
        
def getHardEdges(target,idNumber = False):
    edgeNum,polyNum,uvSetNum = getComponentNum(target)
    dagPath = getDagNode(target)
    FnShape = getShapeFn(dagPath)

    hardEdgeIDs = []
    for edgeID in range(0,edgeNum):    
        if FnShape.isEdgeSmooth(edgeID)==False:

            if idNumber:
                hardEdgeIDs.append(edgeID)
            else:
                hardEdgeIDs.append(target + ".e["+str(edgeID)+"]")

    return hardEdgeIDs
        
    
##----------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------
##vectors
##----------------------------------------------------------------------------------------------
def stringToRevVector(axis):

    if axis[0] == "-":
        return stringToVector(axis[-1])
    
    else:
        return stringToVector("-" + axis[-1])

def stringToVector(axis):
    if axis == "x":
        return om.MVector.kXaxisVector 
    elif axis == "y":
        return om.MVector.kYaxisVector 
    elif axis == "z":
        return om.MVector.kZaxisVector 

    elif axis == "-x":
        return om.MVector.kXnegAxisVector
    elif axis == "-y":
        return om.MVector.kYnegAxisVector
    elif axis == "-z":
        return om.MVector.kZnegAxisVector

def axisToVector(axis,target,world = True):

    if world:
        pointMatrix = om.MMatrix(cmds.getAttr(target + ".worldMatrix[0]"))    
    else:
        pointMatrix = om.MMatrix(cmds.getAttr(target + ".matrix"))

    axisVector = om.MTransformationMatrix(pointMatrix).setTranslation(stringToVector(axis),om.MSpace.kObject).translation(om.MSpace.kWorld)
    return axisVector.normal()

def getProjctionVector(vectorA,vectorB):
    vectorA = om.MVector(vectorA)
    vectorB = om.MVector(vectorB)

    vectorB = vectorB.normal()
    dotProduct = vectorA * vectorB
    shadowVector = vectorB * dotProduct
   
    return shadowVector

def getVector(startPoint,endPoint):
    vectorA = om.MVector(getPosition(startPoint))
    vectorB = om.MVector(getPosition(endPoint))

    return vectorB - vectorA

def vectorToMatrix(axisOrder,primaryAxisVector,secondaryAxisVector,sideAxisVector):
    axisMatrix = []

    primaryAxisVector = list(primaryAxisVector)
    primaryAxisVector.append(0.0)
    secondaryAxisVector = list(secondaryAxisVector)
    secondaryAxisVector.append(0.0)
    sideAxisVector = list(sideAxisVector)
    sideAxisVector.append(0.0)

    if axisOrder == "xy":
        axisMatrix.extend(primaryAxisVector)
        axisMatrix.extend(secondaryAxisVector)
        axisMatrix.extend(sideAxisVector)

    elif axisOrder == "xz":
        axisMatrix.extend(primaryAxisVector)
        axisMatrix.extend(sideAxisVector)
        axisMatrix.extend(secondaryAxisVector)
    
    elif axisOrder == "yx":        
        axisMatrix.extend(secondaryAxisVector)
        axisMatrix.extend(primaryAxisVector)
        axisMatrix.extend(sideAxisVector)
        
    elif axisOrder == "yz":
        axisMatrix.extend(sideAxisVector)
        axisMatrix.extend(primaryAxisVector)        
        axisMatrix.extend(secondaryAxisVector)

    elif axisOrder == "zx":
        axisMatrix.extend(secondaryAxisVector)
        axisMatrix.extend(sideAxisVector)
        axisMatrix.extend(primaryAxisVector)
        
    elif axisOrder == "zy":
        axisMatrix.extend(sideAxisVector)
        axisMatrix.extend(secondaryAxisVector)
        axisMatrix.extend(primaryAxisVector)

    axisMatrix.extend([0.0,0.0,0.0,1.0])   

    return axisMatrix

def getNearlestAxis(target,sampleVector):
    axisAimDict = {}

    for axis in ["x","y","z","-x","-y","-z"]:
        axisVector = axisToVector(axis,target)
        vectorA = om.MVector(sampleVector)
        vectorA = vectorA.normal()
        
        vectorB = om.MVector(axisVector)
        dotProduct = vectorA*vectorB
        axisAimDict[axis] = dotProduct

    nearlestAxis = ""
    min = 1.0

    for key in axisAimDict.keys():
        if min > (1.0 - axisAimDict[key]):
            min = (1.0 - axisAimDict[key])
            nearlestAxis = key

    return nearlestAxis

##----------------------------------------------------------------------------------------------
##DAG node
##----------------------------------------------------------------------------------------------
def createNode(nodeType,name,source = None,position = [0,0,0],rotation = [0,0,0]):
    if nodeType == "locator":
        node = cmds.spaceLocator(name = name)
    else:
        ##transform joint
        node = cmds.createNode(nodeType,name = name)

    if source != None:
        snapPosition(source,node,False)
        snapRotation(source,node,False)

    else:
        cmds.xform(node, t = position, ws = True)
        cmds.xform(node, ro = rotation, ws = True)

    return node

def getDagNode(target):    
    try:
        sellist = om.MGlobal.getSelectionListByName(target)
        return sellist.getDagPath(0)
    except:
        return None

def getFullPathName(target):
    if type(getDagNode(target)) != om.MDagPath:
        return target

    return om.MFnDagNode(getDagNode(target).node()).fullPathName()

def getShortName(target):
    if type(getDagNode(target)) != om.MDagPath:
        return target

    return om.MFnDagNode(getDagNode(target).node()).name()

def checkUniqueName(target):    
    if type(getDagNode(target)) != om.MDagPath:
        return True

    return om.MFnDependencyNode(getDagNode(target).node()).hasUniqueName()

def reParent(target,newParent):
    curParent = cmds.listRelatives(target,p=True)
    if curParent == None:
        cmds.parent(target,newParent,a =True)
    
    elif curParent[0] != newParent:
        cmds.parent(target,newParent,a =True)
        
    return 

def setOffsetParentMatrix(target):
    matrix = cmds.getAttr(target + ".matrix")
    cmds.setAttr(target + ".offsetParentMatrix",matrix,type = "matrix")
    cmds.xform(target, os =True, matrix = [1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0])

    cmds.setAttr(target + ".rotate",0.0,0.0,0.0)
    
    if cmds.nodeType(target) == "joint":
        cmds.setAttr(target + ".jointOrient",0.0,0.0,0.0)

def addOffsetNode(nodeType,target,suffix):
    offsetNode = createNode(nodeType,target + suffix ,target)
    insertHierarchy(target,offsetNode)

    if nodeType == "joint":
        cmds.setAttr(offsetNode + ".drawStyle",2)
    return offsetNode

def insertHierarchy(target,insertNode):
    curParent = cmds.listRelatives(target,p=True)

    if curParent != None:
        reParent(insertNode,curParent[0])
    
    reParent(target,insertNode)
    return

def createHierarchy(hierarchyList,nodeType,force):
    
    for tree in hierarchyList:
        hierarchy = tree.split("|")

        for i in range(0,len(hierarchy)):
            nodeName = hierarchy[i]

            if cmds.objExists(nodeName) == False:
                if nodeType == "objectSet":
                    cmds.sets(name = nodeName,empty =True)
                else:
                    createNode(nodeType,nodeName,source = None,position = [0,0,0],rotation = [0,0,0])

            if i != 0 and force:
                if nodeType == "objectSet":
                    cmds.sets(nodeName,forceElement = hierarchy[i-1])
                else:
                    reParent(nodeName,hierarchy[i-1])

    return

def getCurHierarchy(target,topNode = None,fullpath =False):    
    hierarchyList = []

    if fullpath:
        target = getFullPathName(target)

        if topNode != None:
            topNode = getFullPathName(topNode)

    hierarchyList.append(target)

    if target == topNode:
        return hierarchyList

    reachTop = False

    count = 0

    while reachTop == False:
        parent = cmds.listRelatives(hierarchyList[-1], p =True, f = fullpath)
        
        if parent == None:
            reachTop = True
            continue

        elif parent[0] == topNode:
            reachTop = True

        hierarchyList.append(parent[0])

    hierarchyList.reverse()

    return hierarchyList

def getTransformNode(targets,fullpath = False):
    transfromNodes = []
    
    for target in targets:
        nodeTypes = cmds.nodeType(target,inherited = True)
        transfromNode = None
        if "transform" in nodeTypes:
            transfromNode = target
        
        elif "shape" in nodeTypes:
            parent = cmds.listRelatives(target, p =True,f=fullpath)[0]
            transfromNode = parent

        if transfromNode not in transfromNodes:
            transfromNodes.append(transfromNode)
    
    return transfromNodes

def getIKJointChain(ikHandle,fullpath):
    ikHandleDag = getDagNode(ikHandle)    
    ikHandleDnFn = om.MFnDependencyNode(ikHandleDag.node())
    
    if fullpath:
        startJoint = om.MFnDagNode(ikHandleDnFn.findPlug('startJoint', False).source().node()).fullPathName()
        effector = om.MFnDagNode(ikHandleDnFn.findPlug('endEffector', False).source().node()).fullPathName()

        effectorDag = getDagNode(effector)
        effectorDnFn = om.MFnDependencyNode(effectorDag.node())
        endJoint = om.MFnDagNode(effectorDnFn.findPlug('offsetParentMatrix', False).source().node()).fullPathName()
    
    else:
        startJoint = om.MFnDagNode(ikHandleDnFn.findPlug('startJoint', False).source().node()).name()
        effector = om.MFnDagNode(ikHandleDnFn.findPlug('endEffector', False).source().node()).name()

        effectorDag = getDagNode(effector)
        effectorDnFn = om.MFnDependencyNode(effectorDag.node())
        endJoint = om.MFnDagNode(effectorDnFn.findPlug('offsetParentMatrix', False).source().node()).name()

    jointChain = getCurHierarchy(endJoint,startJoint,fullpath)

    return jointChain

def subIgnorTypeNodes(nodes,ignorNodeTypes,topNode,fullpath):

        for ignorType in ignorNodeTypes:
            nodes = list(set(nodes) - set(listTypeNodes(ignorType,topNode,fullpath)))

        return nodes

def listTypeNodes(nodeType,topNode = None, fullpath = False,ignorNodeTypes =[],namespace = None):
    defaultNodes = cmds.ls(defaultNodes =True, l= fullpath)

    if fullpath:
        topNode = getFullPathName(topNode)
    
    nodes = []    
    if nodeType == "transform":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []

    elif nodeType == "noShapeTransform":
        nodes = listTypeNodes("transform",topNode,fullpath)
        
        shapes = cmds.ls(shapes =True, l = fullpath)        
        removeNodes = getTransformNode(shapes,fullpath)
        nodes = list(set(nodes) - set(removeNodes))

    elif nodeType == "locator":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []
        nodes = getTransformNode(nodes,fullpath)
        
    elif nodeType == "joint":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []

    elif nodeType == "IKJoints":
        ikHandles = cmds.ls(type = "ikHandle", l= fullpath) or []
        
        for ikHandle in ikHandles:
            jointChain = getIKJointChain(ikHandle,fullpath)
            nodes.extend(jointChain)

    elif nodeType == "constraint":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []

    elif nodeType == "mesh" or nodeType == "nurbsCurve" or nodeType == "nurbsSurface":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []
        nodes = getTransformNode(nodes,fullpath)

    elif nodeType == "camera":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []
        nodes = getTransformNode(nodes,fullpath)

    elif nodeType == "light":
        nodes = cmds.ls(type = nodeType, l= fullpath) or []
        nodes = getTransformNode(nodes,fullpath)

    else:
        nodes = cmds.ls(type = nodeType, l= fullpath) or []

    if topNode != None:
        if cmds.objExists(topNode):
            allHierarchy = cmds.listRelatives(topNode,ad =True,f=fullpath) or []
            allHierarchy.append(topNode)
            nodes = list(set(nodes) & set(allHierarchy))
        else:
            nodes = []
            
    nodes = subIgnorTypeNodes(nodes,ignorNodeTypes,topNode,fullpath)
    nodes = list(set(nodes) - set(defaultNodes))
    
    
    if namespace != None:
        tempNodes= []
        for node in nodes:
            if node.startswith(namespace +":"):
                tempNodes.append(node)

        nodes = tempNodes
        
        
    return nodes

def listSetMembers(setName,nodeTypes,allHierarchy,namespace = ""):
    if cmds.objExists(setName) ==False:
        return []

    allMembers = cmds.sets(setName,q=True)
    memberSets = cmds.ls(allMembers, type = "objectSet") or []
    memberNodes = []

    for nodeType in nodeTypes:
        nodes = cmds.ls(allMembers, type = nodeType) or []

        if namespace == "":
            memberNodes = list(set(memberNodes) | set(nodes))

        else:
            for node in nodes:
                if node.startswith(namespace +":"):
                    memberNodes = list(set(memberNodes) | set([node]))

    if allHierarchy:
        for memberSet in memberSets:
            memberNodes.extend(listSetMembers(memberSet,nodeTypes,allHierarchy,namespace))
    
    return memberNodes

def hideHistory(targets,ignorNodes = ["initialParticleSE"]):
    for target in targets:
        outputs = cmds.listConnections(target, d = True) or []

        for output in outputs:
            futureNodes = cmds.listHistory(output,pruneDagObjects =True,future =True) or []
            
            for node in futureNodes:
                if cmds.nodeType(node) in ignorNodes:
                    # cmds.setAttr(node + ".ihi",True)
                    continue

                cmds.setAttr(node + ".ihi",False)


def getCurOrder(target):
    parent = cmds.listRelatives(target, p =True)

    if parent == None:
        topNodes = cmds.ls(assemblies =True)
        index = topNodes.index(target)
        return index

    else:
        nodes = cmds.listRelatives(parent[0],type = "transform")
        index = nodes.index(target)
        return index

def setOrder(target,index):
    cmds.reorder(target, f =True)

    if index != 0:
        cmds.reorder(target, relative = index)

def sortOrder(targets):
    startIndex = None

    for target in targets:
        index = getCurOrder(target)

        if startIndex == None:
            startIndex = index
        elif startIndex > index:
            startIndex = index

    sortTargets = sorted(targets)
    
    for i in range(0,len(sortTargets)):
        setOrder(sortTargets[i],startIndex + i)

def getSetsHierarchy(setName,parentSets,setNameList):
    setMembers = listSetMembers(setName,["objectSet"],False,namespace = "")

    tmpParentSets = list(parentSets)
    tmpParentSets.append(setName)
        
    for setMember in setMembers:
        setLongName = "|".join(tmpParentSets)+ "|" + setMember
        setNameList.append(setLongName)
        
        setNameList = getSetsHierarchy(setMember,tmpParentSets,setNameList)
           
    return setNameList

##-----------------------------------------------
##joints
##-----------------------------------------------
##set joint Orient-------------------------------
def primaryDistVector(target,primaryAimType,primaryAimTarget):
    targetPosition = om.MVector(getPosition(target))

    if primaryAimType == "next":
        chNodes = cmds.listRelatives(target,type="transform",fullPath =True)
        panretNodes = cmds.listRelatives(target,type="transform",p=True,fullPath =True)

        if chNodes != None:
            aimPosition = om.MVector(getPosition(chNodes[0]))
            
        elif chNodes == None and panretNodes != None:
            aimPosition = om.MVector(getPosition(panretNodes[0])) * -1.0

    elif primaryAimType == "object":
        aimPosition = om.MVector(getPosition(primaryAimTarget))

    distAxisVector = aimPosition - targetPosition
    distAxisVector = distAxisVector.normal()
    
    return distAxisVector

def secondaryDistVector(target,secondaryAimType,secondaryAimTarget,secondaryAimAxis):
    if secondaryAimType == "world":
        distAxisVector = stringToVector(secondaryAimAxis)

    elif secondaryAimType == "object":
        targetPosition = om.MVector(getPosition(target))
        aimPosition = om.MVector(getPosition(secondaryAimTarget))
        distAxisVector = aimPosition - targetPosition
        distAxisVector = distAxisVector.normal()

    elif secondaryAimType == "parent":
        parent = cmds.listRelatives(target,p=True,fullPath =True)
        distAxisVector = axisToVector(secondaryAimAxis,parent[0])
    
    elif secondaryAimType == "objectAxis":        
        distAxisVector = axisToVector(secondaryAimAxis,secondaryAimTarget)

    return distAxisVector

def setJointOrient(joint,primaryAxis,secondaryAxis,primaryAimType,secondaryAimType,primaryAimTarget,secondaryAimTarget,primaryAxisReverse,secondaryAxisReverse,secondaryAimAxis):
    axisOrder = primaryAxis + secondaryAxis

    chNodesPosition = getChNodeTransform(joint)

    distPrimaryAxisVector = primaryDistVector(joint,primaryAimType,primaryAimTarget)

    if primaryAxisReverse:
        distPrimaryAxisVector = distPrimaryAxisVector * -1.0

    distSecondaryAxisVector = secondaryDistVector(joint,secondaryAimType,secondaryAimTarget,secondaryAimAxis)
    
    if secondaryAxisReverse:
        distSecondaryAxisVector = distSecondaryAxisVector * -1.0

    shadowVector = getProjctionVector(distSecondaryAxisVector,distPrimaryAxisVector)
    distSecondaryAxisVector = (distSecondaryAxisVector - shadowVector).normal()
    
    if axisOrder == "zy" or axisOrder == "xz":
        distSideAxisVector = distSecondaryAxisVector ^ distPrimaryAxisVector
    else: 
        distSideAxisVector = distPrimaryAxisVector ^ distSecondaryAxisVector

    axisMatrix = vectorToMatrix(axisOrder,distPrimaryAxisVector,distSecondaryAxisVector,distSideAxisVector)
    setMatrix = om.MTransformationMatrix(om.MMatrix(axisMatrix)).setTranslation(om.MVector(getPosition(joint)),om.MSpace.kWorld).asMatrix()
    
    cmds.xform(joint, matrix = list(setMatrix), ws = True)
    restoreChNodeTransform(chNodesPosition)
    cmds.makeIdentity(joint, a =True, r=True, s =True)
    

def setJointOrientToWorld(joint):
    chNodesPosition = getChNodeTransform(joint)
    
    distPrimaryAxisVector = stringToVector("x")
    distSecondaryAxisVector = stringToVector("y")
    distSideAxisVector = stringToVector("z")
    axisMatrix = vectorToMatrix("xy",distPrimaryAxisVector,distSecondaryAxisVector,distSideAxisVector)

    setMatrix = om.MTransformationMatrix(om.MMatrix(axisMatrix)).setTranslation(om.MVector(getPosition(joint)),om.MSpace.kWorld).asMatrix()

    cmds.xform(joint, matrix = list(setMatrix), ws = True)
    restoreChNodeTransform(chNodesPosition)
    cmds.makeIdentity(joint, a =True, r=True, s =True)

def setJointOrientToZero(joint):
    chNodesPosition = getChNodeTransform(joint)        
    cmds.setAttr(joint + ".rotate",0,0,0)
    cmds.setAttr(joint + ".jointOrient",0,0,0)
    restoreChNodeTransform(chNodesPosition)
    cmds.makeIdentity(joint, a =True, r=True, s =True)

def setMirrorJointOrient(source,target,pivotOpt,mirrorAxis,mirrorFunc,keepCH,reverseAxis = ""):
    mirrorOrint = getMirrorOrient(source,pivotOpt,mirrorAxis,mirrorFunc,reverseAxis)
    # target = source.replace(search,replace)

    if cmds.objExists(target) and target != source:
        chNodesPosition = {}

        if keepCH:
            chNodesPosition = getChNodeTransform(target)

        cmds.xform(target, ro = list(mirrorOrint), ws = True)        
        restoreChNodeTransform(chNodesPosition)
        cmds.makeIdentity(target,r=True,s =False,t=False,a=True,jo = False)

##----------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------
##shapes
##----------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------
def getShapeFn(dagPath):
    FnShape = None

    if dagPath.hasFn(om.MFn.kMesh):
        FnShape = om.MFnMesh(dagPath)        

    elif dagPath.hasFn(om.MFn.kNurbsSurface):
        FnShape = om.MFnNurbsSurface(dagPath)

    elif dagPath.hasFn(om.MFn.kNurbsCurve):
        FnShape = om.MFnNurbsCurve(dagPath)

    return FnShape

def getComponentNum(target):
    dagPath = getDagNode(target)
    FnShape = getShapeFn(dagPath)
    
    edgeNum = FnShape.numEdges
    polyNum = FnShape.numPolygons
    uvSetNum = FnShape.numUVSets

    return edgeNum,polyNum,uvSetNum

def getVtxPositions(target,space = om.MSpace.kWorld):
    dagPath = getDagNode(target)
    FnShape = getShapeFn(dagPath)
    
    vtxPositions = []
    if FnShape == None:
        return vtxPositions
    
    for position in FnShape.getPoints(space):
        vtxPositions.append(list(position)[:3])

    return vtxPositions

def getCVPositions(target,space = om.MSpace.kWorld):
    dagPath = getDagNode(target)
    FnShape = getShapeFn(dagPath)
    
    cvPositions = []
    if FnShape == None:
        return cvPositions

    for position in FnShape.cvPositions(space):
        cvPositions.append(list(position)[:3])

    return cvPositions

def generateKnot(degree,cvNum):
    knot = om.MDoubleArray()
    
    if degree == 1:
        for i in range(0,cvNum):
            knot.append(i)
    
    elif degree == 2:		
        knotCount = 0
                
        for i in range(0,cvNum+1):
            knot.append(knotCount)
        
            if i > 0 and i < (cvNum-1):
                knotCount = knotCount +1
    
    elif degree == 3:
        knotCount = 0
                
        for i in range(0,cvNum+2):
            knot.append(knotCount)
    
            if i > 1 and i < (cvNum-1):
                knotCount = knotCount +1
    
    return list(knot)

def readCurveShape(target,space = "world"):
    if space == "world":
        space = om.MSpace.kWorld
    elif space == "object":
        space = om.MSpace.kObject

    cvPositions = getCVPositions(target,space = space)
    dagPath = getDagNode(target)
    
    form = None
    knots = None
    degree = None
    FnShape = getShapeFn(dagPath)
    if FnShape != None:
        form = FnShape.form
        knots = list(FnShape.knots())
        degree = FnShape.degree 
        
    return cvPositions,degree,form,knots

def createCurveShape(cvPositions,degree,form,knots = None,parent = None,editPoint = False):
    if knots == None:
        knots = generateKnot(degree,len(cvPositions))

    periodic = False
    if form == 3:
        periodic = True
    
    if editPoint ==False:
        curve = cmds.curve(point = cvPositions, knot = knots, degree = degree,periodic = periodic)
    else:
        curve = cmds.curve(ep = cvPositions, knot = knots, degree = degree,periodic = periodic)
    
    if parent != None:        
        shape = cmds.listRelatives(curve, type = "shape")[0]

        if cmds.objExists(parent) == False:
            cmds.createNode("transform",name = parent)

        cmds.parent(shape,parent,s=True,r=True)
        cmds.rename(shape,parent + "Shape")
        cmds.delete(curve)
        
        curve = parent

    return curve

def convertToBspCurve(curve,space = "local",tolerance = 0.00001):
    BspNode = cmds.createNode("fitBspline")
    cmds.setAttr(BspNode + ".keepRange",0)
    cmds.setAttr(BspNode + ".tolerance",tolerance)

    outputCurveShape = cmds.createNode("nurbsCurve")
    outputCurve = cmds.listRelatives(outputCurveShape, p = True)[0]
    outputCurve = cmds.rename(outputCurve,curve + "_bsp")

    if space == "local":
        cmds.connectAttr(curve + ".local",BspNode + ".inputCurve")
    elif space == "world":
        cmds.connectAttr(curve + ".worldSpace[0]",BspNode + ".inputCurve")

    cmds.connectAttr(BspNode + ".outputCurve",outputCurve + ".create")
    
    return outputCurve

def mirrorCurveShape(source,target,mirrorAxis = "x"):
    
    if mirrorAxis == "x":
        mirrorScale = [-1.0,1.0,1.0]
    elif mirrorAxis == "y":
        mirrorScale = [1.0,-1.0,1.0]
    elif mirrorAxis == "z":
        mirrorScale = [1.0,1.0,-1.0]

    sourceCvPositions,degree,form,knots = readCurveShape(source,space = "world")

    for i in range(0,len(sourceCvPositions)):
        cmds.xform(
                    target + ".cv["+str(i)+"]",
                    ws =True, 
                    t = [
                            sourceCvPositions[i][0]*mirrorScale[0],
                            sourceCvPositions[i][1]*mirrorScale[1],
                            sourceCvPositions[i][2]*mirrorScale[2]
                        ]
                    )


def setShapeColorGRB(target,RGB):
    shapes = cmds.listRelatives(target,s =True) or []

    for shape in shapes:		
        cmds.setAttr(shape + '.useObjectColor', 2)
        cmds.setAttr(shape + '.wireColorRGB', RGB[0],RGB[1],RGB[2], type = 'double3')

def getShapeColorGRB(target):
    shapes = cmds.listRelatives(target,s =True)
    rgb = [0.0,0.0,0.0]

    if shapes == None:
        return rgb

    if cmds.getAttr(shapes[0] + '.useObjectColor') == 2:
        rgb = cmds.getAttr(shapes[0] + '.wireColorRGB')[0]

    return rgb


def getUVPoints(target,uvSetName):
    dagPath = getDagNode(target)
    shape_Fn = getShapeFn(dagPath)
    positionList =[]

    if dagPath.hasFn(om.MFn.kMesh):
        positionList = shape_Fn.getUVs(uvSetName)
    
    return positionList

def findUVRangeFace(target,uvSet,UVRange):
    faceIds = []
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)
    face_ids = range(0,shape_Fn.numPolygons)
    it = om.MItMeshPolygon(mesh_dagPath)

    for index in face_ids:
        it.setIndex(index)

        try:
            uvs = it.getUVs(uvSet)
        except:
            continue
            
        insideRange = True
        for uPoint in uvs[0]:
            if uPoint < UVRange[0] or  uPoint > UVRange[1]:
                insideRange = False
                        
        for vPoint in uvs[1]:
            if vPoint < UVRange[2] or  vPoint > UVRange[3]:
                insideRange = False
                           
        if insideRange:
            faceIds.append(index)

    result = []
    for faceId in faceIds:
        result.append(target+".f["+str(faceId)+"]")
        
    return result

def listUVsets(target):
    if cmds.objExists(target  + ".uvSet") == False:
        return []

    uvIndex = cmds.getAttr(target  + ".uvSet", mi =True)
            
    if uvIndex == None:
        return []

    allUVInfo = []

    for index in uvIndex:
        uvSetName  = cmds.getAttr(target  + ".uvSet["+str(index)+"].uvSetName")
        
        if uvSetName != None:
            UVPoints = getUVPoints(target,uvSetName)

            allUVInfo.append(
                                {
                                    "uvSetName":uvSetName,
                                    "UPoints":UVPoints[0],
                                    "VPoints":UVPoints[1]
                                }
                            )
    
    return allUVInfo

def getUVShellDict(target,uvSet,span):
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)
    uvShellIds = shape_Fn.getUvShellsIds(uvSet)
    
    shells = {}
    for i, n in enumerate(uvShellIds[1]):
        if n in shells:
            shells[n].append(i)
        else:
            shells[n] = [i]
        
    return shells


def listColorSets(target):
    colorSets = cmds.polyColorSet(target,q=True,allColorSets=True) or []
    return colorSets

def cleanupShape(target):

    if cmds.listRelatives(target,type = "shape") == None:
        return

    ##remove connections
    inputs = cmds.listConnections(target, s =True, d =False,p =True,connections =True) or []

    for i in range(0, len(inputs),2):
        cmds.disconnectAttr(inputs[i+1],inputs[i])

    outputs = cmds.listConnections(target, s =False, d =True,p =True,connections =True) or []

    for i in range(0, len(outputs),2):
        cmds.disconnectAttr(outputs[i],outputs[i+1])

    shape = cmds.listRelatives(target,type = "shape") or []
    inputs = cmds.listConnections(shape[0], s =True, d =False,p =True,connections =True) or []

    for i in range(0, len(inputs),2):
        cmds.disconnectAttr(inputs[i+1],inputs[i])

    outputs = cmds.listConnections(shape[0], s =False, d =True,p =True,connections =True) or []

    for i in range(0, len(outputs),2):
        cmds.disconnectAttr(outputs[i],outputs[i+1])

    cmds.sets(target,e =True,forceElement = "initialShadingGroup")
    
    if cmds.objExists(target + '.outMesh'):
        cmds.polyMoveVertex(target,constructionHistory =False,translate = [0.0,0.0,0.0])
        cmds.select(cl =True)

def getSourceShape(target):
    if cmds.listRelatives(target,children=True, shapes=True, path =True) == None:
        return None

    orgShape = ""
    targetShapes = cmds.listRelatives(target,children=True, shapes=True, path =True)
    orgShapes = cmds.ls(targetShapes, intermediateObjects = True)

    if len(orgShapes)== 0:
        orgShape = targetShapes[0]
    elif len(orgShapes) > 0:
        orgShape = orgShapes[0]

    inputs = []
    if cmds.objExists(orgShape + '.inMesh'):
        inputs = cmds.listConnections(orgShape + ".inMesh", s =True, d =False) or []
    
    elif cmds.objExists(orgShape + '.local'):
        inputs = cmds.listConnections(orgShape + ".create", s =True, d =False) or []

    if len(inputs) > 0:
        orgShape = getSourceShape(inputs[0])
    
    return orgShape

def connectShapes(source,target):
    if cmds.listRelatives(target,children=True, shapes=True, path =True) == None:
        return

    orgShape = getSourceShape(target)
    
    if cmds.objExists(source + '.outMesh'):        
        cmds.connectAttr(source + '.outMesh', orgShape + '.inMesh', force = True)
    
    elif cmds.objExists(source + '.local'):
            cmds.connectAttr(source + '.local', orgShape + '.create', force = True)


def getComponentTagNames(target):
    shape = cmds.listRelatives(target,type = "shape")[-1]
    index = cmds.getAttr(shape + ".componentTags",mi =True)

    compTagNames = []

    for i in index:
        compTagName = cmds.getAttr(shape+".componentTags["+str(i)+"].componentTagName")

        if compTagName != "":
            compTagNames.append(compTagName)

    return compTagNames

##----------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------
##constarint
##----------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------
def createHierarchyMatrix(target,spaceParent):
    hierarchyList = getCurHierarchy(target,spaceParent)
    hierarchyList.reverse()
    multmatrix = cmds.createNode("multMatrix")
    
    if len(hierarchyList) == 1:        
        cmds.connectAttr(hierarchyList[0] + ".matrix", multmatrix + ".matrixIn[0]")
        
        if cmds.objExists(hierarchyList[0] + ".offsetParentMatrix"):
            cmds.connectAttr(hierarchyList[0] + ".offsetParentMatrix", multmatrix + ".matrixIn[1]")
    else:
        ii = 0
        for i in range(0,len(hierarchyList)-1):            
            cmds.connectAttr(hierarchyList[i] + ".matrix", multmatrix + ".matrixIn["+str(ii)+"]")
            ii = ii + 1

            if cmds.objExists(hierarchyList[i] + ".offsetParentMatrix"):
                cmds.connectAttr(hierarchyList[i] + ".offsetParentMatrix", multmatrix + ".matrixIn["+str(ii)+"]")
                ii = ii + 1

    return multmatrix

def addOffsetJointOrientMatrix(output,target):
    rotOutput = cmds.createNode("decomposeMatrix")
    offsetMatrix = cmds.createNode("multMatrix")
    cmds.connectAttr(output, offsetMatrix + ".matrixIn[0]")
    
    if cmds.listRelatives(target,parent =True) != None:
        parentScaleMatrix = cmds.createNode("composeMatrix")
        parent = cmds.listRelatives(target,parent =True)[0]
        editAttrs.connectAttrZip(parent,parentScaleMatrix,["scale"],["inputScale"],f =True)
        cmds.connectAttr(parentScaleMatrix + ".outputMatrix", offsetMatrix + ".matrixIn[1]")

    ##jointOrient
    jointOrientInvMatrix = getJointOrientMatrix(target,True)
    cmds.setAttr(offsetMatrix + ".matrixIn[2]", jointOrientInvMatrix, type = "matrix")

    cmds.connectAttr(offsetMatrix + ".matrixSum",rotOutput + ".inputMatrix")
    editAttrs.connectAttrZip(rotOutput,target,["outputRotate"],["rotate"],f =True)

    return rotOutput

def createMultMatrix(source,target,sourceParent,targetParent,offset):
    if offset ==True:
        offsetTemp = createNode(
                                "transform",
                                name = target + "offsettemp",
                                source = target,
                                position = target)
        cmds.parent(offsetTemp,source,a = True)
        
        multmatrix = createHierarchyMatrix(offsetTemp,sourceParent)

        cmds.disconnectAttr(offsetTemp+ ".matrix", multmatrix + ".matrixIn["+str(0)+"]")
        cmds.setAttr(multmatrix + ".matrixIn["+str(0)+"]", *cmds.getAttr(offsetTemp+ ".matrix"),type = "matrix")
        
        if cmds.objExists(offsetTemp + ".offsetParentMatrix"):
            cmds.disconnectAttr(offsetTemp+ ".offsetParentMatrix", multmatrix + ".matrixIn["+str(1)+"]")
            cmds.setAttr(multmatrix + ".matrixIn["+str(1)+"]", *cmds.getAttr(offsetTemp+ ".offsetParentMatrix"),type = "matrix")
        
        cmds.delete(offsetTemp)
    
    else:
        multmatrix = createHierarchyMatrix(source,sourceParent)

    if targetParent != "":
        hierarchyList = getCurHierarchy(target,targetParent)
        hierarchyList = hierarchyList[1:-1]
        latestIndex = cmds.getAttr(multmatrix + ".matrixIn",mi =True)[-1]

        for i in range(0,len(hierarchyList)):
            index = latestIndex + 1 + i
            cmds.connectAttr(hierarchyList[i] + ".inverseMatrix",multmatrix + ".matrixIn["+str(index)+"]")
    
    return multmatrix

def matrixConstraint(source,target,sourceParent,targetParent,attrs = ["t","r"],offset = False):
    multmatrix= createMultMatrix(source,target,sourceParent,targetParent,offset)
    outMatrix = cmds.createNode("decomposeMatrix")
    cmds.connectAttr(multmatrix + ".matrixSum", outMatrix + ".inputMatrix")

    if "t" in attrs:
        editAttrs.connectAttrZip(outMatrix,target,["outputTranslate"],["translate"],f =True)

    if "r" in attrs:
        if cmds.nodeType(target) == "joint":
            addOffsetJointOrientMatrix(multmatrix + ".matrixSum",target)

        else:
            editAttrs.connectAttrZip(outMatrix,target,["outputRotate"],["rotate"],f =True)

    return multmatrix,outMatrix

def convertToParametricPoint(curve,motionPath):    
    targetPosition = cmds.getAttr(motionPath + ".allCoordinates")[0]
    
    dagPath = getDagNode(curve)
    shapeFn = getShapeFn(dagPath)

    param = shapeFn.getParamAtPoint(om.MPoint(targetPosition))
    lengthParam = shapeFn.findLengthFromParam(param) / shapeFn.length()
    
    if lengthParam > 1.0:
        lengthParam = 1.0
    

    cmds.setAttr(motionPath + ".uValue", 0.0)
    cmds.setAttr(motionPath + ".fractionMode", 1)
    cmds.setAttr(motionPath + ".uValue", lengthParam)
    
    cmds.refresh()
    return

def constraintOnCurve(curve,target,curveSpace,targetParent,offset,attrs,parametric,parameter = None,curveParent =None):
    if curveSpace == "local":    
        transGeo = cmds.createNode("transformGeometry")        
        cmds.connectAttr(curve + ".local",transGeo + ".inputGeometry")

        if curveParent != None:
            curveOffset = cmds.createNode("multMatrix")
            cmds.setAttr(curveOffset + ".matrixIn[0]", cmds.getAttr(curve + ".worldMatrix[0]"), type = "matrix")
            cmds.connectAttr(curveParent + ".worldInverseMatrix[0]", curveOffset + ".matrixIn[1]")
            cmds.connectAttr(curveOffset + ".matrixSum",transGeo + ".transform")

        else:
            cmds.setAttr(transGeo + ".transform", cmds.getAttr(curve + ".worldMatrix[0]"), type = "matrix")
                    
        curveOutput = transGeo + ".outputGeometry"

    elif curveSpace == "world":
        curveOutput = curve + ".worldSpace[0]"

    if parameter == None:
        parameter = getParamOnCurve(curve,target)
        # print(target +">>>" +str(parameter))

    motionPath = cmds.createNode("motionPath")
    cmds.setAttr(motionPath + ".fractionMode", 0)
    cmds.setAttr(motionPath + ".uValue", parameter)
    cmds.setAttr(motionPath + ".f" , False)
    cmds.connectAttr(curveOutput, motionPath + ".geometryPath")
    
    if parametric ==True:
        convertToParametricPoint(curve,motionPath)


    outputMatrix = cmds.createNode("composeMatrix")
    editAttrs.connectAttrZip(motionPath,outputMatrix,["allCoordinates","rotate"],["inputTranslate","inputRotate"])
    
    matrixDummy = cmds.createNode("transform")
    matrixDummyParent = addOffsetNode("transform",matrixDummy,"offset")
    editAttrs.connectAttrZip(motionPath,matrixDummy,["allCoordinates","rotate"],["translate","rotate"])
    multmatrix,outMatrix = matrixConstraint(matrixDummy,target,matrixDummyParent,targetParent,attrs,offset)
    attr = "matrix"
    output = cmds.listConnections(matrixDummy + "."+attr, d =True, s =False,p =True)
    
    if output != None:
        cmds.disconnectAttr(matrixDummy + "." + attr, output[0])
        cmds.connectAttr(outputMatrix + ".outputMatrix",output[0],f =True)

        for attr in ["offsetParentMatrix"]:
            output = cmds.listConnections(matrixDummy + "."+attr, d =True, s =False,p =True)
            cmds.disconnectAttr(matrixDummy + "." + attr, output[0])
            cmds.setAttr(output[0], *cmds.getAttr(matrixDummy+ "." + attr),type = "matrix")

    cmds.delete(matrixDummyParent)

    if cmds.objExists(target + ".parameter") == False:
        cmds.addAttr(target, ln = "parameter", at  ="double", k =True)

    cmds.setAttr(target + ".parameter", cmds.getAttr(motionPath + ".uValue"))
    cmds.connectAttr(target + ".parameter", motionPath + ".uValue")

    return motionPath



##Smooth-----------------------------------
def toPolySmooth(shape):    
    smoothDrawType = cmds.optionVar(q="globalPolyDefaultSmoothDrawType")
    subdivisionType = (0, 2, 3)[smoothDrawType]
    
    if cmds.getAttr(shape + ".useSmoothPreviewForRender"):
        smoothLevel = cmds.getAttr(shape + ".smoothLevel")
    else:
        smoothLevel = cmds.getAttr(shape + ".renderSmoothLevel")

    #Maya Catmull-Clark
    continuity = cmds.getAttr(shape + ".continuity")       
    boundaryRule = cmds.getAttr(shape + ".boundaryRule")  
    smoothUVs = cmds.getAttr(shape + ".smoothUVs")        
    propagateEdgeHardness = cmds.getAttr(shape + ".propagateEdgeHardness")    
    keepMapBorders = cmds.getAttr(shape + ".keepMapBorders")
    keepBorder = cmds.getAttr(shape + ".keepBorder")        
    keepHardEdge = cmds.getAttr(shape + ".keepHardEdge")    

    #OpenSubdiv
    osdVertBoundary = cmds.getAttr(shape + ".osdVertBoundary") 
    osdFvarBoundary = cmds.getAttr(shape + ".osdFvarBoundary") 
    osdFvarPropagateCorners = cmds.getAttr(shape + ".osdFvarPropagateCorners")  
    osdSmoothTriangles = cmds.getAttr(shape + ".osdSmoothTriangles")  
    osdCreaseMethod = cmds.getAttr(shape + ".osdCreaseMethod") 
    
    constructionHistory = True
    cmds.setAttr(shape + ".displaySmoothMesh", 0)
    

    smooths = cmds.polySmooth(shape, method = 0
                        , sdt = subdivisionType
                        , dv = smoothLevel
                        , c = continuity
                        , bnr = boundaryRule
                        , suv = smoothUVs
                        , peh = propagateEdgeHardness
                        , kmb = keepMapBorders
                        , kb = keepBorder
                        , khe = keepHardEdge
                        , ovb = osdVertBoundary
                        , ofb = osdFvarBoundary
                        , ofc = osdFvarPropagateCorners
                        , ost = osdSmoothTriangles
                        , ocr = osdCreaseMethod
                        #, ksb = True
                        #, kt = False
                        , ch = constructionHistory
                        ) or []

    cmds.select(cl =True)

    return smooths


def checkHierarchyVis(nodeLongName):    
    hierarchy = nodeLongName.split("|")
    show = True
    
    for i in range(1,len(hierarchy)):
        longName ="|"+ "|".join(hierarchy[1:i+1])


        if cmds.getAttr(longName + ".v") == 0:
            show = False
        
        if cmds.getAttr(longName + ".template") == 1:
            show = False
        
        if cmds.getAttr(longName + ".overrideEnabled"):
            if cmds.getAttr(longName + ".overrideDisplayType") == 1:
                show = False

            if cmds.getAttr(longName + ".overrideVisibility") == 0:
                show = False

        if show == False:
            break

    return show

def listVisibleMesh(topNode):
    shapes = cmds.listRelatives(topNode,ad = True, type = "mesh", f =True)

    showItems = []

    for shape in shapes:
        if cmds.getAttr(shape + ".intermediateObject"):
            continue

        nodeLongName = cmds.listRelatives(shape, p =True, f =True)[0]
        show = checkHierarchyVis(shape)

        if show:
            showItems.append(nodeLongName)
    
    return showItems

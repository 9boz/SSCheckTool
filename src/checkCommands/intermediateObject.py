from ..SPLib import editTransform
import maya.cmds as cmds

comment = "List the nodes that have intermediateObject"

def checkIntermediateObject(topNode = None):
    result = []

    shapes = cmds.ls(type = "shape",intermediateObjects =True,l = True) or []

    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)
        allHierarchy = cmds.listRelatives(topNode,ad =True,f=True) or []
        allHierarchy.append(topNode)
        shapes = list(set(shapes) & set(allHierarchy))

    result = editTransform.getTransformNode(shapes,True)
    
    return result

def removeIsolateIntermediateObject(targets):
    for node in targets:
        shapes = cmds.listRelatives(node,shapes = True,fullPath=True)

        for shape in shapes:
            if cmds.getAttr(shape + ".intermediateObject") == False:
                continue
            
            if cmds.listConnections(shape, d =True, s =True) == None:
                cmds.delete(shape)

##--------------------------------------------------------------------------------
def correct(correctTargets,**kwargs):
    
    removeIsolateIntermediateObject(correctTargets)

    return

def check(topNode,**kwargs):
    result = checkIntermediateObject(topNode)                  
    
    return result

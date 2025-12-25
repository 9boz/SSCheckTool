from ..SPLib import editTransform
import maya.cmds as cmds

comment = "List faceAssigned components"

import maya.api.OpenMaya as om

def checkFaceAssign(topNode =None):
    result = []

    nodeType = "shadingEngine"
    SGs = editTransform.listTypeNodes(nodeType,topNode = None, fullpath = False,ignorNodeTypes =[]) or []

    for SG in SGs:
        members = cmds.sets(SG,q = True) or []

        for member in members:
            parent = editTransform.getTransformNode([member],fullpath = False)
            if cmds.nodeType(parent) == "transform":
                continue
                
            hierarchy = editTransform.getCurHierarchy(member,fullpath = False)

            if topNode != None:
                if topNode in hierarchy:
                    result.append(member)
                    
            elif topNode == None:
                result.append(member)
                
    return result

##--------------------------------------------------------------------------------
# def correct(correctTargets,**kwargs):    

#     return 


def check(topNode,**kwargs):    
    
    result = checkFaceAssign(topNode)
                  
    return result


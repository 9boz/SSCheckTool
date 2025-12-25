from ..SPLib import editTransform
import maya.cmds as cmds

comment = "List any Assigned SG"

import maya.api.OpenMaya as om

def checkNonAssignSG(topNode =None):
    result = []

    nodeType = "shadingEngine"
    SGs = editTransform.listTypeNodes(nodeType,topNode = None, fullpath = False,ignorNodeTypes =[]) or []

    for SG in SGs:
        members = cmds.sets(SG,q = True) or []

        if len(members) == 0:
            result.append(SG)
                
    return result

##--------------------------------------------------------------------------------
# def correct(correctTargets,**kwargs):    

#     return 


def check(topNode,**kwargs):
    
    result = checkNonAssignSG(topNode)
                  
    return result


import maya.cmds as cmds
from ..SPLib import editTransform

comment = "list shape name  is not starts [transformnode]Shape"
##--------------------------------------------------------------------------------                

def correct(correctTargets,**kwargs):            
    
    for node in correctTargets:
        if editTransform.checkUniqueName(node) == False:
            continue

        shortName = editTransform.getShortName(node)
        shapes = cmds.listRelatives(node,shapes = True,fullPath=True)

        for shape in shapes:
            cmds.rename(shape, shortName + "Shape")

def check(topNode,**kwargs):

    nodeTypes = ["mesh","nurbsCurve","nurbsSurface"]

    result = []

    for nodeType in nodeTypes:
        allNodes = editTransform.listTypeNodes(nodeType,topNode = topNode,fullpath =True,ignorNodeTypes = [])

        for node in allNodes:
            shapes = cmds.listRelatives(node, type = "shape") or []
            
            nodeShortName = node.split("|")[-1]
            for shape in shapes:
                
                if shape.startswith(nodeShortName + "Shape") ==False:    
                    if node not in result:
                        result.append(node)
                        break

    return result
        

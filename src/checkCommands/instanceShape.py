import maya.cmds as cmds
from ..SPLib import editTransform,editAttrs
from .. import checkUtil
comment =  "list instanced shapes"
    
##--------------------------------------------------------------------------------                        
def correct(correctTargets,**kwargs):    
    
    for target in correctTargets:
        dup = cmds.duplicate(target)
        cmds.delete(target)
        cmds.rename(dup,target)

def check(topNode,**kwargs):

    nodeTypes = ["mesh","nurbsCurve","nurbsSurface"]

    result = []

    for nodeType in nodeTypes:
        allNodes = editTransform.listTypeNodes(nodeType,topNode = topNode,fullpath =True,ignorNodeTypes = [])
        
        for node in allNodes:
            shapes = cmds.listRelatives(node, type = "shape",fullPath=True) or []
            
            nodeShortName = node.split("|")[-1]
            for shape in shapes:
                parents = cmds.listRelatives(shape,allParents=True,fullPath=True)        
                
                if len(parents) > 1:
                    if node not in result:
                        result.append(node)
                        break

    return result        
import maya.cmds as cmds
from ..SPLib import editTransform

comment = "List the nodes that have colorSet"
        
##--------------------------------------------------------------------------------                
def correct(correctTargets,**kwargs):            
    for node in correctTargets:
        all_colorSet = cmds.polyColorSet(node,q=True,allColorSets=True)

        if all_colorSet == None:
            continue

        for colorSet in all_colorSet:
            cmds.polyColorSet(node,delete=True,colorSet=colorSet)


def check(topNode,**kwargs):
    result = []
    allNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True,ignorNodeTypes = [])

    for node in allNodes:
        all_colorSet = cmds.polyColorSet(node,q=True,allColorSets=True)
    
        if all_colorSet != None:
            if node not in result:
                result.append(node)

    return result
        

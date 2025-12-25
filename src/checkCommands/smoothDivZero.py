import maya.cmds as cmds
from ..SPLib import editTransform

comment = "list shape name  is smoothLv == 0"
##--------------------------------------------------------------------------------                

# def correct(correctTargets,**kwargs):            

#     for node in correctTargets:        
#         cmds.setAttr(node + ".keepHardEdge", True)


def check(topNode,**kwargs):

    nodeTypes = ["mesh"]

    result = []

    for nodeType in nodeTypes:
        allNodes = editTransform.listTypeNodes(nodeType,topNode = topNode,fullpath =True,ignorNodeTypes = [])

        for node in allNodes:
            if cmds.objExists(node + ".smoothLevel") == False:
                continue

            smoothLevel = cmds.getAttr(node + ".smoothLevel")

            if smoothLevel == 0:
                result.append(node)
            

    return result
        

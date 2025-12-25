import maya.cmds as cmds
from ..SPLib import editTransform

comment = "list shape name  is not starts [transformnode]Shape"
##--------------------------------------------------------------------------------                

def correct(correctTargets,**kwargs):            

    for node in correctTargets:        
        cmds.setAttr(node + ".keepHardEdge", True)


def check(topNode,**kwargs):

    nodeTypes = ["mesh"]

    result = []

    for nodeType in nodeTypes:
        allNodes = editTransform.listTypeNodes(nodeType,topNode = topNode,fullpath =True,ignorNodeTypes = [])

        for node in allNodes:
            if cmds.objExists(node + ".keepHardEdge") == False:
                continue

            keepHardEdge = cmds.getAttr(node + ".keepHardEdge")

            if keepHardEdge == False:
                result.append(node)
            

    return result
        

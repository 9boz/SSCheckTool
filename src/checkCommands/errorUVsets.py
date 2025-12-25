import maya.cmds as cmds
from ..SPLib import editTransform
comment =  "List Nodes that have nullName UV sets"
                
##--------------------------------------------------------------------------------                
        
def correct(correctTargets,**kwargs):
    for node in correctTargets:
        if cmds.objExists(node  + ".uvSet") == False:
            continue

        uvIndex = cmds.getAttr(node  + ".uvSet", mi =True)
        
        if uvIndex == None:
            continue

        for index in uvIndex:
            uvSetName  = cmds.getAttr(node  + ".uvSet["+str(index)+"].uvSetName")
            uvPointIndex = cmds.getAttr(node  + ".uvSet["+str(index)+"].uvSetPoints",mi =True)

            if uvSetName == None and uvPointIndex != None:
                cmds.setAttr(node + ".uvSet["+str(index)+"].uvSetName", "uvSet"+str(index) + "_reborn", type = "string")
                cmds.polyUVSet(node ,uvSet = "uvSet"+str(index) +"_reborn",delete=True)

    return

def check(topNode,**kwargs):

    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    allMeshNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True)

    result = []

    for node in allMeshNodes:
        if cmds.objExists(node  + ".uvSet") == False:
            continue

        uvIndex = cmds.getAttr(node  + ".uvSet", mi =True)
        
        if uvIndex == None:
            continue

        for index in uvIndex:
            uvSetName  = cmds.getAttr(node  + ".uvSet["+str(index)+"].uvSetName")
            uvPointIndex = cmds.getAttr(node  + ".uvSet["+str(index)+"].uvSetPoints",mi =True)

            if uvSetName == None and uvPointIndex != None:
                if node not in result:
                    result.append(node)

    return result




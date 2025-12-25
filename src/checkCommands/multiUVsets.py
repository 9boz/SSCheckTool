import maya.cmds as cmds
from ..SPLib import editTransform
comment =  "List Nodes that have multiple UV sets"

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

            elif index != 0 and uvSetName != "map1":
                cmds.polyUVSet(node ,uvSet = uvSetName,delete=True)

    return



def check(topNode,**kwargs):
    result = []
    needs = []
    ignors = []

    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    allMeshNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True)

    for node in allMeshNodes:
        uvInfo = editTransform.listUVsets(node)

        uvSetNames = []
        for infoDict in uvInfo:
            uvSetNames.append(infoDict["uvSetName"])

        uvSetNames = list(set(uvSetNames) - set(ignors))
        needCheck = list(set(needs) - set(uvSetNames))

        if len(needCheck) != 0:
            result.append(node)
            continue

        if len(uvSetNames) > 1:
            result.append(node)
            continue

    return result



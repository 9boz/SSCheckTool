import maya.cmds as cmds
from ..SPLib import editTransform

comment = "List Nodes with defaultUVsetName != map1"


##--------------------------------------------------------------------------------
def correct(correctTargets,**kwargs):        

    for target in correctTargets:

        all_uvSet = cmds.polyUVSet(target,q=True,allUVSets=True)
        if all_uvSet == None:
            return

        if "map1" not in all_uvSet:
            cmds.polyUVSet(target,rename=True, newUVSet = "map1", uvSet= all_uvSet[0])

    return 


def check(topNode,**kwargs):
    result = []

    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    allMeshNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True)

    for node in allMeshNodes:
        uvInfo = editTransform.listUVsets(node)
        
        if len(uvInfo) == 0:
            result.append(node)
            continue

        elif uvInfo[0]["uvSetName"] != "map1":
            result.append(node)
            continue

    return result

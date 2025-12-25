import maya.cmds as cmds
from ..SPLib import editTransform
comment = "list sameName nodes"

##--------------------------------------------------------------------------------                            
# def correct(correctTargets,**kwargs):
        
#     return None

def check(topNode,**kwargs):
    result = []
    
    defaultNodes = cmds.ls(defaultNodes =True)
    allNodes = cmds.ls(dagObjects =True,l=True)
    allNodes = list(set(allNodes) - set(defaultNodes))

    shortNameDict = {}

    for node in allNodes:
        # if editTransform.checkUniqueName(node):
        #     continue

        shortName = editTransform.getShortName(node).lower()

        if shortName not in list(shortNameDict.keys()):
            shortNameDict[shortName] = [node]
        else:
            shortNameDict[shortName].append(node)

    for shortName in list(shortNameDict.keys()):
        if len(shortNameDict[shortName]) > 1:
            result.extend(shortNameDict[shortName])

    return result
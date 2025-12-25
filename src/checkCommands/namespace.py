import maya.cmds as cmds

comment = "List namespace in this scene"

##--------------------------------------------------------------------------------                

def correct(correctTargets,**kwargs):                
    return None

def check(topNode,**kwargs):

    ignorList = ['UI', 'shared']
    result = []

    allNameSpace = cmds.namespaceInfo(listOnlyNamespaces = True)
    result = list(set(allNameSpace) - set(ignorList))

    return result
    
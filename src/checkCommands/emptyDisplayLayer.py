import maya.cmds as cmds
from ..SPLib import editTransform,editScenes

comment = "list displayLayers(empty) in this scene"                

##--------------------------------------------------------------------------------                

def correct(correctTargets,**kwargs):            
    editScenes.removeDisplayLayer(emptyOnly = True)

def check(topNode,**kwargs):
    result = []

    ignors = ["defaultLayer"]
    allNodes = editTransform.listTypeNodes("displayLayer",topNode = None,fullpath =True)
    allNodes = list(set(allNodes) - set(ignors))
    
    for layer in allNodes:
        if cmds.editDisplayLayerMembers(layer,q =True) == None:
            result.append(layer)

    return result
        

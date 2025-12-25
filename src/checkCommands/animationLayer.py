import maya.cmds as cmds
from ..SPLib import editTransform

comment = "list animationLayers in this scene"
        
##--------------------------------------------------------------------------------                

def correct(correctTargets,**kwargs):            
    cmds.delete(correctTargets)


def check(topNode,**kwargs):
    result = []

    ignors = ["defaultLayer"]
    allNodes = editTransform.listTypeNodes("animLayer",topNode = None,fullpath =True)
    result = list(set(allNodes) - set(ignors))
        
    return result
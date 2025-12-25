import maya.cmds as cmds
from ..SPLib import editTransform,editScenes

comment = "List animationCurve node"

##--------------------------------------------------------------------------------                
        
# def correct(correctTargets,**kwargs):
#     return


def check(topNode,**kwargs):
    return cmds.ls(type = 'animCurve') or []

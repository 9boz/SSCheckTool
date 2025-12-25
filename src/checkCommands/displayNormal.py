import maya.cmds as cmds
from ..SPLib import editTransform,editAttrs
from .. import checkUtil
comment =  "list displaynormal mesh in this scene"
    
##--------------------------------------------------------------------------------                        
def correct(correctTargets,**kwargs):
    editAttrs.setAttrNodes(correctTargets,{"displayNormal":0},True)

def check(topNode,**kwargs):
    result = checkUtil.checkParam(topNode,['mesh'],attrs = [{'attrName':'displayNormal','value':0,'equal':'!='}])
    return result



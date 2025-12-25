import maya.cmds as cmds
from ..SPLib import editTransform,editAttrs
from .. import checkUtil
comment =  "list  t,r,s,v locked nodes"
    
##--------------------------------------------------------------------------------                        
def correct(correctTargets,**kwargs):
    
    attrs = ["t","r","s","v"]
    for node in correctTargets:

        for attr in attrs:
            targetAttrs = editAttrs.getFlattenAttr(node,attr)
            targetAttrs.append(attr)
                
            for targetAttr in targetAttrs:
                if cmds.objExists(node + "."+targetAttr) ==False:
                        continue

                cmds.setAttr(node + "." + targetAttr, l =False)

def check(topNode,**kwargs):
    result = checkUtil.checkLockedParam(topNode,["transform"],[],["t","r","s","v"])
    return result        
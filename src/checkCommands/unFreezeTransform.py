import maya.cmds as cmds
from ..SPLib import editTransform,editScenes
from .. import checkUtil
comment = "List transformNodes with \ntranslate != [0.0,0.0,0.0] \nrotate != [0.0,0.0,0.0] \nscale != [1.0,1.0,1.0]"

##--------------------------------------------------------------------------------                

def correct(correctTargets,**kwargs):                
    cmds.makeIdentity(correctTargets, a =True,t =True, r=True, s =True,preserveNormals=True)

def check(topNode,**kwargs):

    
    result = checkUtil.checkParam(
                                topNode,
                                ['transform'],
                                ['joint','light','camera'],
                                attrs = [
                                        {'attrName':'translate','value':[0.0,0.0,0.0],'equal':'!='},
                                        {'attrName':'rotate','value':[0.0,0.0,0.0],'equal':'!='},
                                        {'attrName':'scale','value':[1.0,1.0,1.0],'equal':'!='}
                                        ]                                        
                                )
    
    return result
    
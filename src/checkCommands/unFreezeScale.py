import maya.cmds as cmds
from .. import checkUtil

comment = "List transformNodes with scale != [1.0,1.0,1.0]"

##--------------------------------------------------------------------------------
def correct(correctTargets,**kwargs):        
    cmds.makeIdentity(correctTargets, a =True, s =True,preserveNormals=True)

    return 


def check(topNode,**kwargs):    
    
    result = checkUtil.checkParam(
                                topNode,
                                ['transform'],
                                ['joint','light','camera'],
                                attrs = [{'attrName':'scale','value':[1.0,1.0,1.0],'equal':'!='}]
                                )
                  
    return result

import maya.cmds as cmds

comment = "list dataStructure in this scene"
        
##--------------------------------------------------------------------------------

def correct(correctTargets,**kwargs):            
    cmds.dataStructure(removeAll=True)
    return 


def check(topNode,**kwargs):
    return cmds.dataStructure(query=True) or []
        

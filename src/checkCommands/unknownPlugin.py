import maya.cmds as cmds

comment = "list unknownPlugin in this scene"

##--------------------------------------------------------------------------------                
        
def correct(correctTargets,**kwargs):

    plugins = cmds.unknownPlugin(query = True, list =True) or []

    for plugin in plugins:
        cmds.unknownPlugin(plugin,r =True)

    return


def check(topNode,**kwargs):
    return cmds.unknownPlugin(query = True, list =True) or []

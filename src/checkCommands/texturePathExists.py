import maya.cmds as cmds
from ..SPLib import editTransform,editScenes
comment =  "List Nodes that donotExists filePath"
                
##--------------------------------------------------------------------------------                
        
# def correct(correctTargets,**kwargs):
#     return

def check(**kwargs):

    fileDict = editScenes.getAllFileNodeInfo("file",[]) 
    
    result = []

    for key in list(fileDict.keys()):
        
        if fileDict[key]["exists"] == False:
            result.extend(fileDict[key]["node"])


    return result




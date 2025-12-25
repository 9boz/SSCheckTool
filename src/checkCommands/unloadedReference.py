import maya.cmds as cmds


comment = "list unloaded reference in cut scene"


##--------------------------------------------------------------------------------                
           
# def correct(correctTargets,**kwargs):
#     return

def check(topNode,**kwargs):        
    result = []
    
    allRefFiles = cmds.file(q =True ,reference =True)
    
    for refFile in allRefFiles:
        refNode = cmds.file(refFile,q =True ,referenceNode = True)

        load = cmds.referenceQuery(refNode,isLoaded=True)

        if load == False:
            result.append(refNode)
    

    return result

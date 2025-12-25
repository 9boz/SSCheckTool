from ..SPLib import editTransform
import maya.cmds as cmds

comment = "List the nodes that have lockedNormal"

def checkLockedNormal(topNode =None):
    result = []

    allNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True,ignorNodeTypes = [])    

    for node in allNodes:
        vtxs = cmds.ls(node + ".vtx[*]",fl =True)
        
        for vtx in vtxs:
            if cmds.polyNormalPerVertex(vtx, q =True , al =True)[0] == True:
                if node not in result:
                    result.append(node)
                break
    
    return result

##--------------------------------------------------------------------------------
# def correct(correctTargets,**kwargs):    

#     return 


def check(topNode,**kwargs):    
    
    result = checkLockedNormal(topNode)
                  
    return result

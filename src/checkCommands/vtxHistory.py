import maya.cmds as cmds
from ..SPLib import editTransform,editAttrs
from .. import checkUtil
comment =  "list nodes have vtxPntValues"
    
##--------------------------------------------------------------------------------                        

def listVtxPntNodes(topNode =None):
    result = []

    allNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True,ignorNodeTypes = [])    

    for node in allNodes:        
        shapes = cmds.listRelatives(node, type = "mesh")
        
        if shapes == None:
            continue
        
        vtxs = cmds.ls(node + ".vtx[*]", fl = True)

        for i in range(0,len(vtxs)):
            values = cmds.getAttr(node + ".pnts["+str(i)+"]")[0]
            values = [round(values[0],5),round(values[1],5),round(values[2],5)]
            
            if values.count(0.0) != 3:                
                result.append(node)
                break
    
    return result

def correct(correctTargets,**kwargs):    
    
    for target in correctTargets:
        vtxs = cmds.ls(target + ".vtx[*]", fl = True)
        cmds.polyMoveVertex(vtxs,ch =False)



def check(topNode,**kwargs):

    result = []
    result = listVtxPntNodes(topNode)
    
    return result        
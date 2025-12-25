import maya.cmds as cmds
from ..SPLib import editTransform
import maya.api.OpenMaya as om

comment =  "List UVmap , do not belong any shells"

##--------------------------------------------------------------------------------                        

def getUVShellInfo(target,uvSet):
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)
    uvShellIds = shape_Fn.getUvShellsIds(uvSet)
    
    shells = {}
    for i, n in enumerate(uvShellIds[1]):

        if n in shells:
            shells[n].append(i)
        else:
            shells[n] = [i]

    result = []
    
    if -1 in list(shells.keys()):
        for i in shells[-1]:
            result.append(target + ".map["+str(i)+"]")
    
    if len(result) != 0:
        cmds.select(result,r=True)
        result = cmds.ls(sl =True)
        cmds.select(cl=True)

    return result

##-------------------------------------------------------------------------------------
def correct(correctTargets,**kwargs):
    
    for node in correctTargets:
        allUVsetName = cmds.polyUVSet(node,query=True, allUVSets=True)
        
        for uvSetName in allUVsetName:            
            UVmaps = getUVShellInfo(node,uvSetName)

            if len(UVmaps):
                cmds.polyUVSet(node, currentUVSet=True,  uvSet=uvSetName)
                cmds.polyMergeUV(node + ".map[0]",ch =False)

    
        cmds.polyUVSet( currentUVSet=True,  uvSet="map1")
    return

def check(topNode,**kwargs):
    result = []
    
    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    allMeshNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True)

    for node in allMeshNodes:        
        allUVsetName = cmds.polyUVSet(node,query=True, allUVSets=True)
        for uvSetName in allUVsetName:            
            UVmaps = getUVShellInfo(node,uvSetName)

            if len(UVmaps) and node not in result:
                result.append(node)
                
    return result



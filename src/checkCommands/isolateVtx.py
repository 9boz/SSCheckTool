import maya.cmds as cmds
from ..SPLib import editTransform

comment = "list unloaded reference in cut scene"

import maya.api.OpenMaya as om


def listIsolateVtx(target):
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)

    face_ids = range(0,shape_Fn.numPolygons)
    it = om.MItMeshPolygon(mesh_dagPath)

    all_faceVtx_ids = []
    for index in face_ids:
        it.setIndex(index)
        connected_vtx = it.getVertices()
        all_faceVtx_ids.extend(list(connected_vtx)) 

    all_faceVtx_ids = list(set(all_faceVtx_ids))

    all_vtx_ids = []    
    for i in range(0,shape_Fn.numVertices):
        all_vtx_ids.append(i)

    isolate_vtx_ids = list(set(all_vtx_ids) - set(all_faceVtx_ids))

    if len(isolate_vtx_ids) != 0:
        return False
    
    return True

##--------------------------------------------------------------------------------                
           
# def correct(correctTargets,**kwargs):
#     return

def check(topNode,**kwargs):        
    result = []
    
    allNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True,ignorNodeTypes = [])    

    for node in allNodes:
        if listIsolateVtx(node) == False:
            result.append(node)
    

    return result

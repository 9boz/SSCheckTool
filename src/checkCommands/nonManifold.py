from ..SPLib import editTransform
import maya.cmds as cmds

comment = "List NonManifold components"

import maya.api.OpenMaya as om


def listDoubleEdge(target):
    vtxIds = []
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)

    face_ids = range(0,shape_Fn.numPolygons)
    it = om.MItMeshPolygon(mesh_dagPath)
    
    for index in face_ids:
        it.setIndex(index)
        vtxs = it.getVertices()
        connectedVtx = it.getConnectedVertices()

        commons = list(set(vtxs) & set(connectedVtx))
        if len(commons):
            vtxIds = list(set(vtxIds) | set(commons))
              
    result = [target + '.vtx[' + str(vid) + ']'for vid in vtxIds]

    return result

def checkNonManifolds(topNode =None):
    result = []

    allNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True,ignorNodeTypes = [])    


    for node in allNodes:
        
        edges = cmds.polyInfo(node,nonManifoldEdges =True) or []

        if len(edges) != 0:
            result = list(set(result) | set(edges))

        vtxs = cmds.polyInfo(node,nonManifoldVertices =True) or []

        if len(vtxs) != 0:
            result = list(set(result) | set(vtxs))
    
        doubleEdgeVtx = listDoubleEdge(node)

        if len(doubleEdgeVtx) != 0:
            result = list(set(result) | set(doubleEdgeVtx))

    return result

##--------------------------------------------------------------------------------
# def correct(correctTargets,**kwargs):    

#     return 


def check(topNode,**kwargs):    
    
    result = checkNonManifolds(topNode)
                  
    return result


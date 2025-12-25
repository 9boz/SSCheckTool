import maya.cmds as cmds
from ..SPLib import editTransform
import maya.api.OpenMaya as om

comment =  "List face , outside UV Range 0,0-1,1"

##--------------------------------------------------------------------------------                        

def findUVRangeFace(target,uvSet,UVRange):
    faceIds = []
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)
    face_ids = range(0,shape_Fn.numPolygons)
    it = om.MItMeshPolygon(mesh_dagPath)

    for index in face_ids:
        it.setIndex(index)

        try:
            ## cnat find UV
            uvs = it.getUVs(uvSet)
            
        except:
            faceIds.append(index)
            continue
        
        
        insideRange = True
        for uPoint in uvs[0]:
            if uPoint < UVRange[0] or  uPoint > UVRange[1]:
                insideRange = False
                        
        for vPoint in uvs[1]:
            if vPoint < UVRange[2] or  vPoint > UVRange[3]:
                insideRange = False
                           
        if insideRange == False:
            faceIds.append(index)

    result = []
    for faceId in faceIds:
        result.append(target+".f["+str(faceId)+"]")
        
    return result

##------------------------------------------------------------------
# def correct(correctTargets,**kwargs):

#     return



def check(topNode,**kwargs):
    result = []
    
    if topNode != None:
        topNode = editTransform.getFullPathName(topNode)

    allMeshNodes = editTransform.listTypeNodes("mesh",topNode = topNode,fullpath =True)

    for node in allMeshNodes:
        faces = findUVRangeFace(node,"map1",[0.0,1.0,0.0,1.0])

        if len(faces):
            result.extend(faces)


    return result



import maya.cmds as cmds
from ..SPLib import editTransform
import maya.api.OpenMaya as om

comment =  "List face , outside UV Range 0.2 span"


def getUVRangeIndex(target,uvSet,span):
    
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)
    face_ids = range(0,shape_Fn.numPolygons)
    it = om.MItMeshPolygon(mesh_dagPath)

    faceDict = {}

    for index in face_ids:
        it.setIndex(index)
        
        try:            
            uvs = it.getUVs(uvSet)
            
        except:
            faceDict[index] = []
            continue
        
        rangeIndex = []    

        for uPoint,vPoint in zip(uvs[0],uvs[1]):
            uIndex = int((uPoint // span ))            
            vIndex = int((vPoint // span ))

            UVIndex = str(uIndex) + "_" +str(vIndex)
            
            if UVIndex not in rangeIndex:
                rangeIndex.append(UVIndex)

        faceDict[index] = rangeIndex

    return faceDict

def checkOverUVGridBorder(targets,uvDist):

    result = []    

    for target in targets:
        faceDict = getUVRangeIndex(target,"map1",uvDist)

        for faceId in list(faceDict.keys()):
            
            if len(faceDict[faceId]) == 0:
                result.append(target+".f["+str(faceId)+"]")

            elif len(faceDict[faceId]) > 1:
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
    
    result = checkOverUVGridBorder(allMeshNodes,0.2)
    

    return result



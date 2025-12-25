from __future__ import (absolute_import, division,print_function)
import os
import shutil
import sys
import subprocess
import pathlib
import glob

from . import editString,editFiles

mayaVer = None
executable = sys.executable
if executable.endswith("maya.exe") or executable.endswith("mayabatch.exe"):
    import maya.cmds as cmds
    import maya.mel as mel
    import maya.api.OpenMayaUI as omui
    import maya.api.OpenMaya as om
    import maya.OpenMaya
    import maya.OpenMayaUI as OpenMayaUI

    mayaVer = cmds.about(version=True)

##---------------------------------------------
def saveDictOptionVar(toolName,optionDict):
    optionString= ""

    for key in optionDict:
        if optionString != "":
            optionString += ";"
        
        if mayaVer in ["2020","2019"] and type(optionDict[key]) == unicode:
            optionString += key + ";" + optionDict[key]
        else:
            optionString += key + ";" + str(optionDict[key])

    cmds.optionVar(stringValue = [toolName,optionString])

def readDictOptionVar(toolName):
    optionString = ""
    if cmds.optionVar(exists = toolName):            
        optionString = cmds.optionVar(q = toolName)
    
    optionDict = {}

    optionArray = optionString.split(";")
    if len(optionArray) > 1:
        for i in range(0,len(optionArray),2):
            optionDict[optionArray[i]] = optionArray[i+1]

    return optionDict

##---------------------------------------------
##scene
##---------------------------------------------
def createNewScene(force = True):
    
    cmds.file(new=True,f=force)

    ##remove unknown plugin
    removeUnknownPlugin()

    ##remove namespace
    removeNamespace()
    clearUIcommand()
    closeNodeEditor()
    closeGraphEditor()


def removeUnknownPlugin():
    plugins = cmds.unknownPlugin(query = True, list =True) or []

    for plugin in plugins:
        cmds.unknownPlugin(plugin,r =True)

    return

def removeNamespace():
    existsNamespace = listNameSpace()
    for namespace in existsNamespace:
        try:
            cmds.namespace(removeNamespace = namespace)
        except:
            pass

def listUIPanels(UItype):
    uiItems = []

    if UItype == "outlinerPanel":    
        for panel in cmds.lsUI(panels = True) or []:
            if cmds.outlinerEditor(panel, q =True, exists = True):
                uiItems.append(panel)

    elif UItype == "modelEditor":
        for panel in cmds.lsUI(editors = True) or []:
            if cmds.modelEditor(panel, q =True, exists = True):
                uiItems.append(panel)
                
    return uiItems

def clearUIcommand(types = ["outlinerPanel","modelEditor"]):
    for UItype in types:
        ui_panels = listUIPanels(UItype)

        for ui_panel in ui_panels:
            if UItype == "outlinerPanel":
                if cmds.outlinerEditor(ui_panel, q =True, selectCommand = True) != None:                    
                    mel.eval('outlinerEditor -e -selectCommand "" '+ ui_panel)

            elif UItype == "modelEditor":
                if cmds.modelEditor(ui_panel, q =True, editorChanged = True) != None:                    
                    mel.eval('modelEditor -e -editorChanged "" '+ ui_panel)

def closeNodeEditor():
    if cmds.workspaceControl("nodeEditorPanel1Window",ex =True):
        cmds.workspaceControl("nodeEditorPanel1Window",e =True, close = True)


def closeGraphEditor():
    if cmds.workspaceControl("graphEditor1Window",ex =True):
        cmds.workspaceControl("graphEditor1Window",e =True, close = True)


def getFrameRate():
    unitDict = {
                    'game':15,
                    'film': 24,
                    'pal':  25,
                    'ntsc': 30,
                    'show': 48,
                    'palf': 50,
                    'ntscf':60        
                }
    
    unit = cmds.currentUnit(q=True, t=True)

    if unit in unitDict.keys():
        fps =  unitDict[unit]
    else:
        temp = unit.replace('fps', '')
        fps  = int(temp)

    return fps
##---------------------------------------------
##workspace
##---------------------------------------------
def workspaceExists(path,workspaceType = "public"):
    if os.path.exists(path + "workspace.mel"):
        return True

    workspace_dict = {}
    if workspaceType == "default":        
        fileRules = mel.eval("np_getDefaultFileRuleWidgets")

        for i in range(0,len(fileRules),2):
            workspace_dict[fileRules[i]] = fileRules[i+1]

    cmds.workspace(directory = path)

    for key in workspace_dict.keys():
        cmds.workspace(fileRule = [key,workspace_dict[key]])
        if workspace_dict[key] != "":
            cmds.workspace(create = workspace_dict[key])

def setMayaProject(projectPath,workspaceType = "default"):
    workspaceExists(projectPath,workspaceType)
    cmds.workspace(projectPath, openWorkspace =True)
    cmds.workspace(saveWorkspace = True)
    
##---------------------------------------------
##namespace
##---------------------------------------------
def listNameSpace(asReference=False):
    allNameSpace = []

    if asReference:
        allRefFiles = cmds.file(q =True ,reference =True)
        for refFile in allRefFiles:
            allNameSpace.append(cmds.file(refFile,q =True ,namespace = True))

    else:
        ignorList = ['UI', 'shared']
        allNameSpace = cmds.namespaceInfo(listOnlyNamespaces = True,recurse =True)
        allNameSpace = list(set(allNameSpace) - set(ignorList))

    return allNameSpace

def removeNonReferenceNamespace():
    referenceNamespace = listNameSpace(asReference=True)
    allNamespace = listNameSpace(asReference=False)

    for namespace in allNamespace:
        if namespace in referenceNamespace:
            continue

        if cmds.namespace(exists =namespace) == False:
            continue
            
        cmds.namespace(collapseAncestors = namespace)

        if cmds.namespace(exists =namespace) == False:
            continue
                
        cmds.namespace(removeNamespace = namespace,mergeNamespaceWithRoot = True)

def organizeNamespace(namespace,correctNamespace,force =False):    
    allNameSpace = listNameSpace(True)
    refNode = getReferenceNode(namespace)

    if refNode == None:
        return namespace

    correctNamespaceSample = correctNamespace + "(?P<INCREMENT>[0-9]*)"
    
    renameNamespace = str(correctNamespace)
    
    if namespace != renameNamespace:
        namespaceParts = editString.stringToDict(
                                namespace,
                                correctNamespaceSample,
                                renameNamespace + "{INCREMENT}",
                                orNone = False
                                
                                )
        
        if namespaceParts["INCREMENT"] == "" or force:
            i = 1
                    
            while renameNamespace in allNameSpace:
                renameNamespace = correctNamespace + str(i)
                i = i+1
        
            cmds.namespace(rename = [namespace,renameNamespace])
            namespace = renameNamespace

    if  refNode.startswith(namespace + "RN") == False:
        cmds.lockNode(refNode,lock = False)
        refNode = cmds.rename(refNode,namespace + "RN")
        cmds.lockNode(refNode,lock = True)
    
    return renameNamespace

def organizeRefNodes():
    allRefFiles = cmds.file(q =True ,reference =True)
    
    for refFile in allRefFiles:
        refNode = cmds.file(refFile,q =True ,referenceNode = True)
        namespace = cmds.file(refFile,q =True ,namespace = True)
                
        cmds.lockNode(refNode,lock = False)
        refNode = cmds.rename(refNode,namespace + "RN")
        cmds.lockNode(refNode,lock = True)

def getReferenceNode(namespace):
    allRefFiles = cmds.file(q =True ,reference =True)
    
    for refFile in allRefFiles:
        refNode = cmds.file(refFile,q =True ,referenceNode = True)
        
        if namespace == cmds.file(refFile,q =True ,namespace = True):
            return refNode

    return None

def getReferenceFilePath(namespace,withoutCopyNumber =True):
    refNode = getReferenceNode(namespace)
    
    if refNode == None:
        return ""

    filePath = cmds.referenceQuery(refNode,filename=True,withoutCopyNumber =withoutCopyNumber)
    return filePath

def nodeIsReference(node):
    namespace = node.split(":")[0]    
    refNode = getReferenceNode(namespace)
    
    if refNode == None:
        return False
    
    nodes = cmds.referenceQuery(refNode,nodes =True)
    
    if node not in nodes:
        return False
        
    else:
        return True
        
def setFrameRange(startFrame,endFrame,rangetarget):    
    if rangetarget == "animation":
        start = cmds.playbackOptions(animationStartTime=startFrame)
        end = cmds.playbackOptions(animationEndTime=endFrame)

    elif rangetarget == "timeSlider":
        start = cmds.playbackOptions(minTime=startFrame)
        end = cmds.playbackOptions(maxTime=endFrame)

    cmds.setAttr("defaultRenderGlobals.startFrame",startFrame)
    cmds.setAttr("defaultRenderGlobals.endFrame",endFrame)


def getFrameRange(rangeFrom):

    start = 1
    end = 100

    if rangeFrom == "animation":
        start = cmds.playbackOptions(q =True, animationStartTime=True)
        end = cmds.playbackOptions(q =True, animationEndTime=True)

    elif rangeFrom == "timeSlider":
        start = cmds.playbackOptions(q =True, minTime=True)
        end = cmds.playbackOptions(q =True, maxTime=True)

    elif rangeFrom == "renderSetting":
        start = cmds.getAttr("defaultRenderGlobals.startFrame")
        end = cmds.getAttr("defaultRenderGlobals.endFrame")

    elif rangeFrom == "selection":
        aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
        s_e = cmds.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)
        start = s_e[0]
        end = s_e[1]

    return start,end


def removeDisplayLayer(emptyOnly = True):
    layers = cmds.ls(type = "displayLayer") or []
    for layer in layers:

        if emptyOnly:
            if cmds.editDisplayLayerMembers(layer,q =True) == None:
                cmds.delete(layer)

        else:
            cmds.delete(layer)

def getDisplayLayerDict():
    displayLayers = cmds.ls(type = "displayLayer")
    layerDict = {}

    for layer in displayLayers:
        if layer == "defaultLayer":
            continue
            
        members = cmds.editDisplayLayerMembers(layer,q =True) or []
        
        layerDict[layer] = members

    return layerDict

def crateDisplayLayerFromDict(layerDict):
        
    for layer in list(layerDict.keys()):
        if cmds.objExists(layer) == False:
            cmds.createDisplayLayer(empty =True,name = layer)
        
        for member in layerDict[layer]:
            if cmds.objExists(member) == False:
                continue

            cmds.editDisplayLayerMembers(layer,member,noRecurse=True)
                            

##-----------------------------------------------
##maya file
##-----------------------------------------------
fileTypeDict = {
    "ma":       "mayaAscii",
    "mb":       "mayaBinary",
    "editMA":   "editMA",
    "fbx":      "fbx",
    "FBX":      "fbx",
    "stl":      "STLExport",
    "obj":      "OBJexport"
}

def extToFileType(fileName):    
    ext = fileName.split(".")[-1]
    return fileTypeDict[ext]

def checkNeedSave():
    fileCheckState = cmds.file(q=True, modified=True)
    curOpen = cmds.file(q=True, sn=True)

    if curOpen == "":
        curOpen = "untitled"

    if fileCheckState:
        mel.eval("checkForUnknownNodes();")
        saved = mel.eval("saveChanges(\"\");")

        if saved == 0:
            return False

    return True

def getCurSceneName(fullPath = None):

    if fullPath == None:
        fullPath = cmds.file(q=True, sn=True)
        
    fileName = os.path.basename(fullPath)
    filePath = os.path.dirname(fullPath)

    if filePath != "":
        filePath += "/"
        
    fileNameBody, extension = os.path.splitext(fileName)
    
    return filePath,fileNameBody,extension

def openFile(filePath,fileName,openBy,force =False):    
    if openBy == "maya":
        filetype = extToFileType(fileName)

        if force:
            cmds.file(
                        filePath + fileName,
                        f =True,
                        open = True,
                        options = 'v=0;',
                        type = filetype                
                    )

            removeUnknownPlugin()            
            clearUIcommand()            
            return

        elif checkNeedSave():
            cmds.file(
                        filePath + fileName,
                        f =True,
                        open = True,
                        options = 'v=0;',
                        type = filetype                
                    )

            removeUnknownPlugin()            
            clearUIcommand()            

    elif openBy == "os":
        filePath = filePath.replace("/",os.path.sep)

        if mayaVer in ["2020","2019"]:
            path = filePath.encode("mbcs") + fileName.encode("mbcs")
            
        else:
            path = filePath + fileName
            
        subprocess.Popen([path], shell=True)

def importFile(filePath,fileName,addOption = {},renamingPrefix = None, renameAll = False):
    filetype = extToFileType(fileName)    
    curTopNodes = set(cmds.ls(assemblies =True))

    if renamingPrefix == None:
        renamingPrefix = fileName.split(".")[0]

    cmds.file(
            filePath + fileName,
            i = True,            
            type = filetype,
            options = 'v=0;',
            renameAll = renameAll,
            renamingPrefix= renamingPrefix,
            mergeNamespacesOnClash = False,
            **addOption
        )
    
    # if renameAll == False:
    #     cmds.namespace(removeNamespace = renamingPrefix,mergeNamespaceWithRoot =True)

    distTopNodes = set(cmds.ls(assemblies =True))	
    addTopNodes = list(distTopNodes - curTopNodes)

    return addTopNodes

def referenceFile(filePath,fileName,namespace,mergeNamespaces =False):
    if filePath == None or fileName == None:
        return None
    
    if not filePath.endswith("/") and filePath != "":
        filePath = filePath + "/"

    if namespace.endswith(":"):
        namespace = namespace[0:-1]
    
    elif namespace == "":
        namespace = ":"

    file = cmds.file(
                        filePath + fileName,
                        r =True ,
                        options = 'v=0;', 
                        namespace = namespace,
                        mergeNamespacesOnClash = mergeNamespaces,
                        loadReferenceDepth = "topOnly",
                        groupReference =False,
                        lockReference = False,
                        deferReference =False
                        )
    
    outNamespace = cmds.file(file,q =True ,namespace = True)

    refNode = getReferenceNode(outNamespace)
    if  refNode != outNamespace + "RN":
        cmds.lockNode(refNode,lock = False)
        refNode = cmds.rename(refNode,outNamespace + "RN")
        cmds.lockNode(refNode,lock = True)

    return outNamespace

def removeReference(nameSpace):
    filePath = getReferenceFilePath(nameSpace,False)
    cmds.file(filePath,removeReference = True)


def replaceReferenceFile(filePath,fileName,namespace):
    refNode = getReferenceNode(namespace)

    if not filePath.endswith("/") and filePath != "":
        filePath = filePath + "/"

    if namespace.endswith(":"):
        namespace = namespace[0:-1]

    if os.path.exists(filePath+fileName):
        cmds.file(filePath+fileName,lr = refNode)

def referenceEditMA(filePath,fileName,namespace,asMain,mapPlaceHolderNamespace = []):
    if not filePath.endswith("/") and filePath != "":
        filePath = filePath + "/"

    if namespace.endswith(":"):
        namespace = namespace[0:-1]

    applyTo = getReferenceNode(asMain)
    
    outNamespace = None
    if applyTo != None:
        file =  cmds.file(filePath + fileName,type = "editMA",r =True, namespace = namespace , applyTo = applyTo,mapPlaceHolderNamespace = mapPlaceHolderNamespace)
        outNamespace = cmds.file(file,q =True ,namespace = True)
    
    else:
        file =  cmds.file(filePath + fileName,type = "editMA",r =True, namespace = namespace , applyTo = "",mapPlaceHolderNamespace = mapPlaceHolderNamespace)
        outNamespace = cmds.file(file,q =True ,namespace = True)
    
    return outNamespace

def importEditMA(filePath,fileName,asMain,mapPlaceHolderNamespace = []):
    if not filePath.endswith("/") and filePath != "":
        filePath = filePath + "/"
        
    applyTo = getReferenceNode(asMain)    
    if applyTo != None:
        cmds.file(filePath + fileName,type = "editMA",i =True, applyTo = applyTo,mapPlaceHolderNamespace = mapPlaceHolderNamespace)
    else:        
        cmds.file(filePath + fileName,type = "editMA",i =True, applyTo = "", mapPlaceHolderNamespace = mapPlaceHolderNamespace)


def loadReference(namespace,load):
    refNode = getReferenceNode(namespace)
 
    if load == True:
        cmds.file(loadReference = refNode)
    else:
        cmds.file(unloadReference = refNode)



def saveFile(filePath,fileName):
    if not filePath.endswith("/") and filePath != "":
        filePath = filePath + "/"

    removeUnknownPlugin()
    clearUIcommand()

    filetype = extToFileType(fileName)    

    try:
        cmds.editRenderLayerGlobals(currentRenderLayer = "defaultRenderLayer")
    except:
        pass

    cmds.file(rename = filePath + fileName)
    cmds.file(                
                f =True,
                save = True,
                options = 'v=0;',
                type = filetype
            )

def exportFile(filePath,fileName,exportOpt = {"preserveReferences":False,"exportSelected":True,"shader":True,"expressions":True,"constraints":True,"constructionHistory":True,"channels":True}):
    if not filePath.endswith("/") and filePath != "":
        filePath = filePath + "/"

    filetype = extToFileType(fileName)
    
    cmds.file(
            filePath + fileName,
            force = True,
            options = 'v=0;',
            type = filetype,            
            **exportOpt
            )



##---------------------------------------------------------------------
##animations 
##---------------------------------------------------------------------
def bakeAnimations(targets,shapeAttrs = False,frameRange = []):
    ##bakeAnimation

    if len(frameRange) == 0:        
        start,end = getFrameRange("animation")    
        frameRange.append(start)
        frameRange.append(end)

    cmds.select(cl =True)
    cmds.bakeResults(targets, 
                        t=(frameRange[0],frameRange[1]),
                        simulation=True ,
                        shape =shapeAttrs,
                        bakeOnOverrideLayer = False,
                        removeBakedAttributeFromLayer =True,
                        removeBakedAnimFromLayer =True

                        )

    ##getAnimationCurves
    animCurves = []
    for target in targets:
        nodes = cmds.listConnections(target, type = "animCurve",s=True, d=False) or []
        animCurves.extend(nodes)

    return animCurves

def exportNodesEditMA(targets,exportPath,exportFile):
    cmds.select(targets, r = True,noExpand =True)

    if os.path.exists(exportPath) == False:
        os.makedirs(exportPath)
        
    cmds.exportEdits(exportPath+exportFile,type = "editMA",exportSelected =True,excludeHierarchy = True,includeAnimation=True,includeSetAttrs =True,includeNetwork =False,f =True)
    cmds.select(cl =True)

    return exportPath,exportFile

def reparentConstraint(nodes):
    nodes = cmds.ls(nodes, type = "constraint") or []

    for node in nodes:
        if nodeIsReference(node):
            continue
        
        inputs = cmds.listConnections(node + ".constraintParentInverseMatrix",s = True, d =False)
            
        if inputs == None:
            continue

        cmds.parent(node,inputs[0])        

def getIncludeNodes(selected,types = ["constraint","pairBlend"]):
    
    allNodes = []
    if "constraint" in types:
        constraintNodes = []

        for target in selected:
            if cmds.objExists(target + ".parentInverseMatrix[0]") == False:
                continue
            connections = cmds.listConnections(target + ".parentInverseMatrix[0]",type = "constraint",destination =True, source =False, p=False) or []
            
            for connection in connections:            
                if nodeIsReference(connection):
                    continue

                if connection not in constraintNodes:
                    constraintNodes.append(connection)
        
        allNodes.extend(constraintNodes)

    if "pairBlend" in types:
        blendNodes = []
        for target in selected:        
            
            connections = cmds.listConnections(target ,type = "pairBlend",destination =True, source =False, p=True) or []
            
            for connection in connections:            
                nodeName = connection.split(".")[0]
                attrName = connection.split(".")[-1]
                                
                if nodeIsReference(nodeName) or attrName != "weight":
                    continue
            
                if nodeName not in blendNodes:
                    blendNodes.append(nodeName)
        
        allNodes.extend(blendNodes)

    return allNodes

def extendReferenceEdit(exportPath,exportFile,namespace):
    refNode = getReferenceNode(namespace)
    if refNode == None:
        return
    
    refEdits = cmds.referenceQuery(refNode, editStrings=True,showDagPath =False)    
    exportStrings = ""
    
    for line in refEdits:
        if line.startswith("addAttr "):
            line = line.replace(namespace,"<main>")
            parts = line.split(" ")
            for i in range(1,len(parts)-1,2):
                if parts[i] in ["-longName","-shortName"]:
                    parts[i+1] = '"'+parts[i+1]+'"'                
            parts[-1] = '"'+parts[-1]+'"'
            line = " ".join(parts)
            
            exportStrings += line +";\n"
    
    if len(exportStrings) == 0:
        return
    
    #insert
    headerLine = 0
    with open(exportPath+exportFile)as f:
        for line in f:
            headerLine += 1
            if line.startswith("fileInfo"):
                break
                
    with open(exportPath+exportFile)as f:
        l = f.readlines()
    l.insert(headerLine, exportStrings)   

    with open(exportPath+exportFile, mode='w') as f:
        f.writelines(l)

def exportAnimationEditMA(targets,exportPath,exportFile,includeNodeTypes,excludeNode):
    cmds.select(targets, r = True,noExpand =True)

    includeNode = getIncludeNodes(targets,includeNodeTypes)

    if os.path.exists(exportPath) == False:
        os.makedirs(exportPath)
    
    if len(includeNode) == 0 and cmds.exportEdits(q = True,selected =True,includeSetAttrs =True,includeAnimation =True) != None:
        cmds.exportEdits(
                            exportPath+exportFile,
                            type = "editMA",
                            selected =True,
                            includeSetAttrs =True,
                            includeAnimation =True,
                            includeNode = includeNode,
                            excludeNode = excludeNode,
                            editCommand = "addAttr",
                            f =True
                        )

        cmds.select(cl =True)

    elif len(includeNode) != 0:
        cmds.exportEdits(
                            exportPath+exportFile,
                            type = "editMA",
                            selected =True,
                            includeSetAttrs =True,
                            includeAnimation =True,
                            includeNode = includeNode,
                            excludeNode = excludeNode,
                            editCommand = "addAttr",
                            f =True
                        )

        cmds.select(cl =True)
    else:
        print("nothing to export")
        cmds.select(cl =True)
        return None,""
    
    return exportPath,exportFile


##---------------------------------------------------------------------
##textures 
##---------------------------------------------------------------------

def findUVRangeFace(target,uvSet,UVRange):
    faceIds = []
    mesh_dagPath = om.MGlobal.getSelectionListByName(target).getDagPath(0)
    shape_Fn = om.MFnMesh(mesh_dagPath)
    face_ids = range(0,shape_Fn.numPolygons)
    it = om.MItMeshPolygon(mesh_dagPath)

    for index in face_ids:
        it.setIndex(index)

        try:
            uvs = it.getUVs(uvSet)
        except:
            continue
            
        insideRange = True
        for uPoint in uvs[0]:
            if uPoint < UVRange[0] or  uPoint > UVRange[1]:
                insideRange = False
                        
        for vPoint in uvs[1]:
            if vPoint < UVRange[2] or  vPoint > UVRange[3]:
                insideRange = False
                           
        if insideRange:
            faceIds.append(index)

    result = []
    for faceId in faceIds:
        result.append(target+".f["+str(faceId)+"]")
        
    return result


def getGridColor(filename,grindNum,index):    
    if not os.path.exists(filename):
        return False

    img = maya.OpenMaya.MImage()
    img.readFromFile(filename)
    
    w = maya.OpenMaya.uIntPtr()
    h = maya.OpenMaya.uIntPtr()
    img.getSize(w, h)
    dist = int(w.value() / grindNum)
       
    x = int((dist*0.5) + (dist * index[0]))
    y = int((dist*0.5) + (dist * index[1]))
    
    bytePoint = x + ((y-1) * w.value())
    bytePoint = bytePoint *4
        
    charPixelPtr = img.pixels()
    util = maya.OpenMaya.MScriptUtil()
    r = util.getUcharArrayItem(charPixelPtr, bytePoint)
    g = util.getUcharArrayItem(charPixelPtr, bytePoint+1)
    b = util.getUcharArrayItem(charPixelPtr, bytePoint+2)
    a = util.getUcharArrayItem(charPixelPtr, bytePoint+3)

    return [r/255.0, g/255.0, b/255.0, a/255.0]


def getCacheNodeInfo(node):
    fileNodeinfo = {
                    "files":[],
                    "node":[],
                    "directory":"",
                    "exists":False
    }

    texturePartsDict = {
                            "f":{"type":"int","padding":None,"default":0},
        }

    dirPath = cmds.getAttr(node + ".cachePath") + "/"
    cacheName = cmds.getAttr(node + ".cacheName")
    filePath = dirPath + cacheName + ".xml"
    fileName = cacheName + ".xml"

    files = []
    exists = os.path.exists(filePath)
    ##check mcx
    
    if os.path.exists(dirPath + cacheName + ".mcx"):
        files.append(cacheName + ".mcx")
            
    else:
        for i in glob.glob(dirPath + cacheName + "Frame*.mcx"):
            files.append(os.path.basename(i.replace(os.path.sep,'/')))

    files.append(cacheName + ".xml")

    fileNodeinfo = {
                    "node":[node],
                    "files":files,
                    "directory":dirPath,
                    "exists":exists
        }

    return filePath,fileNodeinfo

def getABCNodeInfo(node):
    fileNodeinfo = {
                    "files":[],
                    "node":[],
                    "directory":"",
                    "exists":False
    }

    texturePartsDict = {
                            "f":{"type":"int","padding":None,"default":0},
        }

    filePath = cmds.getAttr(node + ".abc_File")
    pathFormat = filePath.replace("<","{").replace(">","}")
    keys = editString.stringFormatToDict(pathFormat,{},returnType = "keys")

    if len(keys) != 0:
        dirPath = os.path.dirname(pathFormat) + "/"    
        fileNameFormat = os.path.basename(pathFormat)
        fileNameSample = editString.stringFormatToSampleString(fileNameFormat,texturePartsDict)
        retunFileDict = editFiles.getFileFork(dirPath,fileNameFormat,fileNameSample,None)

        fileNodeinfo = {
                    "node":[node],
                    "files":list(retunFileDict.keys()),
                    "directory":dirPath,
                    "exists":True
        }

    else:            
        filePath = cmds.getAttr(node + ".abc_File")
        fileName = os.path.basename(filePath)
        exists = os.path.exists(filePath)
        dirPath = os.path.dirname(filePath)

        fileNodeinfo = {
                    "node":[node],
                    "files":[fileName],
                    "directory":dirPath,
                    "exists":exists
        }

    return filePath,fileNodeinfo

def getFileNodeInfo(node):
    fileNodeinfo = {
                    "files":[],
                    "node":[],
                    "directory":"",
                    "exists":False
    }

    texturePartsDict = {
                            "UDIM":{"type":"int","padding":None,"default":0},
                            "f":{"type":"int","padding":None,"default":0},
        }
    
    if cmds.listConnections(node + ".fileTextureName",s =True,d =False) != None:
        return None,fileNodeinfo

    filePath = cmds.getAttr(node + ".computedFileTextureNamePattern")
    pathFormat = filePath.replace("<","{").replace(">","}")
    keys = editString.stringFormatToDict(pathFormat,{},returnType = "keys")

    if len(keys) != 0:
        dirPath = os.path.dirname(pathFormat) + "/"    
        fileNameFormat = os.path.basename(pathFormat)
        fileNameSample = editString.stringFormatToSampleString(fileNameFormat,texturePartsDict)
        retunFileDict = editFiles.getFileFork(dirPath,fileNameFormat,fileNameSample,None)

        fileNodeinfo = {
                    "node":[node],
                    "files":list(retunFileDict.keys()),
                    "directory":dirPath,
                    "exists":True
        }

    else:            
        filePath = cmds.getAttr(node + ".fileTextureName")
        fileName = os.path.basename(filePath)
        exists = os.path.exists(filePath)
        dirPath = os.path.dirname(filePath)

        fileNodeinfo = {
                    "node":[node],
                    "files":[fileName],
                    "directory":dirPath,
                    "exists":exists
        }

    return filePath,fileNodeinfo

def getAllFileNodeInfo(nodeType,ignorNodes = []):
    fileDict = {}
    fileNodes = cmds.ls(type = nodeType) or []

    for node in fileNodes:
        if node in ignorNodes:
            continue
        
        if nodeType == "AlembicNode":
            filePath,fileNodeinfo = getABCNodeInfo(node)
        
        elif nodeType == "file":
            filePath,fileNodeinfo = getFileNodeInfo(node)
        
        elif nodeType == "cacheFile":
            filePath,fileNodeinfo = getCacheNodeInfo(node)
    

        if filePath == None:
            continue

        if filePath in list(fileDict.keys()):
            fileDict[filePath]["node"].append(node)

        else:
            fileDict[filePath] = fileNodeinfo

    return  fileDict

def getAllTextureInfo(ignorNodes = []):
    fileDict = {}
    fileNodes = cmds.ls(type = "file") or []

    for node in fileNodes:
        if node in ignorNodes:
            continue
        
        filePath,fileNodeinfo = getFileNodeInfo(node)
        
        if filePath == None:
            continue

        if filePath in list(fileDict.keys()):
            fileDict[filePath]["node"].append(node)

        else:
            fileDict[filePath] = fileNodeinfo

    return  fileDict

##----------------------------------------------------------------
##view
##----------------------------------------------------------------

HUDDict = {
            "objectDetails":            ["HUDObjDetBackfaces","HUDObjDetSmoothness","HUDObjDetInstance","HUDObjDetDispLayer","HUDObjDetDistFromCm","HUDObjDetNumSelObjs"],
            "polyCount":                ["HUDPolyCountVerts","HUDPolyCountEdges","HUDPolyCountFaces","HUDPolyCountTriangles","HUDPolyCountUVs"],
            "particleCount":            ["HUDParticleCount"],
            "subdDetails":              ["HUDSubdLevel","HUDSubdMode"],
            "viewportRenderer":         ["HUDViewportRenderer"],
            "symmetry":                 ["HUDSymmetry"],
            "capsLock":                 ["HUDCapsLock"],
            "cameraNames":              ["HUDCameraNames"],
            "focalLength":              ["HUDFocalLength"],
            "frameRate":                ["HUDFrameRate"],
            "materialLoadingDetails":   ["HUDLoadingTextures","HUDLoadingMaterials"],
            "currentFrame":             ["HUDCurrentFrame"],
            "sceneTimecode":            ["HUDSceneTimecode"],
            "currentContainer":         ["HUDCurrentContainer"],
            "viewAxis":                 ["HUDViewAxis"],
            "HikDetails":               ["HUDHikKeyingMode"],
            "selectDetails":            ["HUDSoftSelectState"],
            "animationDetails":         ["HUDIKSolverState","HUDCurrentCharacter","HUDPlaybackSpeed","HUDSoftSelectState"],
            "toolMessage":              ["HUDSoftSelectState"],
            "XGenHUD":                  ["HUDSoftSelectState","HUDXGenSplinesCount","HUDXGenGPUMemory"],
            "evaluationManagerHUD":     ["HUDGPUOverride","HUDEMState","HUDEvaluation","HUDSoftSelectState"]
}

def getCurHUDItems():
    showItems = []

    items = cmds.headsUpDisplay(listHeadsUpDisplays =True)

    for item in items:
        if cmds.headsUpDisplay(item, q = True, vis = True):
            showItems.append(item)

    return showItems

def hideAllHUDTtems():
    items = cmds.headsUpDisplay(listHeadsUpDisplays =True)

    for item in items:
        cmds.headsUpDisplay(item, e = True, vis = False) 


def setHUDItems(setNames):
    for key in setNames:
        if key not in list(HUDDict.keys()):
            continue

        for item in HUDDict[key]:
            if cmds.headsUpDisplay(item, exists = True) == False: 
                continue

            cmds.headsUpDisplay(item, e = True, vis = True) 

def getCurViewPanel():
    curView = omui.M3dView.active3dView()
    return OpenMayaUI.MQtUtil.fullName(int(omui.M3dView.active3dView().widget())).split("|")[-2]

def getView(panelName):    
    if cmds.modelPanel(panelName, exists =True) == False:
        return None

    if panelName not in cmds.getPanel(visiblePanels=True) or []:
        return None
    
    return omui.M3dView.getM3dViewFromModelPanel(panelName)
                
def setIsolateView(panelName,nodes):
    cmds.isolateSelect(panelName,state = False)        
    cmds.isolateSelect(panelName,state = True)
    
    for node in nodes:
        if cmds.objExists(node):
            cmds.isolateSelect(panelName,addDagObject = node)

def createTmpView():
    window = cmds.window('window')    
    mainLayout = cmds.formLayout(window)
    panel = cmds.modelEditor()
    cmds.formLayout(mainLayout, e=True,
                                attachForm=[(panel, "top", 0),(panel, "left", 0), 
                                    (panel, "bottom", 0), (panel, "right", 0)]) 
    cmds.showWindow(window)
    return window,panel


def getFrames(startFrame,endFrame,byFrame):    
    frames = []
    for i in range(int(startFrame),int(endFrame) +1,int(byFrame)):
        frames.append(i)

    return frames

def excutePlayBlast(viewItemOption,camera,outputPath,outputFormat,timeRange,resolution,nodes =None,panel = None,byFrame = 1,sequenceTime =False,colorMng = True,renderOR = ""):
    cmds.select(cl = True)
    window = None

    if panel == None:
        window,panel = createTmpView()
        cmds.modelEditor(panel, edit=True, **viewItemOption)

    cmds.modelEditor(panel, edit=True, camera=camera)
    curColorMng = cmds.getAttr("defaultColorMgtGlobals.playblastOutputTransformEnabled")
    cmds.setAttr("defaultColorMgtGlobals.playblastOutputTransformEnabled",colorMng)
    
    if renderOR != "":    
        cmds.modelEditor(panel,e=True,rendererOverrideName=renderOR)
    
    cmds.refresh(currentView=True)
    
    if nodes != None:
        setIsolateView(panel,nodes)

    compressionDict = {
                            "png":["png","image"],
                            "jpg":["jpg","image"],
                            "avi":["none","movie"]
                        }
    
    outputPath = outputPath.replace("//","/")

    if sequenceTime == "sequenceTime":
        print("use sequenceTime >> " + str(timeRange[0]) + "  to " + str(timeRange[1]))
        cmds.playblast(
                        filename = outputPath,
                        forceOverwrite =True,
                        format = compressionDict[outputFormat][1],
                        compression = compressionDict[outputFormat][0],
                        sequenceTime = True,
                        clearCache = 1,
                        viewer = False,
                        showOrnaments =  True,
                        offScreen = True,
                        fp = 4, 
                        percent = 100,
                        quality = 100,
                        # frame = frames,
                        startTime = timeRange[0],
                        endTime = timeRange[1],
                        widthHeight = resolution,
                        editorPanelName = panel,                        
                    )
    else:        
        frames = getFrames(timeRange[0],timeRange[1],1)

        if sequenceTime != None:
            frames = sequenceTime

        cmds.playblast(
                        filename =outputPath,
                        forceOverwrite =True,
                        format = compressionDict[outputFormat][1],
                        compression = compressionDict[outputFormat][0],
                        sequenceTime = False,
                        clearCache = 1,
                        viewer = False,
                        showOrnaments =  True,
                        offScreen = True,
                        fp = 4, 
                        percent = 100,
                        quality = 100,
                        frame = frames,
                        # startTime = timeRange[0],
                        # endTime = timeRange[1],
                        widthHeight = resolution,
                        editorPanelName = panel,
                        # sound = sound
                    )
        
    
    cmds.isolateSelect(panel,state = False)
    cmds.setAttr("defaultColorMgtGlobals.playblastOutputTransformEnabled",curColorMng)

    if window != None:
        cmds.deleteUI(window)

    if byFrame != 1:                
        if compressionDict[outputFormat][1] == "image":            
            outputPathObj = pathlib.Path(outputPath)
            dirPath = str(outputPathObj.parent).replace(os.path.sep,'/') + "/"
            seqFilePath = list(pathlib.Path(dirPath).rglob(outputPathObj.name+"*."+compressionDict[outputFormat][0]))
            
            seqFiles = []

            for filePath in seqFilePath:
                fileName = str(filePath.name)
                seqFiles.append(fileName)

            editFiles.overwiteStepFrames(byFrame,seqFiles,dirPath)
    
def getCurViewSetting(camera):
    displayResolution = cmds.getAttr(camera + ".displayResolution")
    overscan = cmds.getAttr(camera + ".overscan")
    curHUDs = getCurHUDItems()
    return displayResolution,overscan,curHUDs

def prepareViewSetting(camera,resolutionGate,showHUDs,headsUpDisplay):
    displayResolution,overscan,curHUDs = getCurViewSetting(camera)

    hideAllHUDTtems()

    showHUDItems = []

    for HUDItem in list(showHUDs.keys()):
        if showHUDs[HUDItem]:
            showHUDItems.append(HUDItem)

    if headsUpDisplay ==False:
        cmds.setAttr(camera + ".displayResolution",False)

        if cmds.getAttr(camera + ".overscan",l=True) == False and cmds.listConnections(camera + ".overscan") == None:
            cmds.setAttr(camera + ".overscan",1.0)

    elif headsUpDisplay == True and resolutionGate == False:
        cmds.setAttr(camera + ".displayResolution",False)
        
        if cmds.getAttr(camera + ".overscan",l=True) == False and cmds.listConnections(camera + ".overscan") == None:
            cmds.setAttr(camera + ".overscan",1.0)

    
    if resolutionGate == True and displayResolution == False:        
        cmds.setAttr(camera + ".displayResolution",True)
        
        if cmds.getAttr(camera + ".overscan",l=True) == False and cmds.listConnections(camera + ".overscan") == None:
            cmds.setAttr(camera + ".overscan",1.3)

    setHUDItems(showHUDItems)


def restoreViewSetting(camera,displayResolution,overscan,curHUDs):
    cmds.setAttr(camera + ".displayResolution",displayResolution)
    
    if cmds.getAttr(camera + ".overscan",l=True) == False and cmds.listConnections(camera + ".overscan") == None:
        cmds.setAttr(camera + ".overscan",overscan)
    hideAllHUDTtems()
    setHUDItems(curHUDs)



def checkWorkspaceExists(path):
    if os.path.exists(path + "workspace.mel"):
        return True

    workspace_dict = {}

    fileRules = mel.eval("np_getDefaultFileRuleWidgets")
    for i in range(0,len(fileRules),2):
        workspace_dict[fileRules[i]] = fileRules[i+1]

    cmds.workspace(directory = path)

    for key in workspace_dict.keys():
        cmds.workspace(fileRule = [key,workspace_dict[key]])
        

def setProject(projectPath):
    checkWorkspaceExists(projectPath)
    cmds.workspace(projectPath, openWorkspace =True)
    cmds.workspace(saveWorkspace = True)

    print("set projectPath  >>>  " + projectPath)
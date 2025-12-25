from __future__ import (absolute_import, division,print_function)
import sys
import os
import glob
import json
import shutil
from datetime import datetime

from . import editString

try:
    from importlib import reload
except:
    pass

reload(editString)
LOCALAPPDATA = os.getenv('LOCALAPPDATA').replace(os.path.sep,'/') + "/"
##--------------------------------------------------------------------------------------------
mayaVer = None
executable = sys.executable
if executable.endswith("maya.exe") or executable.endswith("mayabatch.exe"):
    import maya.cmds as cmds
    import maya.mel as mel
    mayaVer = cmds.about(version=True)

if mayaVer in ["2020","2019"]:
    from . import pathlib_2_7 as pathlib
else:
    import pathlib


def removeModules(moduleName):
    for k in list(sys.modules):
        if k.startswith(moduleName):
            del sys.modules[k]

##-----------------------------------------------
##os file
##-----------------------------------------------
def convertPathStringByMayaVer(path):
    if mayaVer in ["2020","2019"]:
        path = unicode(path,"mbcs").replace(os.path.sep, '/') + "/"

    return path

def checkPathString(dirPath):    
    dirPath = dirPath.replace(os.path.sep, '/')

    if dirPath.endswith("/") ==False:
        dirPath = dirPath + "/"
        
    return dirPath


def getFileInfo(filePath,infoKey):
    if mayaVer in ["2020","2019"]:
        filePath = filePath.encode("mbcs")

    infoDict = {}

    if "size" in infoKey:
        size = os.path.getsize(filePath)
        infoDict["size"] = str(round(size/1048576,5))

    if "update" in infoKey:
        create,update = getTimeStamp(filePath)
        infoDict["update"] = update

    if "ext" in infoKey:        
        infoDict["ext"] = filePath.split(".")[-1]

    return infoDict

def listDirs(dirPath,ignor = []):
    dirPath = checkPathString(dirPath)

    if mayaVer in ["2020","2019"]:
        dirPath = dirPath.encode("mbcs")

    dirs = []
    
    if os.path.exists(dirPath)==False:
        return dirs

    pathNode = pathlib.Path(dirPath).iterdir()

    for node in pathNode:
        if node.is_dir():
            dirName = node.name
            
            if mayaVer in ["2020","2019"]:       
                dirName = dirName.decode("mbcs")
                
            dirs.append(dirName)

        else:
            continue
    
    dirs = list(set(dirs) - set(ignor))
    dirs.sort()
    return dirs

def listFiles(dirPath,exts = None):
    files = []
    dirPath = checkPathString(dirPath)

    if mayaVer in ["2020","2019"]:
        dirPath = dirPath.encode("mbcs")

    if os.path.exists(dirPath)==False:
        return files

    pathNode = pathlib.Path(dirPath).iterdir()
    
    for node in pathNode:
        if node.is_dir():
            continue
        
        elif node.is_file():
            fileName = node.name

            if mayaVer in ["2020","2019"]:     
                fileName = fileName.decode("mbcs")

            extension = node.suffix.replace(".","").lower()
            if exts != None and extension not in exts:
                continue

            files.append(fileName)
    
    files.sort()
    return files

def getTimeStamp(filePath,format = "%Y/%m/%d %H:%M"):
    create = ""
    update = ""

    if filePath == "" or os.path.exists(filePath) ==False:
        return create,update

    c_dt = datetime.fromtimestamp(os.path.getctime(filePath))
    dt = datetime.fromtimestamp(os.path.getmtime(filePath))

    create = c_dt.strftime(format)
    update = dt.strftime(format)
    return create,update

##  vers------------------------------------------------------------------
def getPathFork(path,pathPartsDict):
    pathPartsDict = editString.stringFormatToDict(path,pathPartsDict)
    pathParts = path.format(**pathPartsDict).split("/")
    key = ""
    for i in range(0, len(pathParts)):
        if pathParts[i].startswith("{"):
            key = pathParts[i].replace("{","").replace("}","")
            break

    checkPath = "/".join(pathParts[:i])+"/"
    elements = listDirs(checkPath,ignor = [])
    return key,elements

def getDirctoryFork(path,sampleString,nameFormat):
    dirs = listDirs(path,ignor = [])
    retunDirDict = {}

    for dir in dirs:        
        partsDict = editString.stringToDict(dir,sampleString,nameFormat,orNone = True)        
        if len(partsDict) == 0:
            continue

        retunDirDict[dir] = partsDict
    
    return retunDirDict

def getDirForkValues(directoryPath,nameFormat,sampleString,sampleKey):
    dirsDict = getDirctoryFork(directoryPath,sampleString,nameFormat)
    sampleList = []
    
    for dirName in list(dirsDict.keys()):
        sampleValue = dirsDict[dirName][sampleKey]
        sampleList.append(sampleValue)
    
    sampleList.sort()
    return sampleList

def getFileFork(path,nameFormat,sampleString,exts):    
    files = listFiles(path,exts)    
    retunFileDict = {}

    for file in files:            
        partsDict = editString.stringToDict(file,sampleString,nameFormat,orNone = True)
        
        if len(partsDict) == 0:
            continue

        retunFileDict[file] = partsDict
    
    return retunFileDict

def getFileForkValues(directoryPath,fileNameFormat,sampleString,sampleKey,exts):
    filesDict = getFileFork(directoryPath,fileNameFormat,sampleString,exts)
    sampleList = []
    
    for fileName in list(filesDict.keys()):
        sampleValue = filesDict[fileName][sampleKey]
        sampleList.append(sampleValue)
    
    sampleList.sort()
    return sampleList

def directoryKeySearch(serverDict,path,pathPartsDict,matchPartsDict):
    part = path.split("/")[0]
    hitKey = None

    for formatString in list(serverDict.keys()):
        if formatString == "<ACTION>":
            continue

        elif part == formatString: 
            hitKey = formatString
            break
                    
        elif formatString.find("{") != -1:
            formatStringDict = editString.stringFormatToDict(formatString,{},returnType = "dict")            
            directorySample = editString.stringFormatToSampleString(formatString,matchPartsDict)

            tmpformatString = formatString
            for key in list(formatStringDict.keys()):
                if matchPartsDict[key]["type"] == "multi":
                    tmpformatString = formatString.format(**{key:matchPartsDict[key]["multiParts"]})

            directoryDict = editString.stringToDict(part,directorySample,tmpformatString,False)
            
            for key in list(formatStringDict.keys()):
                if matchPartsDict[key]["type"] == "multi":
                    directoryDict[key] = matchPartsDict[key]["multiParts"].format(**directoryDict)

            pathPartsDict.update(**directoryDict)
            
            hitKey = formatString
            break

    return hitKey,pathPartsDict

def pathSearchDown(serverDict,path,stopKey = "",pathPartsDict = {},matchPartsDict = {}):
    keyList = []
    hitKey = ""
    checkDict = dict(serverDict)
    while hitKey != None and  len(path) != 0:
        hitKey,directoryPartsDict = directoryKeySearch(checkDict,path,pathPartsDict,matchPartsDict)         
        path = "/".join(path.split("/")[1:])
        
        if hitKey == None:
            break

        keyList.append(hitKey)

        if stopKey == hitKey:
            break

        checkDict = checkDict[hitKey]
    
    return pathPartsDict,keyList

def digDict(targetDict,keys):
    searchDict = dict(targetDict)

    for key in keys:
        if key in searchDict.keys():
            searchDict = searchDict[key]

    return searchDict

def getStructureSetting(path,structureDict,actionDict,MATCHPARTS):
    pathPartsDict,keyList = pathSearchDown(structureDict,path,"",{},MATCHPARTS)    
    curHierarchyDict = digDict(structureDict,keyList)    
    actionName = "default"
    
    if "<ACTION>" in curHierarchyDict.keys():            

        if curHierarchyDict["<ACTION>"].startswith("lambda"):                    
            ldict = {}        
            exec("lamdaString = " + curHierarchyDict["<ACTION>"], globals(), ldict)
            lamdaString = ldict["lamdaString"]            
            actionName = lamdaString(pathPartsDict)

        else:
            actionName = curHierarchyDict["<ACTION>"]
    
    if actionName in actionDict.keys():
        return actionDict[actionName]
    else:
        return actionDict["default"]

##-----------------------------------------------
##json file
##-----------------------------------------------
def readJSON(filePath,defaultDict = None):
    importDict = {}

    if os.path.exists(filePath) == True and os.path.isfile(filePath):
        with open(filePath) as f:
            importDict = json.load(f)	

    if defaultDict == None:
        return importDict

    else:
        for key in list(defaultDict.keys()):
            if key not in list(importDict.keys()):
                importDict[key] = defaultDict[key]

    return importDict

def writeJSON(filePath,valueDict,indent = 4):	
    with open(filePath, 'w') as f:
        json.dump(valueDict, f, indent = indent)

def saveDictOption(settingDict,libName,toolName,optionKey = None):
    if os.path.exists(LOCALAPPDATA + libName +"/") ==False:
        os.makedirs(LOCALAPPDATA + libName +"/")
    
    if optionKey == None:    
        writeJSON(LOCALAPPDATA + libName+"/"+toolName +"Setting.json",settingDict)

    else:                        
        curSettingDict = readDictOption({},libName,toolName)    
        curSettingDict[optionKey] = settingDict[optionKey]
        writeJSON(LOCALAPPDATA + libName+"/"+toolName +"Setting.json",settingDict)
    
def readDictOption(settingDict,libName,toolName):
    if os.path.exists(LOCALAPPDATA + libName+"/"+toolName +"Setting.json"):
        importDict = readJSON(LOCALAPPDATA + libName+"/"+toolName +"Setting.json")        
        settingDict.update(**importDict)
        
    return settingDict

def saveOptionUpdate(defaultDict,optionDict,saveName,libName,keys = None):
    curOptionDict = readDictOption(defaultDict,libName,saveName)

    if keys == None:
        keys = list(optionDict.keys())
    
    curOptionDict = editString.updateDict(curOptionDict,optionDict,keys)    
    saveDictOption(curOptionDict,libName,saveName)


##-----------------------------------------------
##script file
##-----------------------------------------------
def sourceScriptFile(filePath):
    dirPath = os.path.dirname(filePath)
    fileName = os.path.basename(filePath).split(".")[0]
    
    if os.path.isfile(filePath):
        exec(open(filePath).read())

#-----------------------------------------------
#image file
#-----------------------------------------------

def overwiteStepFrames(step,seqFiles,dirPath):
    for i in range(0,len(seqFiles),step):
        sourceFile = str(seqFiles[i]).replace(os.path.sep,'/')
        
        for ii in range(1,step):
            if len(seqFiles) > i + ii:
                targetFile =  str(seqFiles[i + ii]).replace(os.path.sep,'/')
                shutil.copy2(dirPath+sourceFile,dirPath+targetFile)


def searchStringByLine(filePath,search):
    hitLines = []
    with open(filePath,"r") as f:
        lines = f.readlines()
        for l in lines:
            if search not in l:
                continue
                
            hitLines.append(l)
                        
    f.close()

    return hitLines

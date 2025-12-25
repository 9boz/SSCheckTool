from __future__ import (absolute_import, division,print_function, unicode_literals)
import re

##-----------------------------------------------
##
##-----------------------------------------------
def capitalizeString(sourceString):
    distString = sourceString[0].upper() + sourceString[1:]
    return distString

def lowerString(sourceString):
    distString = sourceString[0].lower() + sourceString[1:]
    return distString

def addPrefix(prefix,sourceString):
    
    if sourceString == "":
        return prefix
    
    if prefix != "":
        return prefix + capitalizeString(sourceString)

    else:
        return sourceString

def editName(source, prefix,suffix,search,replace):
    dist = source.replace(search,replace)
    dist = prefix + capitalizeString(dist) + suffix

    return dist

def intToAlpha(num):
    if num <= 26:
        return chr(64+num)

    elif num%26==0:
        return chr(64+(num/26)-1) + chr(90)
    
    else:
        return chr(64+num/26) + intToAlpha(num%26)

def generateSeqString(seqType,num,padding):

    if seqType == "number":
        seqString = str(num).zfill(padding)

    elif seqType == "alphabet":
        seqString = intToAlpha(num)

    return seqString

def generateName(prefix, suffix,seqType,padding, num = None):
    if num == None:
        return [prefix + capitalizeString(suffix)]

    names = []
    for i in range(0,num):
        names.append(prefix + generateSeqString(seqType,num,padding) + capitalizeString(suffix))
    return names

def replaceName(sourceString,prefix,suffix,search,replace,capitalize):
    if capitalize == False:
        returnString = prefix + sourceString.replace(search,replace) + capitalizeString(suffix)
    else:
        returnString = prefix + capitalizeString(sourceString.replace(search,replace)) + capitalizeString(suffix)

    return returnString

def removePrefix(sourceString,prefix,lower):
    if sourceString.startswith(prefix):
        returnString = sourceString.replace(prefix,"",1)

        if lower:
            returnString = lowerString(returnString)

    else:
        returnString = sourceString

    return returnString
    
def setNumberPadding(inputValue,padding):
    if len(inputValue) > padding:
        return inputValue

    return str(inputValue).zfill(padding - len(inputValue))

def reFillList(inputList,startIndex,fillItem):
   
    for i in range(startIndex,len(inputList)):
        inputList[i] = fillItem

    return inputList

def fillList(inputList,length,fillItem):

    if len(inputList) < length:

        for i in range(0,length-len(inputList)):
            inputList.append(fillItem)

    return inputList

def fillDict(inputDict,keys,fillItem):
    for key in keys:
        if key not in list(inputDict.keys()):
            inputDict[key] = fillItem

    return inputDict


def updateDict(baseDict,sourceDict,keys):

    for key in keys:

        if key not in list(sourceDict.keys()):
            continue
        baseDict.update({key:sourceDict[key]})

    return baseDict
##-----------------------------------------------------------------------------
def generateMatchParts(keyName,partsInfoDict):
    matchStrng = ""

    ##prefix
    if "prefix" in list(partsInfoDict.keys()):
        matchStrng += "("+"|".join(partsInfoDict["prefix"]) + "?)"
   
    matchStrng += "(?P<"+keyName+">"
           
    if partsInfoDict["type"] == "string":
        matchStrng += "[a-z|0-9|A-Z]"
          
    elif partsInfoDict["type"] == "alphabet":
        matchStrng += "[a-z|A-Z]"
          
    elif partsInfoDict["type"] == "alphabetLower":
        matchStrng += "[a-z]"
          
    elif partsInfoDict["type"] == "alphabetUpper":
        matchStrng += "[A-Z]"
      
    elif partsInfoDict["type"] == "list":
        matchStrng += "|".join(partsInfoDict["list"])
        
    elif partsInfoDict["type"] == "int":
        matchStrng += "[0-9|\-]"
        
    elif partsInfoDict["type"] == "float":
        matchStrng += "[0-9|\.|\-|e]"
    
    elif partsInfoDict["type"] == "stringAll":
        matchStrng += "[_|a-z|0-9|A-Z]"

    #padding
    if partsInfoDict["type"] != "list":
        if partsInfoDict["padding"] == None:
            matchStrng += "+"  
        
        elif partsInfoDict["padding"] == 0:
            matchStrng += "*"  

        elif type(partsInfoDict["padding"]) == list:
            matchStrng += "{"+str(partsInfoDict["padding"][0])+","+str(partsInfoDict["padding"][1])+"}"  

        elif type(partsInfoDict["padding"]) == int:
            matchStrng += "{"+str(partsInfoDict["padding"])+"}"  
    
    matchStrng += ")"

    if "suffix" in list(partsInfoDict.keys()):
        matchStrng += "("+"|".join(partsInfoDict["suffix"]) + ")"

    return matchStrng

def stringFormatToSampleString(formatString,partsDict):
    sampleDict = {}
    for key in list(partsDict.keys()):
    
        if partsDict[key]["type"] == "multi":
            subKeys = stringFormatToDict(partsDict[key]["multiParts"],{},"keys")            
            for subkey in subKeys:                
                sampleDict[subkey] = generateMatchParts(subkey,partsDict[subkey])    
            
            sampleDict[key] = partsDict[key]["multiParts"].format(**sampleDict)

        else:
            sampleDict[key] = generateMatchParts(key,partsDict[key])
        
    sampleString = formatString.replace(".","\.").format(**sampleDict)

    return sampleString

def stringFormatToDict(string,partsDict,returnType = "dict",expandMulti = False,MATCHPARTS ={}):
    # string = "{DRIVE}/proj/{PROJECT}/assets/{ASSETTYPE}/{ASSETNAME}/scenes/"
    
    sampleString = "{([A-Z|a-z|0-9]+)}"
    allKeys = re.findall(sampleString,string) or []
    
    for key in allKeys:
        if key not in list(partsDict.keys()):
            partsDict[key] = "{"+key+"}"

            if expandMulti:
                if MATCHPARTS[key]["type"] == "multi":
                    multiPartsDict = stringFormatToDict(MATCHPARTS[key]["multiParts"],partsDict,returnType = "dict")
                    partsDict.update(multiPartsDict)

    if returnType == "dict":
        return partsDict
        
    elif returnType == "keys":
        return allKeys

def stringFormatExpand(formatString,MATCHPARTS):
    ## {CUT}
    ## to
    ## {CUTPREFIX}{CUTNumber}{CUTSUFFIX}

    partsDict = stringFormatToDict(formatString,{},returnType = "dict")

    for key in list(partsDict.keys()):
        if MATCHPARTS[key]["type"] == "multi":
            multiPartsDict = stringFormatToDict(MATCHPARTS[key]["multiParts"],partsDict,returnType = "dict")
            partsDict.update(multiPartsDict)
            partsDict[key] = MATCHPARTS[key]["multiParts"]
    
    formatString = formatString.format(**partsDict)
    return formatString

def stringFormatExpandDict(formatString,partsDict,MATCHPARTS):
    ##{"CUT":"","CUTPREFIX":"c","CUTNUMBER":"002","CUTSUFFIX":""} 
    ## to 
    ##{"CUT":"c002","CUTPREFIX":"c","CUTNUMBER":"002","CUTSUFFIX":""} 
    
    tmpPartsDict = stringFormatToDict(formatString,{},returnType = "dict")
    
    for key in list(tmpPartsDict.keys()):
        if key not in list(MATCHPARTS.keys()):
            continue

        if MATCHPARTS[key]["type"] == "multi":
            partsDict[key] = MATCHPARTS[key]["multiParts"].format(**partsDict)
        
    return partsDict

def expandMultiDict(partsDict,MATCHPARTS):
    ##{"CUT":"c002"} 
    ## to 
    ##{"CUT":"c002","CUTPREFIX":"c","CUTNUMBER":"002","CUTSUFFIX":""} 

    keys = list(partsDict.keys())

    for key in keys:
        if key not in list(MATCHPARTS.keys()):
            continue

        if MATCHPARTS[key]["type"] == "multi":                 
            sampleString = stringFormatToSampleString(MATCHPARTS[key]["multiParts"],MATCHPARTS)            
            multiPartsDict = stringToDict(partsDict[key],sampleString,MATCHPARTS[key]["multiParts"])            
            partsDict.update(**multiPartsDict)

    return partsDict

def stringToDict(string,sampleString,formatString,orNone = True):
    partsDict = stringFormatToDict(formatString,{},"dict")    
    match = re.match(sampleString,string)
    
    for key in list(partsDict.keys()):        
        try:
            partsDict[key] = match.group(key)
        except:
            if orNone:
                partsDict.pop(key)
                continue

            else:
                partsDict[key] = ""

    return partsDict


def pathToDict(path,pathFormat):
    partsDict = {}
    partsDict = stringFormatToDict(pathFormat,partsDict)
    
    pathParts = path.split("/")
    pathFormatParts = pathFormat.split("/")

    for pathPart,pathFormatPart in zip(pathParts,pathFormatParts):
        if pathFormatPart.startswith("{"):
            key = pathFormatPart.replace("{","").replace("}","")
            partsDict[key] = pathPart

    return partsDict


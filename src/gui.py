
from __future__ import (absolute_import, division,print_function)
import os
import maya.cmds as cmds
from datetime import datetime

try:
    from PySide2 import QtWidgets,QtGui,QtCore
    qaction = QtWidgets.QAction

except:
    from PySide6 import QtWidgets,QtGui,QtCore
    qaction = QtGui.QAction


from .SPLib import editFiles,guiUtil,editString,editTransform,editScenes
from . import checkUtil

from importlib import import_module
try:
    from importlib import reload
except:
    pass

reload(guiUtil)
reload(editScenes)
reload(editFiles)
reload(checkUtil)
reload(editTransform)

##-----------------------------------------------------------------------------------------
def getDefaultPath():
    LIBPATH = os.path.normpath(os.path.join(os.path.dirname(__file__).replace(os.path.sep, '/'), '../')).replace(os.path.sep, '/') + "/"
    logExportPath = LIBPATH + "checkResult/"
    presetPath = LIBPATH+ "checkPreset/"
    modulePath = LIBPATH+ "src/checkCommands/"
    return logExportPath,presetPath,modulePath

def importModuleList():
    logExportPath,presetPath,modulePath = getDefaultPath()
    moduleNameList = []
    files = editFiles.listFiles(modulePath,["py"])
        
    for file in files:
        if file == "__init__.py":
            continue

        moduleName = file.replace(".py","")        
        moduleNameList.append(moduleName)

    moduleNameList.sort()    
    return moduleNameList

##-----------------------------------------------------------------------------------------
def execCorrectCmd(moduleName,optDict):
    checkModule = import_module("."+moduleName ,"SSCheckTool.src.checkCommands")
    reload(checkModule)
    result = checkModule.correct(**optDict)
    return result

def execCheckCmd(moduleName,optDict):
    checkModule = import_module("."+moduleName ,"SSCheckTool.src.checkCommands")
    reload(checkModule)
    result = checkModule.check(**optDict)
    return result

def getCheckComment(moduleName):  
    checkModule = None
    try:
        checkModule = import_module("."+moduleName ,"SSCheckTool.src.checkCommands")
        reload(checkModule)
    except:
        checkModule = None

    if checkModule == None:
        return "cant find checkModule",False,False

    existCorrect = False
    if "correct" in dir(checkModule):        
        existCorrect =True

    return str(checkModule.comment),existCorrect,True

##-----------------------------------------------------------------------------------------
def setButtonColor(button,condition):
    if condition == "default":
        button.setStyleSheet('QPushButton{background-color: gray;color: black ;}')
    
    elif condition == "hit":
        button.setStyleSheet('QPushButton{background-color: #f72105;color: white ;}')
    
    elif condition == "warning":
        button.setStyleSheet('QPushButton{background-color: #ebf705;color: black ;}')

    elif condition == "clean":
        button.setStyleSheet('QPushButton{background-color: #05f7f7 ;color: black ;}')

def getDisplayName(node):
    if editTransform.checkUniqueName(node):
        return node.split("|")[-1]
    else:
        return node

def getPresetList(presetPath):    
    presetFiles = editFiles.listFiles(presetPath,["json"])
    return presetFiles

def resultExportToFile(resultDict,CURPRESET,logExportPath):
    resultString = ""

    filePath,fileNameBody,extension = editScenes.getCurSceneName()    
    create,update = editFiles.getTimeStamp(filePath + fileNameBody +extension)
    now = datetime.now()
    today =  str(now.year) +"/"+ str(now.month).zfill(2) +"/"+ str(now.day).zfill(2) + "  " + str(now.hour).zfill(2) + ":"+ str(now.minute).zfill(2)

    if fileNameBody == "":
        fileNameBody = "curScene"

    resultString += "<<<<< excuteCheck result>>>>>" + "\n"
    resultString += "checkDate:" + today + "\n"
    resultString += "usePrest:" + CURPRESET + "\n\n"

    resultString += "<<<fileInfo>>>" + "\n"
    resultString += "filePath:" + filePath + "\n"
    resultString += "fileName:" + fileNameBody + extension+"\n"    
    resultString += "fileTimeStamp:" + str(update) + "(update)\n\n"
    
    resultString += "<<<results>>>" + "\n"

    checkList = list(resultDict.keys())
    checkList.sort()
    for checkName in checkList:
        resultString += ">>>" + checkName + "\n"
        
        if len(resultDict[checkName]) == 0:
            resultString += "     \n"
        else:
            for i in resultDict[checkName]:
                resultString += getDisplayName(i) + "\n"

        resultString += "     \n"

    resultFileName = fileNameBody + "_checkResult_" +str(now.year) +"_"+ str(now.month).zfill(2) +"_"+ str(now.day).zfill(2) + "_" + str(now.hour).zfill(2) + "_"+ str(now.minute).zfill(2) + ".txt"

    with open(logExportPath +resultFileName, mode='w') as f:
        f.write(resultString)

    editScenes.openFile(logExportPath,resultFileName,"os")


##------------------------------------------------------------------
## MARK: GUI
##------------------------------------------------------------------
class CheckerGUI(QtWidgets.QWidget):
    def __init__(self,parent,*args, **kwargs):
        super(CheckerGUI,self).__init__(*args,**kwargs)
        # guiUtil.readStyleSheet(self)
        self.parent = parent
        
        self.checkListGUI = {}
        self.allResult = {}

        mainLayout = QtWidgets.QHBoxLayout(self)
        mainSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        mainLayout.addWidget(mainSplitter)

        ##left side
        leftWidget = QtWidgets.QWidget()
        leftLayout = QtWidgets.QVBoxLayout(leftWidget)
        mainSplitter.addWidget(leftWidget)
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(10)

        ##setting $ command
        settingBox = QtWidgets.QGroupBox()
        settingBox.setObjectName("unUsetitle")
        leftLayout.addWidget(settingBox)
        settingLayout = QtWidgets.QVBoxLayout(settingBox)

        self.rootNodeFld = guiUtil.ObjectFld(longName =True)
        self.rootNodeFld.layout.insertWidget(0,QtWidgets.QLabel("topNode:"))
        settingLayout.addWidget(self.rootNodeFld)

        checkAllBtn = QtWidgets.QPushButton("check all")
        settingLayout.addWidget(checkAllBtn)
        
        resultBtnLayout = QtWidgets.QHBoxLayout()
        settingLayout.addLayout(resultBtnLayout)
        refreshAllBtn = QtWidgets.QPushButton("refresh result")
        resultBtnLayout.addWidget(refreshAllBtn)

        exportBtn = QtWidgets.QPushButton("export result")
        resultBtnLayout.addWidget(exportBtn)

        checkAllBtn.clicked.connect(self.applyCheckAll)
        refreshAllBtn.clicked.connect(self.refreshResult)
        exportBtn.clicked.connect(self.exportResult)

        ##checkList
        chekListBox = QtWidgets.QGroupBox()
        chekListBox.setObjectName("unUsetitle")
        leftLayout.addWidget(chekListBox)

        listLayout = QtWidgets.QVBoxLayout(chekListBox)
        listLayout.setContentsMargins(0,0,0,0)

        listArea = QtWidgets.QScrollArea()
        listLayout.addWidget(listArea)
        listArea.setWidgetResizable(True)
        listWidget = QtWidgets.QWidget()
        listArea.setWidget(listWidget)
        listArea.setMinimumHeight(200)
        listArea.setMinimumWidth(300)

        self.allCheckLayout = QtWidgets.QFormLayout(listWidget)
        self.allCheckLayout.setVerticalSpacing(2)
        self.allCheckLayout.setLabelAlignment(QtCore.Qt.AlignRight)

        # leftLayout.addStretch()

        self.resultBox = QtWidgets.QGroupBox("result")
        mainSplitter.addWidget(self.resultBox)
        resultLayout = QtWidgets.QVBoxLayout(self.resultBox)
        
        self.commentFld = QtWidgets.QTextEdit()
        resultLayout.addWidget(self.commentFld)
        self.commentFld.setMinimumSize(400,100)
        self.commentFld.setMaximumHeight(100)

        self.commentFld.setEnabled(False)
        self.commentFld.setStyleSheet('QTextEdit{background-color: gray;color: white ;}')

        self.resultListView = QtWidgets.QListView()
        self.resultModel = QtGui.QStandardItemModel()
        self.resultListView.setModel(self.resultModel)
        self.resultListView.setMinimumSize(400,500)

        self.resultListView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.resultListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.resultListView.selectionModel().selectionChanged.connect(guiUtil.ApplyFunc(self.selectResult)) 

        resultLayout.addWidget(self.resultListView)
        self.refreshResult()

        mainSplitter.setStretchFactor(0, 0)
        mainSplitter.setStretchFactor(1, 1)
        
    def rebuildCheckList(self):
        for checkName in list(self.checkListGUI.keys()):
            for item in list(self.checkListGUI[checkName].keys()):
                self.checkListGUI[checkName][item].deleteLater()
            
        self.buildCheckList()
        self.refreshResult()

    def buildCheckList(self):
        self.checkListGUI = {}
        checkNameList = list(self.parent.CHECKLIST.keys())
        checkNameList.sort()
        
        for checkName in checkNameList:
            if checkName not in self.parent.PRESETDICT["checkList"]:
                continue
            
            checkLayout = QtWidgets.QHBoxLayout()
            checkLayout.setContentsMargins(0, 0, 0, 0)

            checkLayout.setSpacing(3)
            checkBox = QtWidgets.QLabel(checkName)
            checkBtn = QtWidgets.QPushButton("check")
            checkLayout.addWidget(checkBtn)
            resultBtn = QtWidgets.QPushButton("result")
            checkLayout.addWidget(resultBtn)
            resultBtn.setEnabled(False)

            correctBtn = QtWidgets.QPushButton("correct")
            checkLayout.addWidget(correctBtn)
            correctBtn.setEnabled(False)

            self.allCheckLayout.addRow(checkBox,checkLayout)
            self.checkListGUI[checkName] = {"checkBox":checkBox,"applyBtn":checkBtn, "resultBtn":resultBtn,"correctBtn":correctBtn,"checkLayout":checkLayout}

            checkBtn.clicked.connect(guiUtil.ApplyFunc(self.applyCheck,checkName))
            resultBtn.clicked.connect(guiUtil.ApplyFunc(self.showResult,checkName))
            correctBtn.clicked.connect(guiUtil.ApplyFunc(self.applyCorrect,checkName))

            if self.parent.CHECKLIST[checkName]["available"] == False:
                checkBtn.setEnabled(False)
                resultBtn.setEnabled(False)
                correctBtn.setEnabled(False)

    def applyCheck(self,checkName):
        topNode = self.rootNodeFld.read()
        if topNode == "":
            topNode = None

        if self.parent.CHECKLIST[checkName]["available"] == False:
            return

        result = []
        ldict = {"topNode":topNode}                
        result = execCheckCmd(checkName,ldict)
        result.sort()

        self.allResult[checkName] = result
        self.checkListGUI[checkName]["resultBtn"].setEnabled(True)
    
        if len(result) != 0:
            if checkName in self.parent.PRESETDICT["fatalContent"]:
                setButtonColor(self.checkListGUI[checkName]["resultBtn"],"hit")
            else:
                setButtonColor(self.checkListGUI[checkName]["resultBtn"],"warning")

            if self.parent.CHECKLIST[checkName]["correctCommand"]:
                self.checkListGUI[checkName]["correctBtn"].setEnabled(True)

        else:
            setButtonColor(self.checkListGUI[checkName]["resultBtn"],"clean")
            self.checkListGUI[checkName]["correctBtn"].setEnabled(False)

        self.resultBox.setTitle("result")
        self.showResult(checkName)
        return

    def applyCheckAll(self):
        topNode = self.rootNodeFld.read()
        if topNode == "":
            topNode = None

        for checkName in self.parent.PRESETDICT["checkList"]:
            result = []

            if self.parent.CHECKLIST[checkName]["available"] == False:
                continue
            
            ldict = {"topNode":topNode}
            result = execCheckCmd(checkName,ldict)
            result.sort()

            self.allResult[checkName] = result
            self.checkListGUI[checkName]["resultBtn"].setEnabled(True)

            if len(result) != 0:
                if checkName in self.parent.PRESETDICT["fatalContent"]:
                    setButtonColor(self.checkListGUI[checkName]["resultBtn"],"hit")
                else:
                    setButtonColor(self.checkListGUI[checkName]["resultBtn"],"warning")

                if self.parent.CHECKLIST[checkName]["correctCommand"]:
                    self.checkListGUI[checkName]["correctBtn"].setEnabled(True)

            else:
                setButtonColor(self.checkListGUI[checkName]["resultBtn"],"clean")
                self.checkListGUI[checkName]["correctBtn"].setEnabled(False)

            self.resultBox.setTitle("result")

    def applyCorrect(self,checkName):        
        modelIndex = self.resultListView.selectionModel().selectedIndexes()
        
        correctTargets = []
        for index in modelIndex:
            if cmds.objExists(self.resultModel.data(index)):
                correctTargets.append(self.resultModel.data(index))
        
        ldict = {"correctTargets":correctTargets}
        execCorrectCmd(checkName,ldict)
        self.applyCheck(checkName)

    def refreshResult(self):
        self.allResult = {}

        for checkName in list(self.checkListGUI.keys()):            
            setButtonColor(self.checkListGUI[checkName]["resultBtn"],"default")
            self.checkListGUI[checkName]["resultBtn"].setEnabled(False)
            self.checkListGUI[checkName]["correctBtn"].setEnabled(False)

        self.resultListView.selectionModel().blockSignals(True)
        self.resultModel.clear()
        self.resultListView.selectionModel().blockSignals(False)

    def showResult(self,checkName):
        self.resultListView.selectionModel().blockSignals(True)
        self.resultModel.clear()

        for i in range(0,len(self.allResult[checkName])):
            displayName = getDisplayName(self.allResult[checkName][i])
            item = QtGui.QStandardItem(displayName)
            self.resultModel.setItem(i, 0, item)

        self.resultListView.setEnabled(True)
        self.resultListView.selectionModel().blockSignals(False)

        self.resultBox.setTitle(checkName + " result")
        self.commentFld.setText(self.parent.CHECKLIST[checkName]["comment"])

    def selectResult(self):
        modelIndex = self.resultListView.selectionModel().selectedIndexes()
        if len(modelIndex) == 0:
            return 
        
        selectNodes = []
        for index in modelIndex:
            if cmds.objExists(self.resultModel.data(index)):
                selectNodes.append(self.resultModel.data(index))

        cmds.select(selectNodes, r =True,noExpand =True)

    def exportResult(self):

        if len(self.allResult) == 0:
            return

        resultExportToFile(self.allResult,self.parent.CURPRESET,self.parent.logExportPath)


class EditPresetDialog(QtWidgets.QDialog):
    def __init__(self,parent,*args, **kwargs):
        super(EditPresetDialog,self).__init__(parent,**kwargs)
        self.parent = parent

        self.setWindowTitle("edit checkList")
        self.setMinimumSize(400,500)
        # guiUtil.readStyleSheet(self)
        
        self.checkListBtns = {}
        mainLayout = QtWidgets.QVBoxLayout(self)
        
        self.checkListView = QtWidgets.QTreeView()
        self.toolListModle = QtGui.QStandardItemModel(0, 3)
        self.checkListView.setModel(self.toolListModle)
        self.toolListModle.setHeaderData(0, QtCore.Qt.Horizontal, 'listName')
        self.toolListModle.setHeaderData(1, QtCore.Qt.Horizontal, 'use')
        self.toolListModle.setHeaderData(2, QtCore.Qt.Horizontal, 'as fatal')
        
        self.checkListView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)        
        self.checkListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.checkListView.header().setStretchLastSection(False)
        self.checkListView.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.checkListView.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.checkListView.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

        self.checkListView.selectionModel().selectionChanged.connect(self.changeComment) 

        mainLayout.addWidget(self.checkListView)

        self.commentFld = QtWidgets.QTextEdit()
        mainLayout.addWidget(self.commentFld)
        self.commentFld.setMinimumSize(300,100)
        self.commentFld.setMaximumHeight(100)

        self.commentFld.setEnabled(False)
        self.commentFld.setStyleSheet('QTextEdit{background-color: gray;color: white ;}')

        saveBtnLayout = QtWidgets.QHBoxLayout()
        saveBtn = QtWidgets.QPushButton("save")
        saveAsBtn = QtWidgets.QPushButton("save as")
        cancelBtn = QtWidgets.QPushButton("cancel")
        saveBtnLayout.addWidget(saveBtn)
        saveBtnLayout.addWidget(saveAsBtn)
        saveBtnLayout.addWidget(cancelBtn)

        cancelBtn.clicked.connect(self.reject)
        saveAsBtn.clicked.connect(self.saveNewPreset)
        saveBtn.clicked.connect(self.savePreset)

        mainLayout.addLayout(saveBtnLayout)

        self.setItems()

    def setItems(self):
        checkNames = list(self.parent.CHECKLIST.keys())
        checkNames.sort()

        self.checkListBtns = {}
        
        for checkName in checkNames:            
            row = self.toolListModle.rowCount()
            useBtn = QtWidgets.QPushButton("use")
            useBtn.setCheckable(True)

            if checkName in self.parent.PRESETDICT["checkList"]:
                useBtn.setChecked(True)
            
            fatalBtn = QtWidgets.QPushButton("fatal")
            fatalBtn.setCheckable(True)
            if checkName in self.parent.PRESETDICT["fatalContent"]:
                fatalBtn.setChecked(True)

            self.toolListModle.setItem(row, 0, QtGui.QStandardItem(checkName))
            self.checkListView.setIndexWidget(self.toolListModle.index(row, 1), useBtn)
            self.checkListView.setIndexWidget(self.toolListModle.index(row, 2), fatalBtn)

            self.checkListBtns[checkName] = [useBtn,fatalBtn]

    def readItems(self):
        useItems = []
        fatalItems = []

        for checkName in list(self.checkListBtns.keys()):
            if self.checkListBtns[checkName][0].isChecked():
                useItems.append(checkName)

            if self.checkListBtns[checkName][1].isChecked():
                fatalItems.append(checkName)

        self.parent.PRESETDICT["checkList"] = useItems
        self.parent.PRESETDICT["fatalContent"] = fatalItems

        return useItems,fatalItems

    def savePreset(self):
        if self.parent.CURPRESET == "all":
            print("default cant overWrite")
            return

        accept = QtWidgets.QMessageBox.question(self,"save preset", self.parent.CURPRESET + " overWrite?",QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.No)
        
        if accept == 1024:
            self.readItems()            
            self.accept()

    def saveNewPreset(self):
        value,accept = QtWidgets.QInputDialog().getText(self,"save As","input presetName",QtWidgets.QLineEdit.Normal)

        if accept:
            if value == self.parent.CURPRESET:
                self.savePreset()

            elif value == "all":
                print("default cant overWrite")
                return
            
            self.parent.CURPRESET = value

            self.readItems()
            self.accept()

    def changeComment(self):
        modelIndex = self.checkListView.selectionModel().selectedIndexes()
        if len(modelIndex) == 0:
            self.commentFld.setText("")
            return 

        self.commentFld.setText(self.parent.CHECKLIST[self.toolListModle.data(modelIndex[0])]["comment"])


class MainGUI(QtWidgets.QMainWindow):
    def __init__(self,parent,withEditMode,objectName,*args, **kwargs):
        super(MainGUI,self).__init__(parent)
        # guiUtil.readStyleSheet(self)
        self.setObjectName(objectName)
        self.setWindowTitle(objectName)

        self.CURPRESET = "all"
        self.PRESETDICT = {    
                            "checkList": importModuleList(),
                            "fatalContent":[]
                        }
        self.CHECKLIST = {}
        self.logExportPath,self.presetPath,modulePath = getDefaultPath()        
        self.presetList = []

        menuBar = QtWidgets.QMenuBar(self)
        self.setMenuBar(menuBar)

        self.presetMenu = QtWidgets.QMenu('preset', menuBar)
        menuBar.addMenu(self.presetMenu)
        self.presetItems = []
        self.reloadPreset()
        self.loadCheckCommand()

        settingMenu = QtWidgets.QMenu('setting', menuBar)
        menuBar.addMenu(settingMenu)
        editExportPathAct = qaction("result export path", settingMenu)
        settingMenu.addAction(editExportPathAct)
        editExportPathAct.triggered.connect(self.editExportPath)

        resetSettingAct = qaction("reset setting", settingMenu)
        settingMenu.addAction(resetSettingAct)
        resetSettingAct.triggered.connect(self.resetOption)

        if withEditMode:
            self.editMenu = QtWidgets.QMenu('edit', menuBar)
            menuBar.addMenu(self.editMenu)

            editPresetAct = qaction("editPreset", self.editMenu)
            self.editMenu.addAction(editPresetAct)
            editPresetAct.triggered.connect(self.editPreset)

        self.checkWidget = CheckerGUI(self)
        self.setCentralWidget(self.checkWidget)
        self.loadOption()
        self.loadPreset()

    def resetOption(self):        
        self.logExportPath,presetPath,modulePath = getDefaultPath()  
        self.CURPRESET = "all"
        self.saveOption()
        self.loadPreset()

    def loadOption(self):        
        optionDict = editScenes.readDictOptionVar(self.objectName())

        if "CURPRESET" in list(optionDict.keys()):
            self.CURPRESET = optionDict["CURPRESET"]

            if self.CURPRESET not in self.presetList:
                self.CURPRESET = "all"
                        
        if "logExportPath" in list(optionDict.keys()):
            self.logExportPath = optionDict["logExportPath"]
        
    def saveOption(self):
        optionDict = {
                        "CURPRESET":        self.CURPRESET,
                        "logExportPath":    self.logExportPath
                    }
        
        editScenes.saveDictOptionVar(self.objectName(),optionDict)

    def editExportPath(self):        
        dialog = guiUtil.SelectPathDialog(self,"setting - logExportPath",self.logExportPath)

        if dialog.exec_():
            self.logExportPath = editFiles.checkPathString(dialog.inputPath)
            self.saveOption()


    def editPreset(self):        
        dialog = EditPresetDialog(parent = self)
        
        if dialog.exec_():
            self.saveCURPRESET()
            self.clearPreset()
            self.reloadPreset()
            self.loadPreset()

    def saveCURPRESET(self):        
        presetFilePath = self.presetPath + self.CURPRESET + ".json"
        editFiles.writeJSON(presetFilePath,self.PRESETDICT)

    def clearPreset(self):
        for item in self.presetItems:
            try:
                item.deleteLater()
            except:
                pass

    def reloadPreset(self):
        presetFiles = getPresetList(self.presetPath)
        presetAction = qaction("all", self.presetMenu)
        self.presetItems.append(presetAction)
        self.presetMenu.addAction(presetAction)
        presetAction.triggered.connect(guiUtil.ApplyFunc(self.changePreset,"all"))
        self.presetList = ["all"]

        for file in presetFiles:
            presetName = file.replace(".json","")
            presetAction = qaction(presetName, self.presetMenu)
            self.presetItems.append(presetAction)
            self.presetMenu.addAction(presetAction)
            presetAction.triggered.connect(guiUtil.ApplyFunc(self.changePreset,presetName))
            self.presetList.append(presetName)

    def changePreset(self,presetName):
        if self.CURPRESET == presetName:
            return
        self.CURPRESET = presetName
        self.loadPreset()

    def loadPreset(self):
        self.setWindowTitle(self.objectName() + "  " + self.CURPRESET)        
        if self.CURPRESET == "all":
            self.PRESETDICT = {"checkList": importModuleList(),"fatalContent":[]}
        else:
            presetFilePath = self.presetPath + self.CURPRESET + ".json"
            self.PRESETDICT = editFiles.readJSON(presetFilePath,None)

        self.checkWidget.rebuildCheckList()
        self.saveOption()

    def loadCheckCommand(self):        
        moduleNameList = importModuleList()

        for moduleName in moduleNameList:
            comment,existCorrect,available = getCheckComment(moduleName)            
            self.CHECKLIST[moduleName] = {
                                        "comment":comment,
                                        "correctCommand":existCorrect,
                                        "available":available
            }
    
##main----------------------------------------
def main(withEditMode = True):
    objectName = "SSCheckTool"
    mayaMainWindow = guiUtil.getTopLevelWidget('MayaWindow')
    guiUtil.windowCheck(objectName,mayaMainWindow)
    mainGUI = MainGUI(mayaMainWindow,withEditMode,objectName)
        
    mainGUI.show()
    mainGUI.move(300,50)



# coding=utf-8
from __future__ import (absolute_import, division,print_function)
import subprocess
import os
import sys
import pathlib
import re
try:
    from PySide2 import QtWidgets,QtGui,QtCore
    qaction = QtWidgets.QAction

except:
    from PySide6 import QtWidgets,QtGui,QtCore
    qaction = QtGui.QAction

try:
    from importlib import reload
except:
    pass

PROXY_FILTER_ROLE = QtCore.Qt.UserRole + 1

##------------------------------------------------------------------------------
##import for maya
##------------------------------------------------------------------------------
mayaVer = None
executable = sys.executable
if executable.endswith("maya.exe") or executable.endswith("mayabatch.exe"):
    import maya.cmds as cmds    
    mayaVer = cmds.about(version=True)

    from . import editScenes
    reload(editScenes)


##-----------------------------------------------------------------
##
##-----------------------------------------------------------------
def getTopLevelWidget(name):
    for widget in QtWidgets.QApplication.topLevelWidgets():    
        if widget.objectName() == name:
            return widget
    return None

def windowCheck(object,parent,arrowMulti = False):
    if arrowMulti:        
        allChildrenName = []
        renameObject = str(object)
        for child in parent.children():
            allChildrenName.append(child.objectName())
        
        i = 1
        
        while renameObject in allChildrenName:
            renameObject = object + str(i)
            i = i+1
                
        return renameObject
            
    else:
        for child in parent.children():
            if child.objectName() == object:
                child.deleteLater()

        return object

def readStyleSheet(object,fileName = "style"):    
    dirPath = os.path.dirname(__file__)        
    dirPath.replace(os.path.sep, '/')
    path = dirPath +"/" +fileName +'.qss'
        
    try:
        with open(path, 'r') as f:
            style = f.read()
    except:
        style = ''

    object.setStyleSheet(style)


class ApplyFunc(object):
    def __init__(self, func, *args, **kwargs):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
                        
    def __call__(self, *args, **kwargs):
        error = None        
        try:
            if mayaVer != None:
                cmds.undoInfo(openChunk =True)

            self.__func(*self.__args, **self.__kwargs)			
                        
        except Exception as e:
            import traceback
            traceback.print_exc()

        finally:
            if mayaVer != None:
                cmds.undoInfo(closeChunk =True)

def addHelpMenu(menuBar,manualPath):
    helpMenu = QtWidgets.QMenu('help', menuBar)
    menuBar.addMenu(helpMenu)
    
    helpAct = QtWidgets.QAction("manual", helpMenu)
    helpMenu.addAction(helpAct)
    helpAct.triggered.connect(ApplyFunc(callManual,manualPath))

def callManual(manualPath):
    if os.path.exists(manualPath):
        print("<<open manual>>")
        subprocess.Popen([manualPath], shell=True)

##-----------------------------------------------------------------
##GUI parts
##-----------------------------------------------------------------
class IconButton(QtWidgets.QPushButton):
    def __init__(self,image,imageSize,toolTip,*args,**kwargs):
        super(IconButton,self).__init__(*args,**kwargs)    

        self.setIcon(QtGui.QPixmap(image))
        self.setToolTip(toolTip)
        self.setFixedSize(imageSize,imageSize)
        self.setIconSize(QtCore.QSize(imageSize,imageSize))        
        

class FilePathField(QtWidgets.QWidget):
    itemChanged = QtCore.Signal(str)

    def __init__(self,mode = "directory",createBtns = ["set","clear"],filter = "Any files (*)",*args,**kwargs):
        super(FilePathField,self).__init__(*args,**kwargs)

        # self.setAcceptDrops(True)

        self.mode = mode
        self.filter = filter
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.field = QtWidgets.QLineEdit()
        self.layout.addWidget(self.field)

        if "set" in createBtns:
            self.setBtn = QtWidgets.QPushButton("set")
            self.layout.addWidget(self.setBtn)
            self.setBtn.clicked.connect(self.selectItem)
            self.setBtn.setMinimumWidth(40)
            self.setBtn.setMaximumWidth(40)

        if "open" in createBtns:
            self.openBtn = QtWidgets.QPushButton("open")
            self.layout.addWidget(self.openBtn)    
            self.openBtn.clicked.connect(self.openDirctory)
            self.openBtn.setMinimumWidth(40)
            self.openBtn.setMaximumWidth(40)

        if "clear" in createBtns:
            self.clearBtn = QtWidgets.QPushButton("clear")
            self.layout.addWidget(self.clearBtn)    
            self.clearBtn.clicked.connect(self.clearItem)
            self.clearBtn.setMinimumWidth(40)
            self.clearBtn.setMaximumWidth(40)
    
    def dragEnterEvent(self,event):        
        mime = event.mimeData()

        if mime.hasUrls() == True:
            event.accept()
        else:
            event.ignore()

    def dropEvent( self, event ):
        mimedata = event.mimeData()
 
        if mimedata.hasUrls():
            urllist = mimedata.urls()

            addFiles = []
            for url in urllist:
                path = url.toLocalFile()
                inputPath = pathlib.Path(path)

                if inputPath.is_dir():
                    for childPath in inputPath.iterdir():
                        addFiles.append(str(childPath).replace(os.path.sep, '/'))

                else:
                    addFiles.append(path.replace(os.path.sep, '/'))
        
            self.setItem(addFiles[0])

    def selectItem(self):
        curPath = self.field.text()
        
        if os.path.isdir(curPath) ==False:
            curPath = os.path.dirname(curPath)

        if self.mode == "directory":
            fileDialog = QtWidgets.QFileDialog.getExistingDirectory(self, "select Directory",curPath)
            
            if fileDialog == "":
                return
            
            targetPath = fileDialog.replace(os.path.sep, '/')
            if targetPath.endswith("/") ==False:
                targetPath = targetPath+ "/"
                
            self.field.setText(targetPath)
            self.itemChanged.emit(targetPath)


        elif self.mode == "file":

            if self.filter == None:
                fileDialog,accept = QtWidgets.QFileDialog.getOpenFileName(self, "select file",curPath)
            else:
                fileDialog,accept = QtWidgets.QFileDialog.getOpenFileName(self, "select file",curPath,self.filter)
            
            if accept == False or fileDialog == "":
                return
            
            targetPath = fileDialog.replace(os.path.sep, '/')
            self.field.setText(targetPath)
            self.itemChanged.emit(targetPath)

    def setItem(self,object,block = False):

        if block:
            self.field.blockSignals(True)
            self.blockSignals(True)

        self.field.setText(object)

        if block:
            self.field.blockSignals(False)
            self.blockSignals(False)

    def clearItem(self):
        self.field.setText("")

    def openDirctory(self):
        path = self.field.text()
        path = path.replace("/",os.path.sep)
        
        if os.path.isdir(path):   
            
            if mayaVer in ["2020","2019"]:
                path = b'explorer ' + path.encode("mbcs")

            else:
                path = 'explorer ' + path

            subprocess.Popen(path,shell =True)
            

    def read(self):
        return self.field.text()


class CompoundDoubleSpinBox(QtWidgets.QWidget):
    def __init__(self,num,*args,**kwargs):
        super(CompoundDoubleSpinBox,self).__init__(*args,**kwargs)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.boxNum = num
        self.boxList = []

        for i in range(0,self.boxNum):
            box = QtWidgets.QDoubleSpinBox()
            box.setRange(-9999,9999)
            self.layout.addWidget(box)
            self.boxList.append(box)

    def getValues(self):
        values = []

        for i in range(0,self.boxNum):            
            values.append(self.boxList[i].value())

        return values

    def setValues(self,values):
        for i in range(0,self.boxNum):
            self.boxList[i].setValue(values[i])

class ComboBox(QtWidgets.QWidget):
    def __init__(self,data,*args,**kwargs):
        super(ComboBox,self).__init__(*args,**kwargs)

        self.data = data
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.box = QtWidgets.QComboBox()
        self.layout.addWidget(self.box)

        for item in self.data:
            self.box.addItem(item)    

        self.box.update()

    def setData(self,data,block = True):
        self.clearItems()

        if block:
            self.box.blockSignals(True)

        self.data = data
        for item in self.data:
            self.box.addItem(item)

        self.box.update()
        if block:
            self.box.blockSignals(False)
    
    def clearItems(self):

        self.box.blockSignals(True)
        self.box.clear()
        self.box.update()
        self.box.blockSignals(False)

    def readText(self):
        return self.box.currentText()			
        
    def readIndex(self):
        return self.box.currentIndex()
        
    def selectText(self,text,block=False):
        
        if block:
            self.box.blockSignals(True)
        
        if text in self.data:
            self.box.setCurrentIndex(self.data.index(text))
    
        if block:
            self.box.blockSignals(False)

    def selectIndex(self,index):
        self.box.setCurrentIndex(index)


class ViewportPickWidget(QtWidgets.QWidget):
    def __init__(self,parent,*args, **kwargs):
        super(ViewportPickWidget,self).__init__(*args,**kwargs)
        readStyleSheet(self)
        self.parent = parent
        self.viewPortSelect = RadioButton(["cur","sel"],"push",[30,20])        
        self.setLayout(self.viewPortSelect.layout)
        self.viewPortSelect.setSelectText("cur")        
        self.viewPortSelect.radioGP.buttonClicked.connect(self.changeViewPortType)
        self.viewPortSelect.layout.setSpacing(3)
        self.viewPortNameFld = QtWidgets.QLineEdit()        
        self.viewPortSelect.layout.addWidget(self.viewPortNameFld)
        self.viewPortNameFld.setMaximumWidth(200)

        pickBtn = QtWidgets.QPushButton("pick")
        pickBtn.setMaximumWidth(80)
        self.viewPortSelect.layout.addWidget(pickBtn)
        pickBtn.clicked.connect(self.pickViewport)
        self.viewPortSelect.layout.addStretch()

        self.changeViewPortType()

    def changeViewPortType(self):
        viewPortType = self.viewPortSelect.readSelectedText()

        if viewPortType == "cur":
            self.viewPortNameFld.setEnabled(False)

        elif viewPortType == "sel":
            self.viewPortNameFld.setEnabled(True)

        self.setTargetViewPort()

    def pickViewport(self):
        viewPort = editScenes.getCurViewPanel()
        self.viewPortNameFld.setText(viewPort)

        self.setTargetViewPort()
    
    def setTargetViewPort(self):
        viewPortType = self.viewPortSelect.readSelectedText()

        if viewPortType == "cur":
            self.targetViewPort = None

        elif viewPortType == "sel":
            self.targetViewPort = self.viewPortNameFld.text()                   

        self.parent.targetViewPort = self.targetViewPort

class RadioButton(QtWidgets.QWidget):
    def __init__(self,options,btnType,btnSize = [60,20],rowLimitNum = None,*args,**kwargs):
        super(RadioButton,self).__init__(*args,**kwargs)

        self.options = options
        self.buttons = {}
        self.type = btnType
        self.btnSize = btnSize
        self.rowLimitNum = rowLimitNum

        if rowLimitNum ==None:
            self.layout = QtWidgets.QHBoxLayout(self)
        else:
            self.layout = QtWidgets.QVBoxLayout(self)

        self.layoutList = []

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()
        self.radioGP = QtWidgets.QButtonGroup()
        self.setItems()
        self.radioGP.setExclusive(True)
    
    def setEnabled(self,enable):
        for button in self.buttons.values():
            button.setEnabled(enable)

    def clearItems(self):
        for button in self.buttons.values():
            self.radioGP.removeButton(button)
            button.hide()
            button.deleteLater()

        self.buttons = {}

    def setItems(self):
        self.clearItems()

        for i in range(0,len(self.options)):
            option = self.options[i]
            if self.type == "radio":
                widget = QtWidgets.QRadioButton(option)                
                
            elif self.type == "push":
                widget = QtWidgets.QPushButton(option)            
                widget.setFixedSize(self.btnSize[0],self.btnSize[1])                
                widget.setCheckable(True)
            
            if self.rowLimitNum ==None:
                self.layout.insertWidget(i,widget)

            else:
                rowNumber = i // self.rowLimitNum
                rowIndex = i % self.rowLimitNum

                if len(self.layoutList) < rowNumber + 1:
                    subLayout = QtWidgets.QHBoxLayout()
                    subLayout.addStretch()
                    self.layout.addLayout(subLayout)
                    subLayout.setContentsMargins(0, 0, 0, 0)
                    self.layoutList.append(subLayout)
                
                self.layoutList[rowNumber].insertWidget(rowIndex,widget)

            self.radioGP.addButton(widget,i)
            self.buttons[option] = widget

    def readSelectedText(self):

        if self.radioGP.checkedId() != -1:
            return self.options[self.radioGP.checkedId()]
        
        else:
            return ""
    
    def setSelectText(self,value,block=False):
        if block:
            self.radioGP.blockSignals(True)

        for i in range(0,len(self.options)):
            if value == self.options[i]:
                button = self.radioGP.button(i)
                button.setChecked(True)

        if block:
            self.radioGP.blockSignals(False)


class AttachWidgets(QtWidgets.QScrollArea):
    changeCurFile = QtCore.Signal(True)
    dropedFiles = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(AttachWidgets,self).__init__(parent)
        readStyleSheet(self)
        self.setAcceptDrops(True)
        self.imageBtns = {}
        self.files = {}
        self.curFile = ""
        self.setFixedWidth(220)
        self.setWidgetResizable(True)
        
        innerWidget = QtWidgets.QWidget()
        self.setWidget(innerWidget)
        innerWidget.setStyleSheet("background:#0e1c24;")
        self.imageBtnLayout = QtWidgets.QVBoxLayout(innerWidget)
        self.imageBtnLayout.setAlignment(QtCore.Qt.AlignTop)

    def dragEnterEvent(self,event):        
        mime = event.mimeData()

        if mime.hasUrls() == True:
            event.accept()
        else:
            event.ignore()

    def dropEvent( self, event ):
        mimedata = event.mimeData()
 
        if mimedata.hasUrls():
            urllist = mimedata.urls()

            addFiles = []
            for url in urllist:
                path = url.toLocalFile()
                inputPath = pathlib.Path(path)

                if inputPath.is_dir():
                    for childPath in inputPath.iterdir():
                        addFiles.append(str(childPath).replace(os.path.sep, '/'))

                else:
                    addFiles.append(path.replace(os.path.sep, '/'))
        
            self.addimageBtns(addFiles)

    def addimageBtns(self,images):
        addFilePath = []
        for image in images:
            filePath = image.replace(os.path.sep, '/')
            inputPath = pathlib.Path(filePath)

            if inputPath.is_dir():            
                continue

            if filePath in list(self.files.values()):
                continue

            fileName = inputPath.name
            addImageBtn = QtWidgets.QPushButton(fileName)
            addImageBtn.setFixedSize(200,20)
            addImageBtn.clicked.connect(ApplyFunc(self.setCurFile,fileName))
            readStyleSheet(addImageBtn)
     
            self.imageBtnLayout.addWidget(addImageBtn)                         
            self.imageBtns[fileName] = addImageBtn
            self.files[fileName] = filePath
            addFilePath.append(filePath)

        self.dropedFiles.emit(addFilePath)

    def setCurFile(self,fileName):
        self.curFile = fileName
        self.changeCurFile.emit()

    def removeFile(self,fileName):
        btn = self.imageBtns[fileName]
        
        btn.hide()
        btn.deleteLater()
        
        self.imageBtns.pop(fileName)
        self.files.pop(fileName)


class CommentFild(QtWidgets.QTextEdit):
    def __init__(self,*args,**kwargs):
        super(CommentFild,self).__init__(*args,**kwargs)
        readStyleSheet(self)
        self.setAcceptDrops(True)

    def dragEnterEvent(self,event):        
        mimedata = event.mimeData()
        
        if mimedata.hasUrls() == True:
            event.accept()
        else:
            event.ignore()

    def dropEvent( self, event ):
        mimedata = event.mimeData()
        
        contens = self.toPlainText()

        for url in mimedata.urls():            
            path = url.toLocalFile()
            
            filePath = pathlib.Path(path)
            
            if filePath.is_dir():
                continue
        
            if ".txt" in filePath.suffixes:
                with open(path, encoding="utf8", errors='ignore') as f:
                    contens += f.read() + "\n"
            
            else:
                contens += path + "\n"

            self.setPlainText(contens)
##------------------------------------------------------------------------------------
##customListView
##------------------------------------------------------------------------------------
class ListView(QtWidgets.QWidget):
    def __init__(self,layoutDir = "H",*args,**kwargs):
        super(ListView,self).__init__(*args,**kwargs)

        if layoutDir == "H":
            self.layout = QtWidgets.QHBoxLayout(self)
        
        elif layoutDir == "V":
            self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.view = QtWidgets.QListView()
        self.model = StandardItemModel()
        self.view.setModel(self.model)
        self.layout.addWidget(self.view)

        self.data = []
        self.filterString = ""
        self.filteredData = []
    
    def updateData(self):
        self.model.clear()
        self.filteredData = [s for s in self.data if re.match(self.filterString, s)]
        
        for i in range(0,len(self.filteredData)):
            self.model.setItem(i, 0, QtGui.QStandardItem(self.filteredData[i]))

    def setFilterData(self,filterString):
        self.filterString = filterString
        self.view.selectionModel().blockSignals(True)
        self.updateData()        
        self.view.selectionModel().blockSignals(False)

    def clearData(self):
        self.data = []
        self.view.selectionModel().blockSignals(True)
        self.updateData()        
        self.view.selectionModel().blockSignals(False)

    def setData(self,data):
        self.data = data
        self.view.selectionModel().blockSignals(True)
        self.updateData()
        self.view.selectionModel().blockSignals(False)

    def addData(self,data):
        self.view.selectionModel().blockSignals(True)        
        self.data.extend(data)
        self.updateData()
        self.view.selectionModel().blockSignals(False)

    def setSelectItem(self,items):
        self.view.selectionModel().blockSignals(True)
        self.view.selectionModel().clearSelection()

        selected = False

        for i in range(0,self.model.rowCount()):
            if self.model.index(i,0).data() in items:                
                self.view.selectionModel().select(self.model.index(i,0),QtCore.QItemSelectionModel.Select)
                self.view.selectionModel().setCurrentIndex(self.model.index(i,0),QtCore.QItemSelectionModel.Select)                                
                selected = True
        
        self.view.selectionModel().blockSignals(False)
        return selected

    def setScroll(self):
        modelIndex = self.view.selectionModel().selectedIndexes()
        
        if len(modelIndex) == 0:
            return
        
        self.view.scrollTo(modelIndex[0], QtWidgets.QAbstractItemView.PositionAtTop)                

    def clearSelection(self):
        self.view.selectionModel().blockSignals(True)
        self.view.selectionModel().clearSelection()
        self.view.selectionModel().blockSignals(False)

    def selectedItem(self):
        modelIndex = self.view.selectionModel().selectedIndexes()
        
        items = []
        for index in modelIndex:
            items.append(self.model.data(index))

        return items

    def allData(self):
        items = []

        for i in range(0,self.model.rowCount()):
            items.append(self.model.index(i,0).data())

        return items

class StandardItemModel(QtGui.QStandardItemModel):
    def __init__(self,*args,**kwargs):
        super(StandardItemModel,self).__init__(*args,**kwargs)
        self.conditions = None
        self.cndColors = {
                            False :QtGui.QColor("#ed4407"),
                            True:QtGui.QColor("#ffffff")
                        }

    def setCondition(self,conditions):        
        self.conditions = conditions
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def data(self, index, role=QtGui.Qt.DisplayRole,*args,**kwargs):
        
        if self.conditions != None and role == QtGui.Qt.TextColorRole:            
            text = index.data(QtGui.Qt.DisplayRole)
            
            for key in list(self.conditions.keys()):
                if text in self.conditions[key]:
                    return self.cndColors[key]
        
        try:
            return super(StandardItemModel, self).data(index, role)
        except:
            return None

##------------------------------------------------------------------------------------
##customTreeView
##------------------------------------------------------------------------------------
class BaseItem(object):
    def __init__(self, data):
        self._data = data
        self._columncount = 1
        self._children = []
        self._parent = None

    def data(self,column):
        if hasattr(self, '_data') == False:
            return ""
        
        if self._data == None:
            return ""

        return self._data

    def columnCount(self):
        return 1
    
    def childCount(self):
        return len(self._children)

    def child(self,row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        if hasattr(self, '_parent'):
            return self._parent
        
    def row(self):
        if self._parent:

            if self in self._parent._children:
                return self._parent._children.index(self)
            else:
                return 0
        
        else:
            return 0

    def addChild(self,child):
        child._parent = self
        self._children.append(child)

def createItems(item,itemList,allkeys,nodes,topItems):
    if item["parent"] == "":
        treeItem = BaseItem(item["key"])
        nodes[item['key']] = treeItem
        topItems.append(treeItem)
        return

    elif item["parent"] not in allkeys:
        treeItem = BaseItem(item["key"])
        nodes[item['key']] = treeItem
        topItems.append(treeItem)
        return

    elif item["parent"] in list(nodes.keys()):
        parent = nodes[item["parent"]]

    else:
        parentIndex = allkeys.index(item["parent"])
        parentItem = itemList[parentIndex]
        createItems(parentItem,allkeys,nodes,topItems)
        parent = nodes[item["parent"]]

    treeItem = BaseItem(item["key"])
    parent.addChild(treeItem)
    nodes[item['key']] = treeItem

class TreeItem(BaseItem):
    def __init__(self, data):
        super(TreeItem,self).__init__(data)

class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self,nodes,*args, **kwargs):
        QtCore.QAbstractItemModel.__init__(self)

        self._root  = BaseItem(None)
        self.page = 0
        self.showItemCount = 20
        self.__items = nodes

        self.setupModelData()

    def rowCount(self, index):
        if index.column() > 0:
            return 0

        if index.isValid():
            return index.internalPointer().childCount()
        else:
            return self._root.childCount()

    def addChild(self,node,_parent):
        if not _parent or not _parent.isValid():
            parent = self._root 

        else:
            parent = _parent.internalPointer()
        
        parent.addChild(node)

    def index(self,row,column,_parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root 

        else:
            parent = _parent.internalPointer()

        if not self.hasIndex(row,column,_parent):
            return QtCore.QModelIndex()
        

        child = parent.child(row)

        if child:
            return self.createIndex(row,column,child)        
        else:
            return QtCore.QModelIndex()

    def parent(self,index):
        if not index.isValid():
            return QtCore.QModelIndex()

        chItem = index.internalPointer()
        parentItem = chItem.parent()

        if parentItem == self._root:
            return QtCore.QModelIndex()

        if parentItem == None:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentItem.row(),0,parentItem)

    def columnCount(self,index):
        if index.isValid():
            return index.internalPointer().columnCount()
        
        else:
            return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None
        
        if role == PROXY_FILTER_ROLE:            
            return item.data(index.column())
        
        item = index.internalPointer()
        return item.data(index.column())

    def getTree(self,index,role,tree):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None
        
        item = index.internalPointer()
        parentItem = item.parent()
        tree.insert(0,item.data(index.column()))

        if parentItem != self._root:
            self.getTree(self.createIndex(parentItem.row(),0,parentItem),role,tree)
        
        return tree

    def flags(self, index): 
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section , orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._root.data(section)

        return None


    def setItems(self, items):
        self.__items = items
        self.setupModelData()

    def setupModelData(self):
        for item in self.__items:
            self._root.addChild(item)
        self.layoutChanged.emit()

    def clearItems(self):
        self._root._children = []
        self.layoutChanged.emit()        


class TreeView(QtWidgets.QWidget):
    
    def __init__(self,headers,*args,**kwargs):
        super(TreeView,self).__init__(*args,**kwargs)
        readStyleSheet(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.view = QtWidgets.QTreeView(self)
        self.view.setSortingEnabled(True)        
        self.data = {}
        
        # self.view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.view)
                
        self.headers = headers
        
        self.model = StandardItemModel(0,len(self.headers))
        
        self.view.setModel(self.model)

        for i in range(0,len(self.headers)):
            self.model.setHeaderData(i, QtCore.Qt.Horizontal,self.headers[i])
        
        for i in range(0,len(self.headers)):
            
            if i == 0:
                self.view.header().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
            else:
                self.view.header().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)                
        
        self.view.header().setStretchLastSection(False)

    def setData(self,data,blockSignals =True):
        if blockSignals:
            self.model.blockSignals(True)
        
        self.view.selectionModel().clearSelection()
  
        self.model.removeRows(0, self.model.rowCount())
        keys = list(data.keys())
        keys.sort()
        
        for i in range(0,len(keys)):
            dataDict = data[keys[i]]
            
            for ii in range(0,len(self.headers)):
                if self.headers[ii] in list(dataDict.keys()):                
                    item = QtGui.QStandardItem(str(dataDict[self.headers[ii]]))
                    self.model.setItem(i, ii, item)

        if blockSignals:
            self.model.blockSignals(False)
        self.model.layoutChanged.emit()

    def addData(self,data,blockSignals =True):
        if blockSignals:
            self.model.blockSignals(True)
      
        self.view.selectionModel().clearSelection()          
        keys = list(data.keys())
        keys.sort()
        
        cuRows = self.model.rowCount()

        for i in range(0,len(keys)):            
            dataDict = data[keys[i]]
            
            for ii in range(0,len(self.headers)):
                if self.headers[ii] in list(dataDict.keys()):                
                    item = QtGui.QStandardItem(str(dataDict[self.headers[ii]]))
                    self.model.setItem(i+cuRows, ii, item)

        if blockSignals:
            self.model.blockSignals(False)

        self.model.layoutChanged.emit()
    
    def clearData(self,blockSignals =True):
        if blockSignals:
            self.model.blockSignals(True)
        
        self.view.selectionModel().clearSelection()  
        self.model.removeRows(0, self.model.rowCount())
        
        if blockSignals:
            self.model.blockSignals(False)

        self.model.layoutChanged.emit()

    def selectedItem(self):        
        self.model.blockSignals(True)
        self.view.selectionModel().blockSignals(True)

        indexes = self.view.selectionModel().selectedRows(0)

        data = []

        if len(indexes) == 0:
            self.view.selectionModel().blockSignals(False)
            self.model.blockSignals(False)
            return []
        
        for index in indexes:
            itemDict = {}
            row = index.row()
            for i in range(0,len(self.headers)):                
                value = self.model.data(self.model.index(row,i))
                itemDict[self.headers[i]] = value
            
            data.append(itemDict)

        self.view.selectionModel().blockSignals(False)
        self.model.blockSignals(False)
        return data

    def allItems(self):
        self.model.blockSignals(True)
        self.view.selectionModel().blockSignals(True)
        
        data = []
        
        for row in range(0,self.model.rowCount()):        
            itemDict = {}
            
            for i in range(0,len(self.headers)):                
                value = self.model.data(self.model.index(row,i))
                itemDict[self.headers[i]] = value
            
            data.append(itemDict)

        self.view.selectionModel().blockSignals(False)
        self.model.blockSignals(False)
        return data

    def setSelectItem(self,key,values):
        self.model.blockSignals(True)
        self.view.selectionModel().blockSignals(True)
        self.view.selectionModel().clearSelection()

        selected = False

        for i in range(0,self.model.rowCount()):
            keyIndex = self.headers.index(key)
        
            if self.model.index(i,keyIndex).data() in values:
                
                for ii in range(0,len(self.headers)):
                    self.view.selectionModel().select(self.model.index(i,ii),QtCore.QItemSelectionModel.Select)
                self.view.selectionModel().setCurrentIndex(self.model.index(i,0),QtCore.QItemSelectionModel.Select)
                selected = True
                

        self.view.selectionModel().blockSignals(False)
        self.model.blockSignals(False)
        return selected

    def editRows(self, editedItem):
        self.model.blockSignals(True)
        self.view.selectionModel().blockSignals(True)

        editedIndex = editedItem.index()        
        value = self.model.data(editedIndex)
        col = editedIndex.column()

        indexes = self.view.selectionModel().selectedRows(0)
        
        if len(indexes) != 0:                    
            for index in indexes:
                row = index.row()
                self.model.item(row,col).setText(value)

        self.model.blockSignals(False)
        self.view.selectionModel().blockSignals(False)   
    
    def clearSelection(self):
        self.view.selectionModel().blockSignals(True)
        self.view.selectionModel().clearSelection()
        self.view.selectionModel().blockSignals(False)
##------------------------------------------------------------------------------------
##AttrEditWidget
##------------------------------------------------------------------------------------

##-----------------------------------------------------------------------------------------------
##dialog
##-----------------------------------------------------------------------------------------------
# class ProgressDialog():



class ReportDialog(QtWidgets.QDialog):
    def __init__(self,parent,message,*args,**kwargs):
        super(ReportDialog, self).__init__(parent= parent)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimumSize(300,100)
        
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(QtWidgets.QLabel(message))
        
        buttonLayout =QtWidgets.QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        acceptBtn = QtWidgets.QPushButton("OK")
        buttonLayout.addWidget(acceptBtn)
        
        acceptBtn.clicked.connect(self.apply)        

    def apply(self):
        self.accept()

class AskDialog(QtWidgets.QDialog):
    def __init__(self,parent,message,*args,**kwargs):
        super(AskDialog, self).__init__(parent= parent)	        
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimumSize(300,100)
        mainLayout = QtWidgets.QVBoxLayout(self)
        # mainLayout.addWidget(QtWidgets.QLabel("create Dirs?"))
        mainLayout.addWidget(QtWidgets.QLabel(message))
        
        buttonLayout =QtWidgets.QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        acceptBtn = QtWidgets.QPushButton("OK")
        buttonLayout.addWidget(acceptBtn)
        cancelBtn = QtWidgets.QPushButton("Cancel")
        buttonLayout.addWidget(cancelBtn)

        acceptBtn.clicked.connect(self.apply)
        cancelBtn.clicked.connect(self.cancel)

    def cancel(self):
        self.reject()

    def apply(self):
        self.accept()

class InputStringDialog(QtWidgets.QDialog):
    def __init__(self,parent,title,default,*args, **kwargs):
        super(InputStringDialog,self).__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500,100)
        readStyleSheet(self)

        self.inputString = ""

        mainLayout = QtWidgets.QVBoxLayout(self)
        self.inputStringFld = QtWidgets.QLineEdit(default)

        mainLayout.addWidget(self.inputStringFld)
        
        ##-------------------------------------
        saveBtnLayout = QtWidgets.QHBoxLayout()
        saveBtn = QtWidgets.QPushButton("ok")
        cancelBtn = QtWidgets.QPushButton("cancel")
        saveBtnLayout.addWidget(saveBtn)        
        saveBtnLayout.addWidget(cancelBtn)

        cancelBtn.clicked.connect(self.reject)        
        saveBtn.clicked.connect(self.savePath)

        mainLayout.addLayout(saveBtnLayout)

    def savePath(self):  
        if self.inputStringFld.text() == "":
            self.reject()

        self.inputString = self.inputStringFld.text()
        self.accept()

class SelectItemDialog(QtWidgets.QDialog):
    def __init__(self,parent,title,items,*args, **kwargs):
        super(SelectItemDialog,self).__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500,100)
        readStyleSheet(self)
        self.selectedItem = None

        mainLayout = QtWidgets.QVBoxLayout(self)

        self.selectList = ComboBox(items)

        mainLayout.addWidget(self.selectList)
        
        saveBtnLayout = QtWidgets.QHBoxLayout()
        saveBtn = QtWidgets.QPushButton("select")
        cancelBtn = QtWidgets.QPushButton("cancel")
        saveBtnLayout.addWidget(saveBtn)        
        saveBtnLayout.addWidget(cancelBtn)

        cancelBtn.clicked.connect(self.reject)        
        saveBtn.clicked.connect(self.apply)

        mainLayout.addLayout(saveBtnLayout)

    def apply(self):        
        self.selectedItem = self.selectList.readText()
        self.accept()

class SelectNamespaceDialog(QtWidgets.QDialog):
    def __init__(self,parent,title,*args, **kwargs):
        super(SelectNamespaceDialog,self).__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500,100)
        readStyleSheet(self)              
        mainLayout = QtWidgets.QVBoxLayout(self)

        self.namespaceFld = NameSpaceList([])
        self.namespaceFld.reloadNameSpace()

        mainLayout.addWidget(self.namespaceFld)

        saveBtnLayout = QtWidgets.QHBoxLayout()
        saveBtn = QtWidgets.QPushButton("select")
        cancelBtn = QtWidgets.QPushButton("cancel")
        saveBtnLayout.addWidget(saveBtn)        
        saveBtnLayout.addWidget(cancelBtn)

        cancelBtn.clicked.connect(self.reject)        
        saveBtn.clicked.connect(self.selectnamespace)

        mainLayout.addLayout(saveBtnLayout)

    def selectnamespace(self):  
        ##self.namespaceFld.curNameSpace
        self.namespaceFld.getCurNameSpace()        
        self.accept()

class SelectPathDialog(QtWidgets.QDialog):
    def __init__(self,parent,title,default,*args, **kwargs):
        super(SelectPathDialog,self).__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500,100)
        readStyleSheet(self)
        self.inputPath = default        
        mainLayout = QtWidgets.QVBoxLayout(self)

        self.curExportFld = FilePathField(mode = "directory")

        mainLayout.addWidget(self.curExportFld)

        self.curExportFld.setItem(self.inputPath)

        saveBtnLayout = QtWidgets.QHBoxLayout()
        saveBtn = QtWidgets.QPushButton("save")
        cancelBtn = QtWidgets.QPushButton("cancel")
        saveBtnLayout.addWidget(saveBtn)        
        saveBtnLayout.addWidget(cancelBtn)

        cancelBtn.clicked.connect(self.reject)        
        saveBtn.clicked.connect(self.savePath)

        mainLayout.addLayout(saveBtnLayout)

    def savePath(self):  
        if self.curExportFld.read() == "":
            self.reject()

        self.inputPath = self.curExportFld.read()
        self.accept()




##-----------------------------------------------------------------
##for maya
##-----------------------------------------------------------------        
class ObjectFld(QtWidgets.QWidget):
    def __init__(self,longName = False,*args,**kwargs):
        super(ObjectFld,self).__init__(*args,**kwargs)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.field = QtWidgets.QLineEdit()
        self.setBtn = QtWidgets.QPushButton("set")
        self.clearBtn = QtWidgets.QPushButton("clear")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.longName = longName

        self.layout.addWidget(self.field)
        self.layout.addWidget(self.setBtn)
        self.layout.addWidget(self.clearBtn)

        self.setBtn.clicked.connect(self.selectObject)
        self.clearBtn.clicked.connect(self.clearObject)

        self.setBtn.setMinimumWidth(40)
        self.setBtn.setMaximumWidth(40)

        self.clearBtn.setMinimumWidth(40)
        self.clearBtn.setMaximumWidth(40)

    def selectObject(self):
        sel = cmds.ls(sl =True , l = self.longName) or None

        if sel != None:
            self.field.setText(sel[0])

    def setObject(self,object):
        self.field.setText(object)

    def clearObject(self):
        self.field.setText("")

    def read(self):
        return self.field.text()

class NameSpaceList(ComboBox):
    def __init__(self,data,*args,**kwargs):
        super(NameSpaceList, self).__init__(data,*args,**kwargs)

        self.curNameSpace = ""
        self.reloadBtn = QtWidgets.QPushButton("reload")
        self.reloadBtn.clicked.connect(self.reloadNameSpace)
        self.layout.addWidget(self.reloadBtn)
        self.reloadBtn.setFixedSize(50,20)
                        
        self.pickSBtn = QtWidgets.QPushButton("pick")
        self.pickSBtn.clicked.connect(self.pickNameSpace)
        self.layout.addWidget(self.pickSBtn)
        self.pickSBtn.setFixedSize(50,20)
    
    def setEnabled(self,state):
        self.reloadBtn.setEnabled(state)
        self.pickSBtn.setEnabled(state)
        self.box.setEnabled(state)

    def reloadNameSpace(self):
        self.curNameSpace = self.readText()
        namespaces = editScenes.listNameSpace()        
        namespaces.sort()
        namespaces.insert(0,"None")
        self.setData(namespaces)
        
        if self.curNameSpace != "":
            self.selectText(self.curNameSpace)
            self.box.currentIndexChanged.emit(1)

    def pickNameSpace(self):
        self.reloadNameSpace()

        sel = cmds.ls(sl =True)

        if len(sel) == 0:
            return
        
        target = sel[0]
        target_parts = target.split(":")

        if len(target_parts) < 2:
            return
        
        curNameSpace = target_parts[0]
        if curNameSpace in self.data:
            self.selectText(curNameSpace)
            self.box.currentIndexChanged.emit(1)

    def getCurNameSpace(self):
        self.curNameSpace = self.readText()
        return self.curNameSpace    

class AttrEditWidget(QtWidgets.QWidget):
    finishSetAttrs = QtCore.Signal("bool")

    def __init__(self,attrsDict,width = 150,applyFlag = "editingFinished",*args,**kwargs):
        super(AttrEditWidget,self).__init__(*args,**kwargs)
        
        self.attrsDict = attrsDict
        self.targets = []
        self.fieldWidth = width
        self.attrEditUI = {}
        self.layout = QtWidgets.QFormLayout(self)

        for attrDict in self.attrsDict:
            attrName = attrDict["attrName"]

            if attrDict["type"] == "double":
                field = QtWidgets.QDoubleSpinBox()
                self.attrEditUI[attrName] = field
                field.setMinimumWidth(self.fieldWidth)
                
                if attrDict["min"] != None:
                   field.setMinimum(attrDict["min"]) 
                
                if attrDict["max"] != None:
                   field.setMaximum(attrDict["max"]) 
                                
                field.setValue(attrDict["default"])

                if applyFlag == "editingFinished":
                    field.editingFinished.connect(ApplyFunc(self.setAttrs,attrName))
                elif applyFlag == "valueChanged":
                    field.valueChanged.connect(ApplyFunc(self.setAttrs,attrName))

            elif attrDict["type"] == "bool":
                field = QtWidgets.QCheckBox()
                self.attrEditUI[attrName] = field
                field.setChecked(attrDict["default"])

                if applyFlag != None:
                    field.stateChanged.connect(ApplyFunc(self.setAttrs,attrName))

            elif attrDict["type"] == "long":
                field = QtWidgets.QSpinBox()
                self.attrEditUI[attrName] = field
                field.setMinimumWidth(self.fieldWidth)

                if attrDict["min"] != None:
                   field.setMinimum(attrDict["min"]) 
                
                if attrDict["max"] != None:
                   field.setMaximum(attrDict["max"]) 

                field.setValue(attrDict["default"])

                if applyFlag == "editingFinished":
                    field.editingFinished.connect(ApplyFunc(self.setAttrs,attrName))
                elif applyFlag == "valueChanged":
                    field.valueChanged.connect(ApplyFunc(self.setAttrs,attrName))
                    
            self.layout.addRow(QtWidgets.QLabel(attrName),field)

    def getAttrs(self,target):
        if len(target) == 0:
            return

        if cmds.objExists(target) == False:
            return
            
        for attrDict in self.attrsDict:
            attrName = attrDict["attrName"]
            
            if cmds.objExists(target + "." + attrName):        
                value = cmds.getAttr(target + "." + attrName)
            else:
                value = attrDict["default"]


            self.attrEditUI[attrName].blockSignals(True)

            if attrDict["type"] == "double":
                self.attrEditUI[attrName].setValue(value)

            elif attrDict["type"] == "long":
                self.attrEditUI[attrName].setValue(value)

            elif attrDict["type"] == "bool":
                self.attrEditUI[attrName].setChecked(value)

            self.attrEditUI[attrName].blockSignals(False)

    def setAttrs(self,attrName):        
        if len(self.targets) == 0:
            return
        
        for target in self.targets:
            
            if type(self.attrEditUI[attrName]) == QtWidgets.QDoubleSpinBox:
                value = self.attrEditUI[attrName].value()

            elif type(self.attrEditUI[attrName]) == QtWidgets.QSpinBox:
                value = self.attrEditUI[attrName].value()

            elif type(self.attrEditUI[attrName]) == QtWidgets.QCheckBox:
                value = self.attrEditUI[attrName].isChecked()

            cmds.setAttr(target + "." + attrName,value)

        self.finishSetAttrs.emit(True)
    
    def readValues(self):
        valueDict = {}

        for attrDict in self.attrsDict:
            attrName = attrDict["attrName"]
            
            if attrDict["type"] == "double":
                valueDict[attrName] = self.attrEditUI[attrName].value()

            elif attrDict["type"] == "long":
                valueDict[attrName] = self.attrEditUI[attrName].value()
            
            elif attrDict["type"] == "bool":
                valueDict[attrName] = self.attrEditUI[attrName].isChecked()


        return valueDict

from __future__ import (absolute_import, division,print_function)
import copy
from qtpy import QtWidgets,QtGui,QtCore

SYSTEM_COLOR_DICT = {
                    "activeColor":[0,255,0],
                    "pushColor":[255,0,0] 
}
##------------------------------------------------------------------
def pointToStep(point,minSize):    
    position = point.toTuple()
    
    position=[
                position[0] - (position[0] % minSize),
                position[1] - (position[1] % minSize),
    ]
    
    return QtCore.QPoint(*position)

def divButtonSize(position,size,minSize,num):
    infoList = []

    if size[0] > size[1]:
        #H
        divSizeH = (size[0] - (minSize * (num-1))) / num
        divSizeH = divSizeH - (divSizeH % minSize)
        
        for i in range(0,num):
            divPosition = [position[0] + (divSizeH + minSize)*i, position[1]]

            infoList.append(
                                {
                                    "position":divPosition,
                                    "size":[divSizeH,size[1]]
                                }
            )

    elif size[1] > size[0]:
        #V
        divSizeV = (size[1] - (minSize * (num-1))) / num
        divSizeV = divSizeV - (divSizeV % minSize)

        for i in range(0,num):
            divPosition = [position[0], position[1]+ (divSizeV + minSize)*i]

            infoList.append(
                                {
                                    "position":divPosition,
                                    "size":[size[0],divSizeV],                                    
                                }
            )

    return infoList

def getItemsBounding(items):
    wholeBBox = None

    for item in items:
        rect = item.boundingRect()
        leftTop = item.mapToScene(rect.topLeft()).toTuple()
        rightBottom = item.mapToScene(rect.bottomRight()).toTuple()
        BBox = [
                leftTop[0] +1,
                leftTop[1] +1,
                rightBottom[0]-1,
                rightBottom[1]-1
                ]

        if wholeBBox == None:
            wholeBBox = list(BBox)
            continue
        
        if wholeBBox[0] > BBox[0]:
            wholeBBox[0] = BBox[0]
        
        if wholeBBox[1] > BBox[1]:
            wholeBBox[1] = BBox[1]

        if wholeBBox[2] < BBox[2]:
            wholeBBox[2] = BBox[2]

        if wholeBBox[3] < BBox[3]:
            wholeBBox[3] = BBox[3]

    return   QtCore.QPoint(wholeBBox[0],wholeBBox[1]), QtCore.QPoint(wholeBBox[2],wholeBBox[3])
    

def getSelectAreaRect(startPoint,endpoint):
    startX = startPoint.x()
    startY = startPoint.y()
    endX = endpoint.x()
    endY = endpoint.y()
    rect = None

    ##minx miny maxx maxy
    BBox = [startX,startY,endX,endY]

    if startX > endX:
        BBox[0] = endX
        BBox[2] = startX
    
    if startY > endY:
        BBox[1] = endY
        BBox[3] = startY

    rect = QtCore.QRect(QtCore.QPoint(BBox[0],BBox[1]), QtCore.QPoint(BBox[2],BBox[3]))
    return rect

##------------------------------------------------------------------
class ExecFunc(object):
    def __init__(self, func, *args, **kwargs):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
                        
    def __call__(self, *args, **kwargs):
        error = None        
        try:            
            self.__func(*self.__args, **self.__kwargs)			
                        
        except Exception as e:
            import traceback
            traceback.print_exc()
        

class MenuOrderEditDialog(QtWidgets.QDialog):
    def __init__(self,parent,curCommands):
        super(MenuOrderEditDialog, self).__init__(parent)
        self.curCommands = curCommands
        
        self.setWindowTitle("editMenuOrder")
    
        mainLayout = QtWidgets.QVBoxLayout(self)
        self.menuOrderList = QtWidgets.QListWidget()        
        self.menuOrderList.setMinimumSize(150,100)
        mainLayout.addWidget(self.menuOrderList)

        self.reloadList()

        editOrderLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(editOrderLayout)

        upBtn = QtWidgets.QPushButton("UP")
        editOrderLayout.addWidget(upBtn)
        upBtn.clicked.connect(self.upOrder)

        downBtn =QtWidgets.QPushButton("Down")
        editOrderLayout.addWidget(downBtn)
        downBtn.clicked.connect(self.downOrder)

        removeBtn =QtWidgets.QPushButton("remove")
        editOrderLayout.addWidget(removeBtn)
        removeBtn.clicked.connect(self.removeOrder)

        btnLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(btnLayout)

        acceptBtn = QtWidgets.QPushButton("OK")
        btnLayout.addWidget(acceptBtn)
        acceptBtn.clicked.connect(self.result)

        cancelBtn =QtWidgets.QPushButton("cancel")
        btnLayout.addWidget(cancelBtn)
        cancelBtn.clicked.connect(self.cancel)

    def upOrder(self):        
        curIndex = self.menuOrderList.currentRow()
 
        if curIndex == 0:
            return

        moveItem = self.curCommands[curIndex]

        del self.curCommands[curIndex]

        self.curCommands.insert(curIndex-1, moveItem)
        self.reloadList()

    def downOrder(self):        
        curIndex = self.menuOrderList.currentRow()

        if curIndex == len(self.curCommands)-1:
            return
        
        moveItem = self.curCommands[curIndex]

        del self.curCommands[curIndex]

        self.curCommands.insert(curIndex+1, moveItem)
        self.reloadList()

    def removeOrder(self):
        curIndex = self.menuOrderList.currentRow()
                
        del self.curCommands[curIndex]
        
        self.reloadList()

    def reloadList(self):
        self.menuOrderList.clear()   
        for menu in self.curCommands:
            self.menuOrderList.addItem(menu["menuName"])

    def result(self):
        self.accept()
    
    def cancel(self):
        self.reject()   

class ContextCommandEditDialog(QtWidgets.QDialog):
    def __init__(self,parent,curString,menuName):
        super(ContextCommandEditDialog, self).__init__(parent)
        self.setWindowTitle("editCommands")
    
        mainLayout = QtWidgets.QFormLayout(self)

        self.menuNameFld = QtWidgets.QLineEdit(menuName)
        self.menuNameFld.textChanged.connect(self.checkInputs)
        mainLayout.addRow(QtWidgets.QLabel("menuName:"),self.menuNameFld)

        self.editCommandFld = QtWidgets.QTextEdit()
        self.editCommandFld.setPlainText(curString)
        mainLayout.addRow(QtWidgets.QLabel("command:"),self.editCommandFld)

        mainLayout.addWidget(self.editCommandFld)

        buttonLayout = QtWidgets.QHBoxLayout()
        mainLayout.addRow(QtWidgets.QLabel(""),buttonLayout)
        
        self.applyBtn = QtWidgets.QPushButton("update")
        buttonLayout.addWidget(self.applyBtn)
        self.applyBtn.clicked.connect(self.accept)

        cancelBtn = QtWidgets.QPushButton("cancel")
        buttonLayout.addWidget(cancelBtn)
        cancelBtn.clicked.connect(self.reject)

        self.checkInputs()

    def checkInputs(self):
        if self.menuNameFld.text() == "":
            self.applyBtn.setEnabled(False)
        else:
            self.applyBtn.setEnabled(True)


class CommandEditDialog(QtWidgets.QDialog):
    def __init__(self,parent,curString):
        super(CommandEditDialog, self).__init__(parent)
        self.setWindowTitle("editCommands")
    
        mainLayout = QtWidgets.QVBoxLayout(self)

        self.editCommandFld = QtWidgets.QTextEdit()
        self.editCommandFld.setPlainText(curString)

        mainLayout.addWidget(self.editCommandFld)

        buttonLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        applyBtn = QtWidgets.QPushButton("update")
        buttonLayout.addWidget(applyBtn)
        applyBtn.clicked.connect(self.accept)

        cancelBtn = QtWidgets.QPushButton("cancel")
        buttonLayout.addWidget(cancelBtn)
        cancelBtn.clicked.connect(self.reject)

class ColorSelectButton(QtWidgets.QWidget):
    colorChanged = QtCore.Signal()

    def __init__(self,colors,btnSize = [20,20],*args,**kwargs):
        super(ColorSelectButton,self).__init__(*args,**kwargs)
        self.colors = colors
        self.curColor = colors[0]
        self.buttons = []
        self.btnSize = btnSize

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.radioGP = QtWidgets.QButtonGroup()
        self.setItems()
        self.radioGP.setExclusive(True)
        self.setSelectColor(self.curColor)

        self.radioGP.buttonClicked.connect(self.selectColor)
    
    def selectColor(self):
        self.readSelected()
        self.colorChanged.emit()

    def setEnabled(self,enable):
        for button in self.buttons:
            button.setEnabled(enable)

    def clearItems(self):
        for button in self.buttons:
            self.radioGP.removeButton(button)
            button.hide()
            button.deleteLater()

        self.buttons = []

    def setItems(self):
        self.clearItems()
        
        for i in range(0,len(self.colors)):
            color = self.colors[i]
            button = QtWidgets.QPushButton()
            button.setStyleSheet('QPushButton {\
                                padding: 3px;\
                                border-style:solid;\
                                border-width: 2px;\
                                border-radius:2px;\
                                border-color:rgb(0,0,0);\
                                background-color: rgb(%s, %s, %s);\
                                }\
                                QPushButton:checked{\
                                border-color:rgb(128,200,40);\
                                background-color:rgb(%s, %s, %s);\
                                }' % (str(color[0]),str(color[1]),str(color[2]),str(color[0]),str(color[1]),str(color[2])))

            button.setFixedSize(self.btnSize[0],self.btnSize[1])
            button.setCheckable(True)
            self.layout.addWidget(button)
            self.radioGP.addButton(button,i)
            self.buttons.append(button)

    def readSelected(self):
        if self.radioGP.checkedId() != -1:
            self.curColor = self.colors[self.radioGP.checkedId()]
        
        else:
            self.curColor = [0,0,0]
    
    def setSelectColor(self,value,block=False):
        if block:
            self.radioGP.blockSignals(True)

        for i in range(0,len(self.colors)):
            if value == self.colors[i]:
                button = self.radioGP.button(i)
                button.setChecked(True)

        if block:
            self.radioGP.blockSignals(False)

##------------------------------------------------------------------
class ImageItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, image, parentItem,*args,**kwargs):
        super(ImageItem,self).__init__(parent = parentItem)
        
        self.parentItem = parentItem
        self.normalImg = QtGui.QPixmap(image)                
        self.pushImg = QtGui.QPixmap(image)
        self.overImg = QtGui.QPixmap(image)

        painter = QtGui.QPainter(self.pushImg)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.setBrush(QtGui.QColor(*self.parentItem.pushColor))
        painter.setPen(QtGui.QColor(*self.parentItem.pushColor))
        painter.drawRect(self.pushImg.rect())
        
        painter = QtGui.QPainter(self.overImg)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.setBrush(QtGui.QColor(*self.parentItem.activeColor))
        painter.setPen(QtGui.QColor(*self.parentItem.activeColor))
        painter.drawRect(self.overImg.rect())

        self.setPixmap(self.normalImg)
        
        self.adjustPosition()
        
    def adjustPosition(self):        
        parentRect = self.parentItem.boundingRect()
        localRect = self.boundingRect()
        border = self.parentItem.border

        scaleRatio = 1.0
        if localRect.width() != 0:
            scaleRatio = parentRect.width() / localRect.width()
        
        pos_x = -1 * border
        pos_y = -1 * border

        self.setTransform(QtGui.QTransform().translate(pos_x,pos_y).scale(scaleRatio,scaleRatio))

    def setColor(self):        
        if self.parentItem.pushState:            
            self.setPixmap(self.pushImg)

        elif self.parentItem.state:            
            self.setPixmap(self.overImg)

        else:
            self.setPixmap(self.normalImg)       

        self.adjustPosition()

        
class TextItem(QtWidgets.QGraphicsTextItem):
    def __init__(self, text, color, parentItem,*args,**kwargs):
        super(TextItem,self).__init__(text,parentItem)
        
        self.parentItem = parentItem
        self.setDefaultTextColor(QtGui.QColor(*color))
        # self.setPlainText(text)
        self.adjustPosition()
        
    def adjustPosition(self):        
        parentRect = self.parentItem.boundingRect()
        localRect = self.boundingRect()
        
        pos_x = ((parentRect.width() - localRect.width()) / 2.0 + parentRect.x())
        pos_y = ((parentRect.height() - localRect.height()) / 2.0 + parentRect.y())

        self.setTransform(QtGui.QTransform().translate(pos_x,pos_y))

class ButtonItem(QtWidgets.QGraphicsRectItem):
    def __init__(self,info):
        super(ButtonItem,self).__init__()
        self.border = 1
        self.editEnable = True
        
        self.state = False
        self.pushState = False

        self.size = info["size"]
        self.tmpSize = None
        self.position = info["position"]
        self.tmpPosition = None
        self.label = info["label"]
        self.bgColor = info["bgColor"]
        self.pushColor = SYSTEM_COLOR_DICT["pushColor"]
        self.activeColor = SYSTEM_COLOR_DICT["activeColor"]
        self.labelColor = info["labelColor"]

        self.contextCommands = []

        if "contextCommands" in list(info.keys()):
            self.contextCommands = info["contextCommands"]
            
        self.__rect = QtCore.QRect(0, 0, self.size[0], self.size[1])
        self.setRect(self.__rect)
        self.setPos(*self.position)
        self.imageItem = None

        if "image" in list(info.keys()):
            self.imageItem = ImageItem(info["image"],self)

        self.labelItem = TextItem(self.label,self.labelColor,self)
        self.setZValue(1)
        self.setColor()

    def applyContextCommand(self,index):
        commandString = str(self.contextCommands[index]["command"])
        exec(commandString)

    def editColor(self,mode,color):
        if mode == "active":
            self.activeColor = color
        
        elif mode == "bgColor":
            self.bgColor = color

        elif mode == "push":
            self.pushColor = color

    def setColor(self):
        
        if self.pushState:
            if self.bgColor != None:
                self.setBrush(QtGui.QColor(*self.bgColor))

            pen = QtGui.QPen( QtGui.QColor(*self.pushColor))

        elif self.state:
            if self.bgColor != None:
                self.setBrush(QtGui.QColor(*self.bgColor))

            pen = QtGui.QPen( QtGui.QColor(*self.activeColor))

        else:
            if self.bgColor != None:
                self.setBrush(QtGui.QColor(*self.bgColor))
            
            if len(self.contextCommands) == 0:
                pen = QtGui.QPen( QtGui.QColor(30,30,30))
            else:
                pen = QtGui.QPen( QtGui.QColor(255,30,255))

        pen.setWidth(self.border*2)
        self.setPen(pen)

        if self.imageItem != None:
            self.imageItem.setColor()

    def setLabel(self,text):
        self.label = text
        self.labelItem.setPlainText(self.label)
        self.adjustChItems()

    def setPushState(self,state):
        if state == self.pushState:
            return

        self.pushState = state
        self.setColor()

    def setState(self,state):
        if state == self.state:
            return
        self.state = state
        self.setColor()

    def setSize(self,size):
        self.tmpSize = [size[0],size[1]]
        self.__rect = QtCore.QRectF(0, 0, self.tmpSize[0], self.tmpSize[1])
        self.setRect(self.__rect)
        self.adjustChItems()

    def scaleSize(self,scale):
        self.tmpSize = [self.size[0]* scale[0],self.size[1]* scale[1]]

        if self.tmpSize[0] < 10:
            self.tmpSize[0] = 10
        if self.tmpSize[1] < 10:
            self.tmpSize[1] = 10

        self.__rect = QtCore.QRectF(0, 0, self.tmpSize[0], self.tmpSize[1])
        self.setRect(self.__rect)
        self.adjustChItems()

    def editPosition(self,position):
        self.tmpPosition = position
        self.setPos(*self.tmpPosition)

    def buttonInfo(self):
        info = {
                "size":self.size,
                "position":self.position,
                "label":self.label,
                "bgColor":self.bgColor,                
                "labelColor":self.labelColor,
                "contextCommands":self.contextCommands
        }
        return info

    def adjustChItems(self):
        self.imageItem.adjustPosition()
        self.labelItem.adjustPosition()

    def fixTransform(self):
        if self.tmpSize != None:
            self.size = list(self.tmpSize)
            self.tmpSize = None
            
        if self.tmpPosition != None:
            self.position = list(self.tmpPosition)
            self.tmpPosition = None

class ButtonGroupItem(ButtonItem):
    def __init__(self,buttons,buttonsSource):
        super(ButtonItem,self).__init__()
        self.state = False
        self.pushState = False
        self.editEnable = True
        self.pushColor = [255,0,0]
        self.activeColor = [0,255,0]
        self.buttons = buttons
        self.buttonsSource = buttonsSource
        
        groupRect = getItemsBounding(buttons)
        self.size = [groupRect.width(), groupRect.height()]
        self.defautSize = [groupRect.width(), groupRect.height()]
        self.tmpSize = None
        self.position = [groupRect.topLeft().x(),groupRect.topLeft().y()]
        self.tmpPosition = None
        self.border = 0
        self.__rect = QtCore.QRect(0, 0, groupRect.width(), groupRect.height())
        self.setRect(self.__rect)
        self.setPos(groupRect.topLeft())
        self.setZValue(1)
        
        for chitem in buttons:            
            localPoint = self.mapFromScene(QtCore.QPoint(*chitem.position))
            chitem.setParentItem(self)
            chitem.editPosition([localPoint.x(), localPoint.y()])
            chitem.position = [localPoint.x(), localPoint.y()]            
            chitem.setSize(chitem.size)            
            chitem.editEnable = False
            chitem.adjustChItems()

        self.setColor()

    def setColor(self):
        # self.state = mode

        if self.pushState:
            self.setBrush(QtGui.QColor(*self.pushColor))

        elif self.state:
            self.setBrush(QtGui.QColor(*self.activeColor))
            self.setOpacity(0.5)

        else:
            self.setBrush(QtGui.Qt.NoBrush)
            self.setOpacity(1.0)
        
        self.setPen(QtGui.Qt.NoPen)

    def adjustChItems(self):
        self.update()
        rect = self.rect()
        for chitem in self.childItems():
            scale = [rect.width()/self.defautSize[0],rect.height()/self.defautSize[1]]            
            chitem.editPosition([chitem.position[0] * scale[0],chitem.position[1] * scale[1]])            
            chitem.setSize([(chitem.size[0]+chitem.border) * scale[0],(chitem.size[1]+chitem.border) * scale[1]])
    
    def buttonInfo(self):
        info = {
                "size":self.size,
                "position":self.position    
        }
        return info

class PickerScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args , **kwargs):
        super(PickerScene,self).__init__()
##--------------------------------------------------------------------------------------------------------
class AreaView(QtWidgets.QGraphicsView):
    selectionChange = QtCore.Signal()

    def __init__(self,areaWidth = 480, areaHeight = 640,buttonType = ButtonItem, *args , **kwargs):
        super(AreaView,self).__init__()
        
        self.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff )
        self.setTransformationAnchor( QtWidgets.QGraphicsView.NoAnchor) 
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.undoChunk = []
        self.minSize = 10
        self.bgItem = None
        self.bgImage = None
        self.areaWidth = areaWidth
        self.areaHeight = areaHeight
        
        self.buttonType = buttonType
        self.editMode = False
        self.editTool = None
        self.groupItems = {}
        self.curScale = 1.0

        self.curActiveitems = []
        self.selectItems = []
        self.mouseMode = "select_replace"

        self.setScene(QtWidgets.QGraphicsScene(QtCore.QRectF(self.rect())))
        self.scene().setBackgroundBrush(QtGui.QColor(80,80,80))

        self.clickPoint = None
        self.selectAreaRect = None

        self.setBGImage(None)
    ##Event--------------------------------------------------------------------------------------------------------    
    ##keyPressEvent--------------------------------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_A:
            self.fitView()
    
        if self.editMode:
            if event.key() == QtCore.Qt.Key_Q:
                self.editTool = "select"
            
            elif event.key() == QtCore.Qt.Key_W:
                self.editTool = "translate"
            
            elif event.key() == QtCore.Qt.Key_R:
                self.editTool = "scale"

            elif event.key() == QtCore.Qt.Key_Delete:
                self.deleteButtonItem()

            elif event.key() == QtCore.Qt.Key_C:
                self.editTool = "create"

            elif event.key() == QtCore.Qt.Key_M:
                self.editTool = "createMulti"

            elif event.key() == QtCore.Qt.Key_Z:
                self.undo()

        else:
            self.editTool = None
    ##wheelEvent--------------------------------------------------------------------------------------------------------
    def wheelEvent(self, event):
        wheelAngle = event.angleDelta().y()
        self.zoomView(event,wheelAngle,1.2)

    ##mousePressEvent------------------------------------------------------------------
    def mousePressSelect(self,event):
        
        self.mouseMode = "select_replace"
        
        if event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            self.mouseMode = "select_add"
        
        elif event.modifiers() == QtCore.Qt.ShiftModifier:
            self.mouseMode = "select_inverse"

        elif event.modifiers() == QtCore.Qt.ControlModifier:
            self.mouseMode = "select_remove"

        if self.mouseMode == "select_replace":
            self.selectItems = []

        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.selectAreaRect = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle,self)
        self.selectAreaRect.setGeometry(QtCore.QRect(self.clickPoint, QtCore.QSize(1,1)))
        self.selectAreaRect.show()

        localArea = getSelectAreaRect(self.mapToScene(self.clickPoint).toPoint(),self.mapToScene(self.clickPoint).toPoint())
        areaItems = self.scene().items(localArea)
        self.setButtonPushed(areaItems)

        return areaItems

    def hasSelections(self):
        self.getCurActiveButton()
        areaItems = []

        for item in self.scene().items(QtCore.QRect(self.mapToScene(self.clickPoint).toPoint() , QtCore.QSize(1,1))):
            if self.editMode:
                if type(item) != ButtonGroupItem and type(item) != self.buttonType:
                    continue

                if item.editEnable ==False:
                    continue
            
            else:
                if type(item) != self.buttonType:
                    continue

            areaItems.append(item)

        deltaItems = set(areaItems) - set(self.curActiveitems)

        if len(self.curActiveitems) == 0 or len(areaItems) == 0 or len(deltaItems) != 0:
            return False
        
        else:
            True

    def mousePressEvent(self, event):
        self.pastPoint = None
        self.clickPoint = event.pos()        
        self.mouseMode = "select_replace"

        if event.button() == QtCore.Qt.LeftButton:            
            if self.selectAreaRect != None:
                self.selectAreaRect.hide()
                self.selectAreaRect.deleteLater()
                self.selectAreaRect = None

            ##LMB + ALT
            if event.modifiers() == QtCore.Qt.AltModifier:
                self.mouseMode = "pan"
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                self.pastPoint = event.pos()
            
            ##LMB
            # elif event.modifiers() == QtCore.Qt.NoModifier:
            else:
                hasSelection = self.hasSelections()

                if self.editMode == False:
                    self.mousePressSelect(event)
                     
                else:
                    if self.editTool == "select":
                        self.mousePressSelect(event)
                    
                    elif self.editTool == "create" or self.editTool == "createMulti":
                        self.clickPoint = pointToStep(self.mapToScene(event.pos()),self.minSize)

                        self.mouseMode = "create"
                        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
                        self.selectAreaRect = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle,self)
                        self.selectAreaRect.setGeometry(QtCore.QRect(self.mapFromScene(self.clickPoint), QtCore.QSize(1,1)))
                        self.selectAreaRect.show()

                    elif hasSelection == False:
                        self.mousePressSelect(event)
                        
                    elif self.editTool == "translate":
                        self.mouseMode = "move"
                        self.clickPoint = event.pos()
                        self.pastPoint = event.pos()
                        self.scaleBasePoints = {}

                        for item in self.curActiveitems:                            
                            self.scaleBasePoints[item] = item.scenePos()

                    elif self.editTool == "scale":
                        self.mouseMode = "scale"
                        self.pastPoint = event.pos()

                        BBox = getItemsBounding(self.curActiveitems)
                        self.scaleBaseRect = QtCore.QRect(BBox[0],BBox[1])
                        self.scaleBasePoints = {}

                        for item in self.curActiveitems:
                            self.scaleBasePoints[item] = item.scenePos()

                        self.selectAreaRect = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle,self)                        
                        self.selectAreaRect.setGeometry(QtCore.QRect(self.mapFromScene(BBox[0]),self.mapFromScene(BBox[1])))
                        self.selectAreaRect.show()
        
        elif event.button() == QtCore.Qt.RightButton:            
            #RMB + ALT
            if event.modifiers() == QtCore.Qt.LeftButton:
                if self.selectAreaRect != None:
                    self.selectAreaRect.hide()
                    self.selectAreaRect.deleteLater()
                    self.selectAreaRect = None
                    self.setButtonUnPush()    
                    return 

            elif event.modifiers() == QtCore.Qt.AltModifier:
                self.mouseMode = "zoom"
                self.pastPoint = event.pos()

            else:
                self.clickPoint = event.pos()
                self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
                self.selectAreaRect = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle,self)
                self.selectAreaRect.setGeometry(QtCore.QRect(self.clickPoint, QtCore.QSize(1,1)))
                self.selectAreaRect.show()
                localArea = getSelectAreaRect(self.mapToScene(self.clickPoint).toPoint(),self.mapToScene(self.clickPoint).toPoint())
                areaItems = self.scene().items(localArea)
                self.selectAreaRect.hide()
                self.selectAreaRect.deleteLater()
                self.selectAreaRect = None

                targetItem = None

                for item in areaItems:
                    if type(item) == self.buttonType:
                        targetItem = item

                self.callContextMenu(targetItem,event)
                return

    ##mouseMoveEvent------------------------------------------------------------------
    def mouseMoveEvent(self, event):

        if self.clickPoint == None:
            return
                
        if self.mouseMode.startswith("select_"):
            if self.selectAreaRect == None:
                return

            curPoint = event.pos()
            self.selectAreaRect.setGeometry(getSelectAreaRect(self.clickPoint,curPoint))

            localArea = getSelectAreaRect(self.mapToScene(self.clickPoint).toPoint(),self.mapToScene(curPoint).toPoint())
            areaItems = self.scene().items(localArea)
            self.setButtonUnPush()
            self.setButtonPushed(areaItems)

        elif self.mouseMode == "create":
            if self.selectAreaRect == None:
                return

            curPoint = pointToStep(self.mapToScene(event.pos()),self.minSize)
            self.selectAreaRect.setGeometry(getSelectAreaRect(self.mapFromScene(self.clickPoint),self.mapFromScene(curPoint)))

        elif self.mouseMode == "move":
            curPoint = event.pos()
            delta = self.mapToScene(curPoint) - self.mapToScene(self.clickPoint)
            self.moveActiveItems(delta)
            
        elif self.mouseMode == "scale":
            curPoint = event.pos()         
            delta = self.mapToScene(curPoint) - self.mapToScene(self.clickPoint)
            self.scaleActiveItems(delta)

            BBox = getItemsBounding(self.curActiveitems)            
            self.selectAreaRect.setGeometry(QtCore.QRect(self.mapFromScene(BBox[0]),self.mapFromScene(BBox[1])))

        elif self.mouseMode == "pan":
            curPoint = event.pos()
            delta = curPoint - self.pastPoint
            self.setTransform(self.transform() * QtGui.QTransform().translate(delta.x(), delta.y()))
            self.pastPoint = event.pos()  

        elif self.mouseMode == "zoom":
            curPoint = event.pos()
            delta = curPoint - self.pastPoint
            self.zoomView(event,delta.x(),1.02)
            self.pastPoint = event.pos() 

    ##mouseReleaseEvent-------------------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        releasePoint = event.pos()

        if self.mouseMode.startswith("select_"):
            self.setButtonUnPush()
            if self.selectAreaRect == None:
                return

            localArea = getSelectAreaRect(self.mapToScene(self.clickPoint).toPoint(),self.mapToScene(releasePoint).toPoint())
            areaItems = self.scene().items(localArea)
            self.setButtonState(areaItems)
            # self.selectItems.extend(areaItems)
            self.selectAreaRect.hide()
            self.selectAreaRect.deleteLater()
            self.selectAreaRect = None
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        
        elif self.mouseMode == "create":
            releasePoint = pointToStep(self.mapToScene(event.pos()),self.minSize)  
            localArea = getSelectAreaRect(self.clickPoint,releasePoint)
            
            position = localArea.topLeft().toTuple()
            size = [localArea.width(),localArea.height()]

            self.selectAreaRect.hide()
            self.selectAreaRect.deleteLater()
            self.selectAreaRect = None
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

            if self.editTool == "create":
                buttons = self.createButtonItem(position,size)
                
            elif self.editTool == "createMulti":
                buttons = self.createButtonItemMulti(position,size)

            self.setButtonState(buttons)

        elif self.mouseMode == "move":
            self.fixTransformActiveItems()

        elif self.mouseMode == "scale":
            if self.selectAreaRect == None:
                return
            self.fixTransformActiveItems()
            self.selectAreaRect.hide()
            self.selectAreaRect.deleteLater()
            self.selectAreaRect = None
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        elif self.mouseMode == "pan":
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        elif self.mouseMode == "zoom":
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        self.clickPoint = None
        self.viewport().update()
        
        if self.editMode:
            self.selectionChange.emit()

        # print(len(self.selectItems))

    def callContextMenu(self,item,event):
        if item == None:
            return
        
        self.context = []
        if self.editMode:
            if item.editEnable == False:
                return

            menu = QtWidgets.QMenu("menu")
            action = menu.addAction("addMenu")
            action.triggered.connect(lambda: self.addContextCommand(item))
                        
            order = menu.addAction("changeOrder")            
            order.triggered.connect(lambda: self.reorderContextCommand(item))

            menu.addSeparator()
            
            for i in range(0, len(item.contextCommands)):
                action = QtWidgets.QAction(item.contextCommands[i]["menuName"], menu)
                menu.addAction(action)
                action.triggered.connect(ExecFunc(self.editContextCommand,item,i))
                self.context.append(action)            

            menu.exec_(self.mapToGlobal(event.pos()))

        else:
            item.setPushState(True)
            menu = QtWidgets.QMenu(title="menu")
            
            for i in range(0, len(item.contextCommands)):
                action = QtWidgets.QAction(item.contextCommands[i]["menuName"], menu)
                menu.addAction(action)
                action.triggered.connect(ExecFunc(self.excuteCommand,item.contextCommands[i]["command"]))
                self.context.append(action)
                            
            menu.exec_(self.mapToGlobal(event.pos()))
            item.setPushState(False)

    def excuteCommand(self,commandString):
        ldict = {}   
        
        try:
            exec(commandString, globals(), ldict)

        except Exception as e:
            import traceback
            traceback.print_exc()

    def addContextCommand(self,item):
        dialog = ContextCommandEditDialog(self,"","")
        
        if dialog.exec_():
            updateString = dialog.editCommandFld.toPlainText()
            updateName = dialog.menuNameFld.text()
        
            updateCommands = copy.deepcopy(item.contextCommands)
            updateCommands.append({"menuName":updateName,"command":updateString})            
            self.changeContextCommand([item],[updateCommands])


    def reorderContextCommand(self,item):
        
        dialog = MenuOrderEditDialog(self,item.contextCommands)
        
        if dialog.exec_():
            self.changeContextCommand([item],[dialog.curCommands])

    def editContextCommand(self,item,index):   
        dialog = ContextCommandEditDialog(self,item.contextCommands[index]["command"],item.contextCommands[index]["menuName"])
        
        if dialog.exec_():
            updateString = dialog.editCommandFld.toPlainText()
            updateName = dialog.menuNameFld.text()
        
            updateCommands = copy.deepcopy(item.contextCommands)
            updateCommands[index]["menuName"] = updateName
            updateCommands[index]["command"] = updateString
            
            self.changeContextCommand([item],[updateCommands])

    ##viewScale--------------------------------------------------------------------------------------------------
    def zoomView(self,event,moveDist,scaleRatio):
        start_pos = self.mapToScene(event.pos())
        self.curScale = self.transform().m11()
                
        if moveDist > 0:            
            scaleRatio = scaleRatio
            if self.curScale > 5.0:
                scaleRatio = 1.0

        else:
            scaleRatio = 1.0 / scaleRatio
            if self.curScale < 0.2:
                scaleRatio = 1.0
  
        self.scale(scaleRatio,scaleRatio)
        self.curScale = self.transform().m11()
        end_pos = self.mapToScene(event.pos())

        self.translate((end_pos - start_pos).x(),(end_pos - start_pos).y())
        self.resizeScene()

    def resetView(self):
        curScale = self.transform().m11()
        scaleRatio = 1.0 / curScale

        self.scale(scaleRatio,scaleRatio)
        self.resizeScene()

        curPointH = self.transform().m31()
        curPointV = self.transform().m32()

        self.translate(curPointH * -1.0 ,curPointV * -1.0)
        self.resizeScene()

    def scaleView(self):
        # curPointH = self.transform().m31()
        # curPointV = self.transform().m32()
        
        self.fitInView(self.scene().itemsBoundingRect(), QtCore.Qt.IgnoreAspectRatio)
                
        # self.scale(self.curScale,self.curScale)
        # self.resizeScene()
        

    def fitView(self):
        self.fitInView(self.scene().itemsBoundingRect(), QtCore.Qt.IgnoreAspectRatio)
                
    def resizeScene(self):
        scaleFactor = 2
        scaleRatio = self.transform().m11()
        itemRect = self.scene().itemsBoundingRect()
        
        itemRect.adjust(
            -itemRect.width()  / scaleRatio * scaleFactor,
            -itemRect.height() / scaleRatio * scaleFactor,
            itemRect.width()   / scaleRatio * scaleFactor,
            itemRect.height()  / scaleRatio * scaleFactor
        )

        self.setSceneRect(itemRect)

    ##--------------------------------------------------------------------------------------------------------
    #undo
    ## {"ccommand":"" ,"options":{}}

    def undo(self):
        if len(self.undoChunk) == 0:
            return
        
        self.undoChunk[-1]["command"](**self.undoChunk[-1]["options"])

        self.update()
        self.undoChunk.pop(-1)

    def addUndo(self,command):
        self.undoChunk.append(command)

    def clearUndo(self):
        self.undoChunk = []

    ##button commands--------------------------------------------------------------------------------------
    def addButtonItem(self,infoList,editEnable =True):
        buttons = []
        for info in infoList:
            if info["size"][0] < self.minSize or info["size"][1] < self.minSize:
                continue

            btn = self.buttonType(info)
            btn.editEnable = editEnable
            self.scene().addItem(btn)
            buttons.append(btn)

        return buttons

    def removeButtonItem(self,items):
        for item in items:
            if type(item) != self.buttonType:
                continue
            
            self.scene().removeItem(item)

    def groupButton(self,buttons,groupSize,groupName,buttonsSource):
        groupItem = ButtonGroupItem(buttons,buttonsSource)
        self.scene().addItem(groupItem)
        
        if len(groupSize) != 0:
            self.transformItems([groupItem],[groupSize["size"]],[groupSize["position"]])

        self.groupItems[groupName] = groupItem

    def transformItems(self,items,scales,positions):
        for item,scale,position in zip(items,scales,positions):
            item.setSize(scale)
            item.editPosition(position)
            item.fixTransform()

    def setItemLabels(self,items,labels):
        for item,label in zip(items,labels):
            item.setLabel(label)

    def setItemColors(self,items,colors,mode):
        for item,color in zip(items,colors):
            item.editColor(mode,color)
            item.setColor()

    def clearButtonItem(self):
        items = self.scene().items()

        for item in items:
            if type(item) != self.buttonType:
                continue

            self.scene().removeItem(item)

    def setBGImage(self,file):
        if self.bgItem != None:
            self.scene().removeItem(self.bgItem)

        if file != None:
            self.bgItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(file))
            self.areaWidth = self.bgItem.pixmap().width()
            self.areaHeight = self.bgItem.pixmap().height()      

        else:
            self.areaWidth = 480
            self.areaHeight = 640
            self.bgItem = QtWidgets.QGraphicsRectItem(QtCore.QRect(0,0,self.areaWidth,self.areaHeight))

        self.bgImage = file
        self.scene().addItem(self.bgItem)
        
        self.resize(self.areaWidth, self.areaHeight)
        self.resizeScene()

    def setItemContextCommand(self,items,commands):
        for item,command in zip(items,commands):
            item.contextCommands = copy.deepcopy(command)

    def loadInfoDict(self,itemDict):
        self.setBGImage(itemDict["BGImage"])
        self.addButtonItem(itemDict["buttons"])
        
    ##-----------------------------------------------------------------------------------------------------
    def exportInfoDict(self):
        itemDict = {}

        items = self.scene().items()
        buttons = []
        
        for item in items:
            if type(item) == self.buttonType and item.editEnable:
                buttons.append(item.buttonInfo())
                continue            
                    
        itemDict["buttons"] = buttons
        itemDict["BGImage"] = self.bgImage
        
        return itemDict

    ##buttunState-----------------------------------------------------------------------------------------------------
    def getAllButtons(self):
        buttons = []
        items = self.scene().items()

        for item in items:
            if self.editMode:
                if type(item) != ButtonGroupItem and type(item) != self.buttonType:
                    continue

                if item.editEnable ==False:
                    continue
            
            else:
                if type(item) != self.buttonType:
                    continue
        
            buttons.append(item)
        
        return buttons

    def getCurActiveButton(self):
        self.curActiveitems = []
        items = self.scene().items()

        for item in items:
            if self.editMode:
                if type(item) != ButtonGroupItem and type(item) != self.buttonType:
                    continue

                if item.editEnable ==False:
                    continue
            
            else:
                if type(item) != self.buttonType:
                    continue

            if item.state:
                self.curActiveitems.append(item)

    def clearButtonState(self):
        items = self.scene().items()

        for item in items:
            if type(item) != ButtonGroupItem and  type(item) != self.buttonType:
                continue

            item.setState(False)
            
    def setButtonUnPush(self):
        for item in self.scene().items():
            if self.editMode:
                if type(item) != ButtonGroupItem and type(item) != self.buttonType:
                    continue

                if item.editEnable ==False:
                    continue
            
            else:
                if type(item) != self.buttonType:
                    continue

            item.setPushState(False)

    def setButtonPushed(self,items):

        for item in self.scene().items():
            if self.editMode:
                if type(item) != ButtonGroupItem and type(item) != self.buttonType:
                    continue

                if item.editEnable ==False:
                    continue
            
            else:
                if type(item) != self.buttonType:
                    continue
                        
            if item in items:
                if self.mouseMode == "select_replace":
                    item.setPushState(True)

                elif self.mouseMode == "select_inverse":
                    item.setPushState(True)

                elif self.mouseMode == "select_remove":
                    item.setPushState(False)

                elif self.mouseMode == "select_add":
                    item.setPushState(True)
            
    def setButtonState(self,items):
        if len(items) == 0 or self.mouseMode == "select_replace":
            self.clearButtonState()

        for item in items:
            if self.editMode:
                if type(item) != ButtonGroupItem and type(item) != self.buttonType:
                    continue

                if item.editEnable ==False:
                    continue
            
            else:
                if type(item) != self.buttonType:
                    continue

            if self.mouseMode == "select_replace":
                item.setState(True)
                if item not in self.selectItems:
                    self.selectItems.append(item)
            
            elif self.mouseMode == "select_inverse":
                if item.state:
                    if item in self.selectItems:
                        self.selectItems.remove(item)
                    item.setState(False)
                else:
                    item.setState(True)
                    if item not in self.selectItems:
                        self.selectItems.append(item)

            elif self.mouseMode == "select_remove":
                item.setState(False)
                
                if item in self.selectItems:
                    self.selectItems.remove(item)

            elif self.mouseMode == "select_add":
                item.setState(True)
                
                if item not in self.selectItems:
                    self.selectItems.append(item)
    ##edit buttun-----------------------------------------------------------------------------------------------------    
    def moveActiveItems(self,delta):        
        for item in self.curActiveitems:
            basePoint = self.scaleBasePoints[item]
            targetPos = basePoint + delta            
            targetPos = pointToStep(targetPos,self.minSize)
            item.editPosition(targetPos.toTuple())

    def scaleActiveItems(self,delta):
        wholeTopLeft = self.scaleBaseRect.topLeft().toTuple()
        
        deltaV = delta.y() + self.scaleBaseRect.height()
        deltaH = delta.x() + self.scaleBaseRect.width()

        deltaV = deltaV - (deltaV % self.minSize)
        deltaH = deltaH - (deltaH % self.minSize)

        scaleV = deltaV / self.scaleBaseRect.height()
        scaleH = deltaH / self.scaleBaseRect.width()


        for item in self.curActiveitems:
            topleft = self.scaleBasePoints[item].toTuple()
            
            deltaTopleft = [
                                topleft[0] - wholeTopLeft[0],
                                topleft[1] - wholeTopLeft[1]
                            ]
            
            targetPos = [
                            (deltaTopleft[0] * scaleH) + wholeTopLeft[0],
                            (deltaTopleft[1] * scaleV) + wholeTopLeft[1]
            ]
            targetPos = pointToStep(QtCore.QPoint(*targetPos),self.minSize)
            item.editPosition(targetPos.toTuple())

            item.scaleSize([scaleH,scaleV])
            item.update()

    def fixTransformActiveItems(self):
        self.fixTransformItems(self.curActiveitems)
        
    def fixTransformItems(self,items):        
        scales = []
        positions = []

        for item in items:            
            scales.append(list(item.size))
            positions.append(list(item.position))
            item.fixTransform()
            
        undoInfo = {
                    "command":self.transformItems,
                    "options":{
                                "items":items,
                                "scales":scales,
                                "positions":positions,
                    }
        }

        self.undoChunk.append(undoInfo)

    def changeItemLabels(self,items,label):    
        labels = []
        targets = []
        for item in items:
            if type(item) == ButtonGroupItem:
                continue
            
            targets.append(item)
            labels.append(str(item.label))

            self.setItemLabels([item],[label])

        undoInfo = {
                    "command":self.setItemLabels,
                    "options":{
                                "items":targets,
                                "labels":labels
                    }
        }

        self.undoChunk.append(undoInfo)

    def changeItemColors(self,items,color,mode):
        colors = []
        targets = []
        for item in items:
            if type(item) == ButtonGroupItem:
                continue
            
            targets.append(item)

            if mode == "active":
                colors.append(item.activeColor)
            
            elif mode == "bgColor":                
                colors.append(item.bgColor)

            elif mode == "push":                
                colors.append(item.pushColor)

            self.setItemColors([item],[color],mode)

        undoInfo = {
                    "command":self.setItemColors,
                    "options":{
                                "items":targets,
                                "colors":colors,
                                "mode":mode
                    }
        }

        self.undoChunk.append(undoInfo)

    def changeContextCommand(self,items,commands):

        pastCommands = []

        for item,command in zip(items,commands):
            pastCommands.append(copy.deepcopy(item.contextCommands))
            print(command)
            self.setItemContextCommand([item],[command])

        undoInfo = {
                    "command":self.setItemContextCommand,
                    "options":{
                                "items":items,
                                "commands":pastCommands,                                
                    }
        }

        self.undoChunk.append(undoInfo)


    ##create buttun-----------------------------------------------------------------------------------------------------    
    def createButtonItem(self,position,size):
        infoList = [
                        {
                            "position":position,
                            "size":size,
                            "label":"A",
                            "bgColor":[30,200,200],
                            "labelColor":[0,0,0],
                            "targets":[]
                        }
                    ]

        buttons = self.addButtonItem(infoList)
        
        undoInfo = {
                    "command":self.removeButtonItem,
                    "options":{
                                "items":buttons,
                    }
        }

        self.undoChunk.append(undoInfo)
        return buttons

    def createButtonItemMulti(self,position,size):
        ##need filter
        num = 0
        infoList = divButtonSize(position,size,self.minSize)
        
        for i in range(0, num):
            updateDict = {
                            "label":"A",
                            "bgColor":[30,200,200],
                            "labelColor":[0,0,0],
                            "targets":[]

            }
            infoList[i].update(**updateDict)

        buttons = self.addButtonItem(infoList)
        undoInfo = {
                    "command":self.removeButtonItem,
                    "options":{
                                "items":buttons,
                    }
        }

        self.undoChunk.append(undoInfo)
        return buttons

        

    def deleteButtonItem(self):
        itemInfo = []
        self.getCurActiveButton()
        items = self.curActiveitems

        if len(items) == 0:
            return

        for item in items:
            if type(item) != self.buttonType:
                continue

            itemInfo.append(item.buttonInfo())
                
        self.removeButtonItem(items)

        undoInfo = {
                    "command":self.addButtonItem,
                    "options":{
                                "infoList":itemInfo,
                    }
        }

        self.undoChunk.append(undoInfo)



##-----------------------------------------------------------------------------

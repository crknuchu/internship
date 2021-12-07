from PyQt6 import QtWidgets
from PyQt6.QtGui import QCursor
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from numpy import e
import demoapp
import sys
import pandas
from matplotlib.backends.backend_qtagg import FigureCanvas,NavigationToolbar2QT
import os
import argparse
import numpy as np
from matplotlib.backend_bases import PickEvent
import math

class MainLine():
    #has line object and list of markers on the line
    def __init__(self,lineObj):
        self.lineObj = lineObj
        self.markerList = [] #list of dotMarkers on the mainLine
        self.name = self.lineObj.get_label()
    
    def set_visible(self,bool):
        self.lineObj.set_visible(bool)
        for marker in self.markerList:
            marker.set_visible(bool)

    def get_visible(self):
        return self.lineObj.get_visible()
    
    def contains(self,event):
        return self.lineObj.contains(event)


class Marker():
    #marker contains marker object and annotation
    def __init__(self,ax,style,color):
        self.ax = ax
        self.style = style
        self.color = color
        self.xdata = None
        self.ydata = None
        self.markerObj = None
        self.annotation = None
        self.type = None
    
    def set_visible(self,bool):
        if self.markerObj is not None:
            self.markerObj.set_visible(bool)
        if self.annotation is not None:
            self.annotation.set_visible(bool)
    
    def contains(self,event):
        if self.markerObj is not None:
            return self.markerObj.contains(event)
    
    def remove(self):
        if self.annotation is not None:
            self.annotation.remove()
        if self.markerObj is not None:    
            self.markerObj.remove()

class DotMarker(Marker):
    #dot marker that is put on lines
    def __init__(self, ax, xdata, ydata, style, color,line):
        super().__init__(ax, style, color)
        self.type = "dot"
        self.xdata = xdata
        self.ydata = ydata
        self.xpixel,self.ypixel = ax.transData.transform((xdata,ydata))
        self.parentLine = line
    
        listoflines = self.ax.plot(self.xdata,self.ydata,style,picker=6)
        self.markerObj = listoflines[0]
        if self.color is not None:
            self.markerObj.set_color(self.color)
        self.annotation = self.ax.annotate(f"({self.xdata:.2f},{self.ydata:.2f})",(self.xdata,self.ydata))
        self.name = self.markerObj.get_label()
    
    def move(self,xdata):
        self.markerObj.set_xdata(xdata)
        estimated_ydata = np.interp(xdata,self.parentLine.lineObj.get_xdata(),self.parentLine.lineObj.get_ydata())
        self.markerObj.set_ydata(estimated_ydata) 
        self.annotation.set_x(xdata)
        self.annotation.set_y(estimated_ydata)
        self.annotation.set_text(f"({xdata:.2f},{estimated_ydata:.2f})")
        self.xpixel,self.ypixel = self.ax.transData.transform((xdata,estimated_ydata))

class LineMarker(Marker):
    #dashed line marker
    def __init__(self,ax,style,color):
        super().__init__(ax,style,color)
    
class HorizontalMarker(LineMarker):
    def __init__(self, ax, ydata, style, color):
        super().__init__(ax, style, color)
        self.ydata = ydata
        self.type = "horizontal"

        self.markerObj = self.ax.axhline(self.ydata,picker=True)
        self.markerObj.set_linestyle(self.style)
        self.markerObj.set_color(self.color)
        self.annotation = self.ax.annotate(f"({self.ydata:.2f})",(self.ax.get_xlim()[0],self.ydata))

        self.name = self.markerObj.get_label()

    def move(self,ydata):
        self.markerObj.set_ydata(ydata) 
        self.annotation.set_y(ydata)
        self.annotation.set_text(f"({ydata:.2f})")

class VerticalMarker(LineMarker):
    def __init__(self, ax, xdata, style, color):
        super().__init__(ax, style, color)
        self.xdata = xdata
        self.type = "vertical"

        self.markerObj = self.ax.axvline(self.xdata,picker=True)
        self.markerObj.set_linestyle(self.style)
        self.markerObj.set_color(self.color)
        self.annotation = self.ax.annotate(f"({self.xdata:.2f})",(self.xdata,self.ax.get_ylim()[0]))

        self.name = self.markerObj.get_label()

    def move(self,xdata):
        self.markerObj.set_xdata(xdata) 
        self.annotation.set_x(xdata)
        self.annotation.set_text(f"({xdata:.2f})")

class customTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.createWidgets()        
        self.addWidgetsToLayout()

        self.textInput.returnPressed.connect(lambda: self.returnPressed(self.textInput.text()))
        self.clearButton.pressed.connect(self.clearPressed)
        self.checkBox.toggled.connect(self.disableDropDownMenu)
        self.dropDownMenu.textActivated.connect(lambda string: self.dropDownMenuActivated(string))
        self.removeLegendButton.pressed.connect(self.removeLegendPressed)
        self.staticCanvas.mpl_connect("motion_notify_event",self.lineHoverEvent)
        self.staticCanvas.mpl_connect("button_press_event",self.rightClickMenuEvent)
        self.staticCanvas.mpl_connect("button_press_event",self.addVerticalMarker)
        self.staticCanvas.mpl_connect("button_press_event",self.addHorizontalMarker)
        self.staticCanvas.mpl_connect('button_release_event', self.on_release)
        self.staticCanvas.mpl_connect('motion_notify_event', self.on_motion)
        self.staticCanvas.mpl_connect('pick_event', self.pick_event)

        self.markers = {} #name of marker : Marker Object
        self.lines = {} #name of line : MainLine object
        self.current_marker = None

    
    def on_release(self,event):
        self.current_marker = None

    def pick_event(self,event):
        if(event.mouseevent.button==1):
            if event.artist.get_label() in self.lines:
                line = self.lines[event.artist.get_label()]
                if line.markerList:
                    for marker in line.markerList: #if marker is too close to another marker, disable adding a new one
                        dist = math.hypot(marker.xpixel - event.mouseevent.x, marker.ypixel - event.mouseevent.y)
                        if dist < 12:
                            return
                    self.addDotMarker(event)
                else:
                    self.addDotMarker(event)
            elif event.artist.get_label() in self.markers:
                self.current_marker = self.markers[event.artist.get_label()]  
            
    def on_motion(self, event):
        if self.current_marker is None:
            return
        if self.current_marker.type == "horizontal":
            self.current_marker.move(event.ydata)
        elif self.current_marker.type == "vertical": #move based on marker type
            self.current_marker.move(event.xdata)
        elif self.current_marker.type == "dot":
            self.current_marker.move(event.xdata)

        self.staticCanvas.draw()

    def addDotMarker(self,event):
            line = self.lines[event.artist.get_label()]
            x = event.mouseevent.xdata
            estimated_ydata = np.interp(x,line.lineObj.get_xdata(),line.lineObj.get_ydata()) #gets intersection of vertical line from x to line
            marker = DotMarker(self.ax,x,estimated_ydata,"o",None,line)
            self.lines[line.name].markerList.append(marker)
            self.markers[marker.name] = marker
            self.staticCanvas.draw()

    def addVerticalMarker(self,event):
        if (event.ydata):               #calculates 1/20 between max y value and min y value
            if(event.button==1) and (event.ydata <= self.calculateMarkerEdge(self.ax.get_ylim()[0],self.ax.get_ylim()[1],20)): 
                verticalMarker = VerticalMarker(self.ax,event.xdata,"--","red")
                self.markers[verticalMarker.name] = verticalMarker

    def addHorizontalMarker(self,event):
        if (event.xdata):
            if(event.button==1) and (event.xdata <= self.calculateMarkerEdge(self.ax.get_xlim()[0],self.ax.get_xlim()[1],20)): 
                horizontalMarker = HorizontalMarker(self.ax,event.ydata,"--","red")
                self.markers[horizontalMarker.name] = horizontalMarker

    def calculateMarkerEdge(self,a,b,fraction):
        return (b-a)/fraction + a

    def setVisibility(self,action):
        line = self.lines[action.text()]
        if line.get_visible():
            line.set_visible(False)
            action.setChecked(False)
        else:
            line.set_visible(True)
            action.setChecked(True)
        self.staticCanvas.draw()

    def rightClickMenuEvent(self,event):
        #opens right click popup
            pickedItem = False
            if (event.button == 3):    
                for marker in self.markers.values():
                    if marker.contains(event)[0]:
                        pickedItem = True
                        eventTrigger = marker
                        break
                
                if (pickedItem == True):
                    self.createMarkerMenu(eventTrigger)
                else:
                    self.createDefaultMenu()

    def createMarkerMenu(self,eventTrigger):
        self.markerMenu = QtWidgets.QMenu(self)
        self.markerMenu.addAction("Delete")
        self.markerMenu.popup(QCursor.pos())
        action = self.markerMenu.exec()
        if action is not None:
            self.removeMarker(eventTrigger)

    def removeMarker(self,marker):
        marker.remove()
        del self.markers[marker.name]

    def createDefaultMenu(self):
        self.contextMenu = QtWidgets.QMenu(self)
        for _,line in self.lines.items():
            act = self.contextMenu.addAction(line.name)
            act.setCheckable(True)
            if line.get_visible():
                act.setChecked(True)
            else:
                act.setChecked(False)
        self.contextMenu.popup(QCursor.pos())
        action = self.contextMenu.exec()
        if action is not None:
                self.setVisibility(action)

    def lineHoverEvent(self,event):
        #thickens line when mouse hover
        legend = self.ax.legend()
        for line in self.ax.get_lines():
            #line.set_picker(True)
            if line.contains(event)[0]: #returns bool if line contains event
                line.set_linewidth(2)
            #    line.set_picker(True)
            else:
                line.set_linewidth(1)
            #    line.set_picker(False)
            
            self.staticCanvas.blit(self.ax.bbox)
            self.staticCanvas.draw()
        
    def removeLegendPressed(self):
        self.ax.get_legend().remove()
        self.staticCanvas.draw()
        self.removeLegendButton.setEnabled(False)

    def dropDownMenuActivated(self,string):
        self.textOutput.append(string)
        self.clearButton.setEnabled(True)

    def disableDropDownMenu(self):
        #disables and enables the drop-down menu
        if self.dropDownMenu.isEnabled():
            self.dropDownMenu.setEnabled(False)
        else:
            self.dropDownMenu.setEnabled(True)

    def clearPressed(self):
        self.textOutput.clear()
        self.clearButton.setEnabled(False)

    def returnPressed(self,string):
        #appends text from inputText to outputText when enter is pressed
        self.textOutput.append(string)
        self.textInput.clear()
        self.clearButton.setEnabled(True)

    def createWidgets(self):
        #creates all the widgets inside customTab widget
        self.textOutput = QtWidgets.QTextEdit()
        self.textOutput.setReadOnly(True)
        self.textInput = QtWidgets.QLineEdit()
        self.clearButton = QtWidgets.QPushButton()
        self.clearButton.setText("Clear")
        self.clearButton.setEnabled(False)
        self.dropDownMenu = QtWidgets.QComboBox()
        self.dropDownMenu.addItem("lorem")
        self.dropDownMenu.addItem("ipsum")
        self.dropDownMenu.addItem("dolor")
        self.dropDownMenu.addItem("sit")
        self.dropDownMenu.addItem("amet")
        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setText("Disable Drop-down Menu")
        self.removeLegendButton = QtWidgets.QPushButton("Remove Legend")
        self.staticCanvas = FigureCanvas(Figure())
        self.navBar = NavigationToolbar2QT(self.staticCanvas,self)
        self.staticCanvas.hide()
        self.navBar.hide()


    def addWidgetsToLayout(self):
        #adds widgets to customTab
        self.tabLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.BottomToTop,self)
        self.inputLayout = QtWidgets.QVBoxLayout() 
        self.inputLayoutLeft = QtWidgets.QHBoxLayout() 
        self.inputLayoutRight = QtWidgets.QHBoxLayout()
        self.tabLayout.addLayout(self.inputLayout)
        self.inputLayout.addLayout(self.inputLayoutLeft)
        self.inputLayout.addLayout(self.inputLayoutRight)
        self.tabLayout.addWidget(self.textOutput)
        self.inputLayoutLeft.addWidget(self.clearButton)
        self.inputLayoutLeft.addWidget(self.textInput)        
        self.inputLayoutRight.addWidget(self.dropDownMenu)
        self.inputLayoutRight.addWidget(self.checkBox)
        self.inputLayoutRight.addWidget(self.removeLegendButton) 


class MainWindow(demoapp.Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabWidget.removeTab(1) #remove the 2 default tabs from qt designer
        self.tabWidget.removeTab(0)
        self.tabWidget.setTabsClosable(True)
        self.addNewTabButton = QtWidgets.QPushButton()
        self.addNewTabButton.setText("+")
        self.tabWidget.setCornerWidget(self.addNewTabButton)

        self.addNewTab()
        self.currentWidget = self.tabWidget.currentWidget()
        
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p","--path",type=str)
        self.args = self.parser.parse_args()
        if self.args.path:
            try:
                open(self.args.path,"r")
            except:
                print("file doesn't exist")
                exit()
            self.openCSVFile(self.args.path)


        self.addNewTabButton.pressed.connect(self.addNewTab)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.closeTab(index))
        self.actionOpen.triggered.connect(self.fileOpen)
        self.tabWidget.currentChanged.connect(self.changeCurrentTab)

    def changeCurrentTab(self):
        self.currentWidget = self.tabWidget.currentWidget()

    
    def fileOpen(self):
        filter = "Text Files,CSV Files (*.txt *.csv)"
        files,_ =  QtWidgets.QFileDialog.getOpenFileNames(self.currentTab,"","",filter)
        for filename in files:
            if filename != "": #if user doesn't select a file, the dialog returns an empty string
                if filename.endswith(".txt"):
                    self.openTxtFile(filename)
                elif filename.endswith(".csv"):
                    self.openCSVFile(filename)
    
    def openTxtFile(self,filename):
        #removes canvas, adds textOutput and appends text from file to Output
        self.removeCanvas()
        self.addTextOutput()
        with open(filename,"r") as data:
                    lines = data.read()
                    self.currentWidget.textOutput.append(lines)
    
    def addTextOutput(self):
        #adds textOutput to current tab
        self.currentWidget.textOutput = QtWidgets.QTextEdit()
        self.currentWidget.tabLayout.addWidget(self.currentWidget.textOutput)

    def removeCanvas(self):
        #removes canvas from current tab
        self.currentWidget.tabLayout.removeWidget(self.currentWidget.staticCanvas)
        self.currentWidget.tabLayout.removeWidget(self.currentWidget.navBar)

    def openCSVFile(self,filename):
        #opens csv file and plots it on canvas
        self.removeTextOutput()
        self.addCanvas()
        self.plot(filename)

    def plot(self,filename):
        #plots data from filename
        df = pandas.read_csv(filename)
        self.currentWidget.ax = self.currentWidget.staticCanvas.figure.subplots()
        df.plot(x="godina",ax=self.currentWidget.ax,picker=True)
        for line in self.currentWidget.ax.get_lines(): #adds lines to dict
            self.currentWidget.lines[line.get_label()] = MainLine(line)
        self.currentWidget.ax.set_ylabel("BDP")
        self.currentWidget.ax.set_title(os.path.basename(filename))

    def removeTextOutput(self):
        self.currentWidget.tabLayout.removeWidget(self.currentWidget.textOutput)
        self.currentWidget.textOutput.setVisible(False)

    def addCanvas(self):
        #adds canvas and navigation bar to current tab
        self.currentWidget.tabLayout.addWidget(self.currentWidget.staticCanvas)
        self.currentWidget.tabLayout.addWidget(self.currentWidget.navBar)
        self.currentWidget.staticCanvas.show()
        self.currentWidget.navBar.show()
            
    def closeTab(self,index):
        self.tabWidget.removeTab(index)

    def addNewTab(self):
        self.currentTab = customTab()
        self.tabWidget.addTab(self.currentTab,"New Tab")
        self.tabWidget.setCurrentWidget(self.currentTab)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())



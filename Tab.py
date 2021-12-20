from Marker import DotMarker,VerticalMarker,HorizontalMarker
from MainLine import MainLine

from PyQt6 import QtWidgets
from PyQt6.QtGui import QCursor
from matplotlib.backends.backend_qtagg import FigureCanvas,NavigationToolbar2QT
from matplotlib.figure import Figure

import math
import numpy as np
import pandas
import os



class Tab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.createWidgets()        
        self.addWidgetsToLayout()
        self.connectTab()

        self.ax = self.staticCanvas.figure.subplots()
        self.markers = {} #name of marker : Marker Object
        self.lines = {} #name of line : MainLine object
        self.current_marker = None
        self.model = None

    def connectTab(self):
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

    def on_release(self,event):
        self.current_marker = None

    def pick_event(self,event):
        if(event.mouseevent.button==1): #left click
            if event.artist.get_label() in self.lines: #if artist is line
                line = self.lines[event.artist.get_label()]
                if line.markerList:
                    for marker in line.markerList: #if marker is too close to another marker, disable adding a new one
                        dist = math.hypot(marker.xdata - event.mouseevent.xdata, marker.ydata - event.mouseevent.ydata)
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
                self.staticCanvas.draw()

    def addHorizontalMarker(self,event):
        if (event.xdata):
            if(event.button==1) and (event.xdata <= self.calculateMarkerEdge(self.ax.get_xlim()[0],self.ax.get_xlim()[1],20)): 
                horizontalMarker = HorizontalMarker(self.ax,event.ydata,"--","red")
                self.markers[horizontalMarker.name] = horizontalMarker
                self.staticCanvas.draw()

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
            if line.contains(event)[0]: #returns bool if line contains event
                line.set_linewidth(2)
            else:
                line.set_linewidth(1)
            
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
    
    def plot(self,filename):
        df = pandas.read_csv(filename)
        df.plot(x="godina",ax=self.ax,picker=True)
        for line in self.ax.get_lines(): #adds lines to dict
            self.lines[line.get_label()] = MainLine(line)
        self.ax.set_ylabel("BDP")
        self.ax.set_title(os.path.basename(filename))
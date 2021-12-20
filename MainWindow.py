from PyQt6 import QtWidgets
from PyQt6 import QtCore
from PyQt6.QtGui import QStandardItem, QStandardItemModel
import demoapp
import os
import argparse
import json

from Tab import Tab

class Model(QStandardItemModel):
    itemDataChanged = QtCore.Signal(object, object)

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole): #called when Item changes
        oldvalue = index.data(role)
        result = super(Model, self).setData(index, value, role) #true if setData successful
        if result and value != oldvalue:
            self.itemDataChanged.emit(self.itemFromIndex(index), role) #emits signal with role
        return result

class MainWindow(demoapp.Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.initializeMainWindow()
        self.connectMainWindow()
        
        for path in self.parserargs():
            self.openCSVFile(path)
        
    def connectMainWindow(self):
        self.addNewTabButton.pressed.connect(self.addNewTab)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.closeTab(index))
        self.actionOpen.triggered.connect(self.fileOpen)
        self.tabWidget.currentChanged.connect(self.changeCurrentTab)
        self.actionDock.triggered.connect(self.dockVisible)
    
    def initializeMainWindow(self):
        self.tabWidget.removeTab(1) #remove the 2 default tabs from qt designer
        self.tabWidget.removeTab(0)
        self.tabWidget.setTabsClosable(True)
        self.addNewTabButton = QtWidgets.QPushButton()
        self.addNewTabButton.setText("+")
        self.tabWidget.setCornerWidget(self.addNewTabButton)
        self.addNewTab()
        self.currentWidget = self.tabWidget.currentWidget()
        self.createDock()

    def parserargs(self):
        #returns list of arguments from command line
        args = []
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p","--path",nargs="+",type=str)
        self.args = self.parser.parse_args()
        if self.args.path != None:
            for path in self.args.path:
                if path:
                    if os.path.isfile(path):
                        args.append(path)
        return args

    def fillStandardModel(self):
        #makes and returns model for treeView
        with open("countries.json","r") as f:
            data = json.load(f)
        standardModel = Model(0,2,self)
        standardModel.setHeaderData(0,QtCore.Qt.Orientation.Horizontal,"GDP per capita")
        standardModel.setHeaderData(1,QtCore.Qt.Orientation.Horizontal,"Population")

        root = standardModel.invisibleRootItem()

        for continent in data['continents']:
            continentItem = QStandardItem(continent["name"])
            continentItem.setEditable(False)
            
            for country in continent["countries"]:
                countryItem = QStandardItem(country["name"])
                countryItem.setEditable(False)
                
                if countryItem.text() in self.currentWidget.lines:
                    countryItem.setFlags(countryItem.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                    if self.currentWidget.lines[countryItem.text()].get_visible():
                        countryItem.setCheckState(QtCore.Qt.CheckState.Checked)
                    else:
                        countryItem.setCheckState(QtCore.Qt.CheckState.Unchecked)

                    continentItem.appendRow(countryItem)
                    gdpItem = QStandardItem(country["gdp"])
                    gdpItem.setEditable(False)
                    populationItem = QStandardItem(country["population"])
                    populationItem.setEditable(False)
                    countryItem.appendRow((gdpItem,populationItem))
            
            if continentItem.hasChildren():
                root.appendRow(continentItem)  
        
        return standardModel

    def dockVisible(self):
        if not self.dock.isVisible():
            self.dock.setVisible(True)
    
    def createDock(self):
        #creates dock and tree view inside it
        self.treeView = QtWidgets.QTreeView()
        self.dock = QtWidgets.QDockWidget("Tree View")
        self.dock.setWidget(self.treeView)
        self.createTreeView()
        self.dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea,self.dock)
    
    def createTreeView(self):
        self.currentWidget.model = self.fillStandardModel()
        self.currentWidget.model.itemDataChanged.connect(self.handleItemDataChanged) #event for model
        self.updateTreeView()    
    
    def updateTreeView(self):
        self.treeView.setModel(self.currentWidget.model)
        self.treeView.expandAll()
        self.treeView.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def handleItemDataChanged(self, item, role):
        #select functionality based on role
        if role == QtCore.Qt.ItemDataRole.CheckStateRole:
            self.hideLineFromTree(item)

    def hideLineFromTree(self,item):
        #hides checked country from graph
        linename = item.text()
        if item.checkState() == QtCore.Qt.CheckState.Unchecked:
            self.currentWidget.lines[linename].set_visible(False)
            self.currentWidget.staticCanvas.draw()
        elif item.checkState() == QtCore.Qt.CheckState.Checked:
            self.currentWidget.lines[linename].set_visible(True)
            self.currentWidget.staticCanvas.draw()

    def changeCurrentTab(self):
        self.currentWidget = self.tabWidget.currentWidget()
        self.updateTreeView()

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
        self.addNewTab()
        self.removeTextOutput()
        self.addCanvas()
        self.drawCanvas(filename)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.currentWidget),os.path.basename(filename))
        self.createTreeView()

    def drawCanvas(self,filename):
        #plots data from filename
        self.currentWidget.plot(filename)

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

    def addNewTab(self): #tabname umesto filename
        self.currentTab = Tab()
        self.tabWidget.addTab(self.currentTab,"New Tab")
        self.tabWidget.setCurrentWidget(self.currentTab)
        self.currentWidget = self.currentTab
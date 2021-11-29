from PyQt6 import QtWidgets
from PyQt6.QtGui import QCursor
from matplotlib.figure import Figure
import demoapp
import sys
import pandas
from matplotlib.backends.backend_qtagg import FigureCanvas,NavigationToolbar2QT
import os


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

        self.lines = {} #name of line : line object

    def setVisibility(self,action):
        #index = self.actionDict[action]
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
        if(event.button == 3): #if the clicked button is Right Click
            self.contextMenu = QtWidgets.QMenu(self)
            for line in self.ax.get_lines():
                lineName = line.get_label()
                act = self.contextMenu.addAction(lineName)
                act.setCheckable(True)
                if line.get_visible():
                    act.setChecked(True)
                else:
                    act.setChecked(False)
            self.contextMenu.popup(QCursor.pos())
            self.action = self.contextMenu.exec()
            if self.action is not None:
                    self.setVisibility(self.action)

    def lineHoverEvent(self,event):
        #thickens line when mouse hover
        legend = self.ax.legend()
        for line in self.ax.get_lines():
            if line.contains(event)[0]: #returns bool if line contains event
                line.set_linewidth(5)
            else:
                line.set_linewidth(1)
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
        #if not self.currentWidget.staticCanvas.axes():
        self.addCanvas()
        self.plot(filename)

    def plot(self,filename):
        #plots data from filename
        df = pandas.read_csv(filename)
        self.currentWidget.ax = self.currentWidget.staticCanvas.figure.subplots()
        df.plot(x="godina",ax=self.currentWidget.ax)
        for line in self.currentWidget.ax.get_lines(): #adds lines to dict
            self.currentWidget.lines[line.get_label()] = line
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



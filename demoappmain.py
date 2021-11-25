from PyQt6 import QtWidgets
from matplotlib.figure import Figure
import demoapp
import sys
import pandas
from matplotlib.backends.backend_qtagg import FigureCanvas,NavigationToolbar2QT

class customTab(QtWidgets.QWidget):
    #def __init__(self, main_app):
    def __init__(self):
        super().__init__()
    
        #self.main_app = main_app
        self.createWidgets()        
        self.addWidgetsToLayout()

        self.textInput.returnPressed.connect(lambda: self.returnPressed(self.textInput.text()))
        self.clearButton.pressed.connect(self.clearPressed)
        self.checkBox.toggled.connect(self.disableDropDownMenu)
        self.dropDownMenu.textActivated.connect(lambda string: self.dropDownMenuActivated(string))

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
        #self.staticCanvas = FigureCanvas(Figure(figsize=(2,2)))
        #self.navBar = NavigationToolbar2QT(self.staticCanvas,self)
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
        #self.textOutput.setEnabled(False)
        #self.tabLayout.addWidget(self.staticCanvas)
        #self.tabLayout.addWidget(self.navBar)
        self.inputLayoutLeft.addWidget(self.clearButton)
        self.inputLayoutLeft.addWidget(self.textInput)        
        self.inputLayoutRight.addWidget(self.dropDownMenu)
        self.inputLayoutRight.addWidget(self.checkBox) 


        

    

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
        self.currentWidget = self.tabWidget.currentWidget()

        #tab0 = customTab(main_app=self)
        self.addNewTab()

        self.addNewTabButton.pressed.connect(self.addNewTab)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.closeTab(index))
        self.actionOpen.triggered.connect(self.fileOpen)
        self.tabWidget.currentChanged.connect(self.changeCurrentTab)

    def changeCurrentTab(self):
        self.currentWidget = self.tabWidget.currentWidget()

    
    def fileOpen(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self.currentTab,"","","All files (*.*);;Text Files (*.txt,);;CSV Files (*.csv)")
        filename = file[0]
        if filename != "": #if user doesn't select a file, the dialog returns an empty string
            self.changeCurrentTab()
            if filename.endswith(".txt"):
                self.openTxtFile(filename)
            elif filename.endswith(".csv"):
                self.openCSVFile(filename)
    
    def openTxtFile(self,filename):
        with open(filename,"r") as data:
                    lines = data.read()
                    self.currentWidget.textOutput.append(lines)

    def openCSVFile(self,filename):
        """
        df = pandas.read_csv(filename)
        for columnName in df:
            column = df[columnName].tolist()
            stringFromInts = [str(int) for int in column]
            string = columnName + ": " + ",".join(stringFromInts)
            self.currentWidget.textOutput.append(string)
        """
        self.removeTextOutput()
        self.addCanvas()
        self.plot(filename)

    def plot(self,filename):
        df = pandas.read_csv(filename)
        ax = self.currentWidget.staticCanvas.figure.subplots()
        ax.plot(df)

    def removeTextOutput(self):
        self.currentWidget.tabLayout.removeWidget(self.currentWidget.textOutput)

    def addCanvas(self):
        self.currentWidget.staticCanvas = FigureCanvas(Figure(figsize=(2,2)))
        self.currentWidget.navBar = NavigationToolbar2QT(self.currentWidget.staticCanvas,self)
        self.currentWidget.tabLayout.addWidget(self.currentWidget.staticCanvas)
        self.currentWidget.tabLayout.addWidget(self.currentWidget.navBar)
            

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



from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
import demoapp
import sys

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
        self.textOutput = QtWidgets.QTextEdit()
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
        """
        #self.tablayout.addWidget(self.textOutput,0,0,1,2)
        #self.tablayout.addWidget(self.clearButton,1,0)
        #self.tablayout.addWidget(self.textInput,1,1)
        #self.tablayout.addWidget(self.dropDownMenu,2,0)
        #self.tablayout.addWidget(self.checkBox,2,1)    
        """
        self.tablayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.BottomToTop,self)
        self.layout1 = QtWidgets.QVBoxLayout() 
        self.layout2 = QtWidgets.QHBoxLayout() 
        self.layout3 = QtWidgets.QHBoxLayout()
        self.tablayout.addLayout(self.layout1)
        self.layout1.addLayout(self.layout2)
        self.layout1.addLayout(self.layout3)

        self.tablayout.addWidget(self.textOutput)

        self.layout2.addWidget(self.clearButton)
        self.layout2.addWidget(self.textInput)        
        
        self.layout3.addWidget(self.dropDownMenu)
        self.layout3.addWidget(self.checkBox) 

        

    

class MainWindow(demoapp.Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabWidget.removeTab(1) #remove the 2 default tabs from qt designer
        self.tabWidget.removeTab(0)

        #tab0 = customTab(main_app=self)
        tab0 = customTab()
        self.tabWidget.addTab(tab0,"new tab")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())



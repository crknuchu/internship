from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
import demoapp
import sys

class customTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
    
        self.createWidgets()        
        self.addWidgetsToLayout()

    def createWidgets(self):
        self.tablayout = QtWidgets.QGridLayout(self)
        self.textOutput = QtWidgets.QTextEdit()
        self.textInput = QtWidgets.QLineEdit()
        self.clearButton = QtWidgets.QPushButton()
        self.clearButton.setText("Clear")
        self.dropDownMenu = QtWidgets.QComboBox()
        self.dropDownMenu.addItem("temp")
        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setText("temp")

    def addWidgetsToLayout(self):
        self.tablayout.addWidget(self.textOutput,0,0,1,2)
        self.tablayout.addWidget(self.clearButton,1,0)
        self.tablayout.addWidget(self.textInput,1,1)
        self.tablayout.addWidget(self.dropDownMenu,2,0)
        self.tablayout.addWidget(self.checkBox,2,1)    
    
        #self.tablayout.addWidget(self.textOutput)
        #self.tablayout.addWidget(self.textInput)
        #self.tablayout.addWidget(self.clearButton)
        #self.tablayout.addWidget(self.dropDownMenu)
        #self.tablayout.addWidget(self.checkBox) 

        

    

class MainWindow(demoapp.Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabWidget.removeTab(1) #remove the 2 default tabs from qt designer
        self.tabWidget.removeTab(0)

        tab0 = customTab()
        self.tabWidget.addTab(tab0,"new tab")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())



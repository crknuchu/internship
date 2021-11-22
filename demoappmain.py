from PyQt6 import QtWidgets
import demoapp
import sys

class customTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
    
    tablayout = QtWidgets.QVBoxLayout()

class MainWindow(demoapp.Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabWidget.removeTab(1)
        self.tabWidget.removeTab(0)

        tab0 = customTab()
        self.tabWidget.addTab(tab0,"new tab")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())




from MainWindow import MainWindow
from PyQt6 import QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())



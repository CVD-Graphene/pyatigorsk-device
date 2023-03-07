import sys
# sys.settrace()
import os

from PyQt5 import QtGui

os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'Core.settings')

from PyQt5.QtWidgets import (
    QApplication,
)
from PyQt5.QtCore import Qt
from Structure.dialog_ui import MainWindow

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
# print("FORMATS", QtGui.QImageReader.supportedImageFormats())

# sys.exit(0)
app = QApplication([])
w = MainWindow()
# w.show()
# w.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask)
# w.showFullScreen()
w.setWindowState(Qt.WindowFullScreen)
w.setVisible(True)
# w.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowType_Mask)
# w.setWindowFlags(Qt.WindowType_Mask)
app.exec()

print("Exit")

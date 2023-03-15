import os
os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'Core.settings')

import tracemalloc

from PyQt5 import QtGui

from PyQt5.QtWidgets import (
    QApplication,
)
from PyQt5.QtCore import Qt
from Structure.dialog_ui import MainWindow

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
# print("FORMATS", QtGui.QImageReader.supportedImageFormats())

tracemalloc.start()

def start():
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

# from Core.actions import ACTIONS
#
# def start_system():
#     system = CvdSystem(actions_list=ACTIONS)
#     system.setup()
#     system.threads_setup()
#     try:
#         while True:
#             sleep(1)
#     except BaseException:
#         system.stop()
#         system.destructor()


if __name__ == '__main__':
    start()

print("Exit")

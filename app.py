import os
os.environ.setdefault('GRAPHENE_SETTINGS_MODULE', 'Core.settings')

import tracemalloc
from Core.actions import ACTIONS
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from Structure.system import AppSystem
from Structure.dialog_ui import AppMainDialogWindow

os.environ["QT_VIRTUALKEYBOARD_STYLE"] = "testkeyboard10" #"testkeyboard1"
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

tracemalloc.start()


def handleVisibleChanged():
    if not QtGui.QGuiApplication.inputMethod().isVisible():
        return
    for w in QtGui.QGuiApplication.allWindows():
        if w.metaObject().className() == "QtVirtualKeyboard::InputView":
            keyboard = w.findChild(QtCore.QObject, "keyboard")
            if keyboard is not None:
                r = w.geometry()
                r.moveTop(int(keyboard.property("y")))
                w.setMask(QtGui.QRegion(r))
                return


def start():
    # sys.exit(0)
    app = QApplication([])

    inputMethod = app.inputMethod()
    inputMethod.visibleChanged.connect(handleVisibleChanged)

    system = AppSystem(
        actions_list=ACTIONS
    )
    system.setup()
    system.threads_setup()

    w = AppMainDialogWindow(system=system)
    w.system_connect()

    w.setWindowState(Qt.WindowFullScreen)
    w.setVisible(True)
    screen_h = app.desktop().screenGeometry().height()
    # w.setFixedHeight(screen_h + 300)
    max_shift = screen_h
    w.main_widget.setFixedHeight(screen_h + max_shift)
    w.main_widget.setContentsMargins(0, max_shift, 0, 0)
    w.setFixedWidth(app.desktop().screenGeometry().width())
    w.main_widget.setFixedWidth(app.desktop().screenGeometry().width())
    w.main_widget.move(0, -max_shift)

    def is_visible():
        visible = inputMethod.isVisible()
        pos_y = inputMethod.anchorRectangle().y()
        shift_bottom = int(max(0.0, pos_y - screen_h * 0.4))
        shift_top = max_shift - shift_bottom

        if visible:
            w.main_widget.setContentsMargins(0, shift_top, 0, shift_bottom)
            w.table_widget.move(0, -shift_bottom)
        else:
            w.main_widget.setContentsMargins(0, max_shift, 0, 0)
            w.table_widget.move(0, 0)

    w.main_widget.setAttribute(Qt.WA_Moved, True)
    inputMethod.visibleChanged.connect(is_visible)

    app.exec()


if __name__ == '__main__':
    start()

print("Exit")

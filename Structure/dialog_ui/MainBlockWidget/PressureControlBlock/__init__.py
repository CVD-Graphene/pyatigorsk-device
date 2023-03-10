from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from Structure.dialog_ui.MainBlockWidget.TemperatureBlock.FlowControlWidget import FlowControlWidget
from Structure.dialog_ui.MainBlockWidget.TemperatureBlock.ShowPressureBlock import ShowPressureBlock
from .styles import styles


class PressureControlBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(styles.container)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.show_pressure_block = ShowPressureBlock()
        self.layout.addWidget(self.show_pressure_block,
                              alignment=QtCore.Qt.AlignTop
                              )

        # self.input = QLineEdit()
        # self.input.setStyleSheet("""
        # background-color: rgb(255, 255, 255);
        # max-width: 200px;
        # font-size: 24px;
        # """)
        # # self.input.clearFocus()
        # self.layout.addWidget(self.input)

        self.pump_widget = FlowControlWidget(title="Pump")
        self.vent_widget = FlowControlWidget(title="Vent")
        self.layout.addWidget(self.pump_widget)
        self.layout.addWidget(self.vent_widget)

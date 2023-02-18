from coregraphene.conf import settings

from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout

from .CurrentSettingsBlock import CurrentSettingsBlock
from .FlowControlWidget import FlowControlWidget
from .SetTemperatureBlock import SetTemperatureBlock
from .ShowPressureBlock import ShowPressureBlock
from .styles import styles


class TemperatureBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName("temperature_block_widget")
        self.setStyleSheet(styles.container)
        # self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.show_pressure_block = ShowPressureBlock()
        self.layout.addWidget(
            self.show_pressure_block,
            alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft
        )

        self.temps_layout = QHBoxLayout()

        self.temps = dict()
        for num, _ in enumerate(settings.TERMODAT_CONFIGURATION):
            t_obj = SetTemperatureBlock(num)
            self.temps[num] = t_obj

        # self.set_temperature = SetTemperatureBlock()
        # self.layout.addWidget(self.set_temperature, QtCore.Qt.AlignTop)

        for k, v in self.temps.items():
            self.temps_layout.addWidget(
                v, alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.layout.addLayout(self.temps_layout)

        self.vent_widget = FlowControlWidget(title="Vent")
        self.layout.addWidget(self.vent_widget,
                              alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)


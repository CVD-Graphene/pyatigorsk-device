from coregraphene.conf import settings

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from .GasStateWidget import GasStateWidget, AirStateWidget
from .ValveControlWidget import ValveControlWidget
from .styles import styles


class PressureBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(14, 14, 2, 14)
        self.setObjectName("pressure_block")
        self.setStyleSheet(styles.container)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.control_valve = ValveControlWidget()
        self.layout.addWidget(self.control_valve)

        self.air = AirStateWidget()
        self.layout.addWidget(self.air)

        self.gases = []

        for i, valve_config in enumerate(settings.VALVES_CONFIGURATION):
            gas = valve_config['NAME']
            max_sccm = valve_config.get('MAX_SCCM', settings.MAX_DEFAULT_SCCM_VALUE)
            gas_widget = GasStateWidget(gas=gas, number=i, max_sccm=max_sccm)
            setattr(self, gas, gas_widget)

            gas_attr = getattr(self, gas)
            self.layout.addWidget(gas_attr)
            self.gases.append(gas_attr)

    def draw_set_gas_target_sccm(self, sccm, gas_num):
        self.gases[gas_num].draw_set_target_sccm(sccm)

    def draw_is_open_gas(self, is_open, gas_num):
        self.gases[gas_num].draw_is_open(is_open)

    def draw_is_open_air(self, is_open):
        self.air.draw_is_open(is_open)

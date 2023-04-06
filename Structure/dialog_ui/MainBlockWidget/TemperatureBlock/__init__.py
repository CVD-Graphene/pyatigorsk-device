from coregraphene.conf import settings
from grapheneqtui.components import ShowPressureBlock, TermodatTemperatureBlock

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from .CurrentSettingsBlock import CurrentSettingsBlock
from .FlowControlWidget import FlowControlWidget
from .styles import styles


class TemperatureBlock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.system_set_temperature = None
        self.system_set_speed = None
        self.system_set_active_regulation = None

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
            t_obj = TermodatTemperatureBlock(
                num,
                max_speed=settings.TERMODAT_MAX_SPEED,
                default_speed=settings.TERMODAT_DEFAULT_SPEED,
            )
            self.temps[num] = t_obj

            t_obj.system_set_temperature = self._on_set_temperature
            t_obj.system_set_speed = self._on_set_speed
            t_obj.system_set_active_regulation = self._on_set_active_regulation

        # self.set_temperature = TermodatTemperatureBlock(...args!)
        # self.layout.addWidget(self.set_temperature, QtCore.Qt.AlignTop)

        for k, v in self.temps.items():
            self.temps_layout.addWidget(
                v, alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.layout.addLayout(self.temps_layout)

        self.vent_widget = FlowControlWidget(title="Vent")
        self.layout.addWidget(self.vent_widget,
                              alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

    def _on_set_temperature(self, value, device_num):
        if self.system_set_temperature is not None:
            # FOR SINGLE SETTER:
            # self.system_set_temperature(value, device_num)

            for i in range(len(self.temps)):
                self.system_set_temperature(value, i)
            for t_obj in self.temps.values():
                t_obj.temperature_input.input.setText(str(value))

    def _on_set_speed(self, value, device_num):
        if self.system_set_speed is not None:
            # FOR SINGLE SETTER:
            # self.system_set_speed(value, device_num)

            for i in range(len(self.temps)):
                self.system_set_speed(value, i)
            for t_obj in self.temps.values():
                t_obj.speed_input.input.setText(str(value))

    def _on_set_active_regulation(self, value, device_num):
        if self.system_set_active_regulation is not None:
            # FOR SINGLE SETTER:
            # self.system_set_active_regulation(value, device_num)

            for i in range(len(self.temps)):
                self.system_set_active_regulation(value, i)
            for t_obj in self.temps.values():
                t_obj.set_is_active_regulation(value)

    def draw_is_active_termodats_regulation(self, is_active):
        for t_obj in self.temps.values():
            t_obj.set_is_active_regulation(is_active)

    def draw_temperature_and_speed_termodats(self, temperature, speed):
        for t_obj in self.temps.values():
            t_obj.draw_target_temperature(temperature)
            t_obj.draw_target_speed(speed)

    def draw_temperature_termodats(self, temperature):
        for t_obj in self.temps.values():
            t_obj.draw_target_temperature(temperature)

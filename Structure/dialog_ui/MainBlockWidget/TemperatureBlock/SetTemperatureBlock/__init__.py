import random
from coregraphene.conf import settings

from PyQt5 import QtCore
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect, \
    QLineEdit, QLabel, QHBoxLayout, QPushButton

from Structure.dialog_ui.constants import SHADOW_BLUR_RADIUS
from .styles import styles


class TemperatureInputLine(QWidget):
    def __init__(self,
                 label_1="T =",
                 label_2="°C",
                 input_validator_args=None,
                 parent=None):
        super().__init__(parent=parent)

        if input_validator_args is None:
            input_validator_args = [0, 60, 2]

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(styles.input_container)

        self.label_1 = QLabel()
        self.label_1.setText(label_1)
        self.label_1.setStyleSheet(styles.label)

        self.label_2 = QLabel()
        self.label_2.setText(label_2)
        self.label_2.setStyleSheet(styles.label)

        self.input = QLineEdit()
        self.input.setStyleSheet(styles.input)
        self.input.setValidator(QDoubleValidator(*input_validator_args))

        self.layout.addWidget(self.label_1, stretch=1, alignment=QtCore.Qt.AlignTop)
        self.layout.addWidget(self.input, stretch=3)
        self.layout.addWidget(self.label_2, 1)


class SetTemperatureBlock(QWidget):
    def __init__(self, number, parent=None):
        super().__init__(parent=parent)
        self.number = number
        self.is_active = False
        self.system_set_temperature = None
        self.system_set_speed = None
        self.system_set_active_regulation = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(styles.container)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        shadow = QGraphicsDropShadowEffect(parent=self)
        shadow.setBlurRadius(SHADOW_BLUR_RADIUS)
        self.setGraphicsEffect(shadow)

        self.title = QLabel()
        self.title.setText("Set temp")
        self.title.setStyleSheet(styles.title)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.current_temperature = QLabel()
        self.current_temperature.setText("T= 20.0 °C")
        self.current_temperature.setStyleSheet(styles.title)
        self.current_temperature.setAlignment(QtCore.Qt.AlignCenter)

        self.speed_input = TemperatureInputLine(
            label_1="T' = ", label_2="°C/ч",
            input_validator_args=[0, settings.TERMODAT_MAX_SPEED, 1]
        )
        self.speed_input.input.setText(str(settings.TERMODAT_DEFAULT_SPEED))
        self.speed_input.input.returnPressed.connect(self._on_change_speed)

        self.temperature_input = TemperatureInputLine()
        self.temperature_input.input.returnPressed.connect(self._on_change_temperature)

        self.state_button = QPushButton()
        # self.state_button.setText("START")
        self.update_active_button()
        self.state_button.clicked.connect(self._on_click_state_button)

        self.layout.addWidget(self.speed_input, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.current_temperature, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.temperature_input, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.state_button, alignment=QtCore.Qt.AlignCenter)

    def set_current_temperature(self, value):
        self.current_temperature.setText(f"T= {round(random.random() * 9)}: {value} °C")

    def _on_change_speed(self):
        speed = self.speed_input.input.text()
        try:
            if self.system_set_speed is not None and speed:
                self.system_set_speed(float(speed), self.number)
        except Exception as e:
            print("Change speed exception:", e)

    def _on_change_temperature(self):
        temperature = self.temperature_input.input.text()
        try:
            if self.system_set_temperature is not None and temperature:
                self.system_set_temperature(float(temperature), self.number)
        except Exception as e:
            print("Change temperature exception:", e)

    def update_active_button(self):
        self.state_button.setText("STOP" if self.is_active else "START")

    def _on_click_state_button(self):
        if self.system_set_active_regulation is not None:
            self.is_active = not self.is_active
            self.system_set_active_regulation(self.is_active, self.number)
        self.state_button.setText("STOP" if self.is_active else "START")

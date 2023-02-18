import random
from coregraphene.conf import settings

from PyQt5 import QtCore
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect, \
    QLineEdit, QLabel, QHBoxLayout, QBoxLayout, QSizePolicy

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

        self.speed_input = TemperatureInputLine(label_1="T' = ", label_2="°C/c")
        self.temperature_input = TemperatureInputLine()

        self.layout.addWidget(self.speed_input, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.current_temperature, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.temperature_input, alignment=QtCore.Qt.AlignCenter)

    def set_current_temperature(self, value):
        self.current_temperature.setText(f"T= {round(random.random() * 9)}: {value} °C")

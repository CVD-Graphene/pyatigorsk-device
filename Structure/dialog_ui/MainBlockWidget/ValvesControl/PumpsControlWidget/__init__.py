from coregraphene.conf import settings
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from grapheneqtui.components import ButterflyButton, PumpButton
from grapheneqtui.constants import BUTTERFLY_BUTTON_STATE
from grapheneqtui.utils import StyleSheet

styles = StyleSheet({
    "container": {
        "name": "QWidget#valve_control_widget",
        "max-height": "200px",
    },
})

PUMPS_CONFIGURATION = settings.PUMPS_CONFIGURATION


class PumpsControlWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)

        self.big_pump_num = settings.BIG_PUMP_INDEX  # 0 if "big" in PUMPS_CONFIGURATION[0]['NAME'].lower() else 1
        self.small_pump_num = settings.SMALL_PUMP_INDEX  # 0 if self.big_pump_num == 1 else 0

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(styles.container)
        self.setObjectName("valve_control_widget")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.button = PumpButton()

        self.big_pump = ButterflyButton()
        self.small_pump = ButterflyButton()

        self.valves_layout = QVBoxLayout()
        self.valves_layout.addWidget(
            self.big_pump, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignHCenter)

        self.small_pump_layout = QHBoxLayout()
        self.small_pump_label = QLabel('small pump')
        self.small_pump_layout.addWidget(
            self.small_pump_label, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignHCenter)
        self.small_pump_layout.addWidget(
            self.small_pump, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignHCenter)

        self.valves_layout.addLayout(self.small_pump_layout)

        # self.layout.addStretch(2)
        self.layout.addWidget(self.button, stretch=1, alignment=QtCore.Qt.AlignCenter,)
        # self.layout.addWidget(self.b, stretch=4, alignment=QtCore.Qt.AlignHCenter,)
        self.layout.addLayout(self.valves_layout)

    def draw_big_pump_is_open(self, is_open: bool):
        state = BUTTERFLY_BUTTON_STATE.OPEN if is_open else BUTTERFLY_BUTTON_STATE.CLOSE
        self.big_pump.update_state_signal.emit(state)
        # self.big_pump.update_active(is_open)

    def draw_small_pump_is_open(self, is_open: bool):
        state = BUTTERFLY_BUTTON_STATE.OPEN if is_open else BUTTERFLY_BUTTON_STATE.CLOSE
        self.small_pump.update_state_signal.emit(state)
        # self.small_pump.update_active(is_open)

    def connect_big_pump_valve_function(self, func):
        def on_click():
            ans = func(self.big_pump_num)
            if type(ans) in [bool, int]:
                self.draw_big_pump_is_open(ans)

        self.big_pump.clicked.connect(on_click)

    def connect_small_pump_valve_function(self, func):
        def on_click():
            ans = func(self.small_pump_num)
            if type(ans) in [bool, int]:
                self.draw_small_pump_is_open(ans)

        self.small_pump.clicked.connect(on_click)

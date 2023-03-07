from coregraphene.conf import settings
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainterPath, QColor, QPainter
from PyQt5.QtWidgets import QPushButton, QWidget, QGridLayout, \
    QVBoxLayout, QLineEdit, QHBoxLayout, QLabel

from Structure.dialog_ui.components.butterfly_button import ButterflyButton
from .styles import styles, button_style, button_style1

PUMPS_CONFIGURATION = settings.PUMPS_CONFIGURATION


class ValveControlWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)

        # self.line = QWidget(self)
        # self.line.setStyleSheet(styles.line)
        # self.line.setFixedWidth(self.width() - 180)
        # print("HEIGHT!!!", self.height() // 2) # 240 = h/2 ????
        # self.line.move(180, 60)  # -self.height() // 2

        self.big_pump_num = settings.BIG_PUMP_INDEX  # 0 if "big" in PUMPS_CONFIGURATION[0]['NAME'].lower() else 1
        self.small_pump_num = settings.SMALL_PUMP_INDEX  # 0 if self.big_pump_num == 1 else 0

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet(styles.container)
        self.setObjectName("valve_control_widget")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.button = ValveControlButton()
        # self.button.setObjectName("button_valve_control")
        # self.button.setStyleSheet(button_style)

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

    def draw_big_pump_is_open(self, is_open):
        self.big_pump.update_active(is_open)

    def draw_small_pump_is_open(self, is_open):
        self.small_pump.update_active(is_open)

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


class ValveControlButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName("button_valve_control")
        self.setStyleSheet(button_style)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        # self.button = QPushButton()
        # self.button.setObjectName("button_valve_control")
        # self.button.setStyleSheet(button_style)
        self.w = ValveLines()
        self.layout.addWidget(self.w)


class ValveLines(QWidget):
    def __init__(self):
        super().__init__()
        # self.layout = QHBoxLayout()
        # self.setLayout(self.layout)
        # self.setObjectName("button_valve_control")
        self.setStyleSheet("""
            width: 90px;
            min-width: 90px;
            height: 90px;
            min-height: 90px;
            border-radius: 45px;
            transform: [{rotate: 60deg}];
            background-color: #FFFFFF;
        """)
        s = """
            background-color: #FFFFFF;
        """
        s = ""
        s += f"min-height: {int(90 / 2 * (1 + 2 ** 0.5 / 2))}px;"
        self.setStyleSheet(s)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        #
        # # self.button = QPushButton()
        # # self.button.setObjectName("button_valve_control")
        # # self.button.setStyleSheet(button_style)
        # self.w = QWidget()
        # self.layout.addWidget(self.w)

    def paintEvent(self, event):
        try:
            qp = QPainter()
            # qp.begin(self.button)
            qp.begin(self)

            # a = randint(10, 100)
            # d = a * math.tan(math.radians(30))
            x, y = 0, 0

            pos_1 = QPointF(9, 0)
            pos_2 = QPointF(30, 99)

            pos_3 = QPointF(64, y)
            pos_4 = QPointF(38, 90)

            qp.setBrush(QColor(0, 0, 0))
            path = QPainterPath()
            path.moveTo(pos_1)
            path.lineTo(pos_2)

            path2 = QPainterPath()
            path2.moveTo(pos_4)
            path2.lineTo(pos_3)

            # qp.rotate(7)
            qp.drawPath(path)
            qp.drawPath(path2)


            qp.end()
        except Exception as e:
            print("Draw line error", e)

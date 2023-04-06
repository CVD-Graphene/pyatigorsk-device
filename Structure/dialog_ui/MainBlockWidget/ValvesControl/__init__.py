from grapheneqtui.structures import BaseValvesControlBlock
from .PumpsControlWidget import PumpsControlWidget


class ValvesControlBlock(BaseValvesControlBlock):

    def set_control_valves(self):
        self.control_valve = PumpsControlWidget()
        self.layout.addWidget(self.control_valve)

from coregraphene.conf import settings
from grapheneqtui.structures import TermodatsManageBlock, BaseMainBlockWidget

from .ValvesControl import ValvesControlBlock


class MainBlockWidget(BaseMainBlockWidget):

    def set_layout_content(self):
        self.pressure_block = ValvesControlBlock(
            gases_configuration=settings.VALVES_CONFIGURATION,
            default_sccm_value=settings.MAX_DEFAULT_SCCM_VALUE,
        )
        self.layout.addWidget(self.pressure_block)

        self.temperature_block = TermodatsManageBlock(
            configuration=settings.TERMODAT_CONFIGURATION,
            max_speed=settings.TERMODAT_MAX_SPEED,
            default_speed=settings.TERMODAT_DEFAULT_SPEED,
        )
        self.layout.addWidget(self.temperature_block)

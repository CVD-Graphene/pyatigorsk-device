from Core.actions import ACTIONS
from coregraphene.conf import settings
from coregraphene.constants import RECIPE_STATES, NOTIFICATIONS, RECIPE_STATES_TO_STR
from grapheneqtui.structures import BaseMainDialogWindow

from .MainBlockWidget import MainBlockWidget


class AppMainDialogWindow(BaseMainDialogWindow):
    main_interface_widget_class = MainBlockWidget

    actions_list = ACTIONS
    recipe_states = RECIPE_STATES
    recipe_states_to_str = RECIPE_STATES_TO_STR
    recipe_table_column_names = settings.TABLE_COLUMN_NAMES
    notifications_configuration = NOTIFICATIONS

    def connect_controllers_actions(self):
        # ======================= CONNECT FUNCTIONS ========================= #
        # GASES #################
        for gas in self.milw.pressure_block.gases:
            num = gas.number

            gas.connect_valve_function(self.system.change_valve_state)
            self.system.change_gas_valve_opened.connect(gas.draw_is_open, device_num=num)

            gas.connect_change_sccm_function(self.system.set_target_rrg_sccm_action)
            self.system.set_target_rrg_sccm_action.connect(gas.draw_set_target_sccm, device_num=gas.number)
            self.system.full_open_rrg_action.connect(gas.draw_set_target_sccm, device_num=gas.number)
            self.system.full_close_rrg_action.connect(gas.draw_set_target_sccm, device_num=gas.number)

            self.system.get_current_rrg_sccm.connect(gas.update_current_sccm_label, device_num=gas.number)

        # AIR #################
        self.milw.pressure_block.air. \
            connect_valve_function(self.system.change_air_valve_state)
        self.system.change_air_valve_opened.connect(self.milw.pressure_block.air.draw_is_open)
        #######################

        # PUMPS ###############
        self.milw.pressure_block.control_valve. \
            connect_big_pump_valve_function(self.system.change_pump_valve_state)
        self.milw.pressure_block.control_valve. \
            connect_small_pump_valve_function(self.system.change_pump_valve_state)

        self.system.change_pump_valve_opened.connect(
            self.milw.pressure_block.control_valve.draw_big_pump_is_open,
            device_num=self.milw.pressure_block.control_valve.big_pump_num,
        )
        self.system.change_pump_valve_opened.connect(
            self.milw.pressure_block.control_valve.draw_small_pump_is_open,
            device_num=self.milw.pressure_block.control_valve.small_pump_num,
        )
        #######################

        # TERMODATS ###########
        self.system.turn_on_all_termodats_action.connect(
            self.milw.temperature_block.draw_is_active_termodats_regulation
        )
        self.system.turn_off_all_termodats_action.connect(
            self.milw.temperature_block.draw_is_active_termodats_regulation
        )
        self.system.set_temperature_and_speed_all_termodats_action.connect(
            self.milw.temperature_block.draw_temperature_and_speed_termodats
        )
        self.system.set_temperature_all_termodats_action.connect(
            self.milw.temperature_block.draw_temperature_termodats
        )

        self.milw.temperature_block.system_set_temperature = self.system.set_target_temperature
        self.milw.temperature_block.system_set_speed = self.system.set_termodat_speed
        self.milw.temperature_block.system_set_active_regulation = \
            self.system.set_termodat_is_active
        ######################

    def _update_ui_values(self):
        self.milw.temperature_block.show_pressure_block.set_value(
            self.system.accurate_vakumetr_value
        )

        # for i, gas in enumerate(self.milw.pressure_block.gases):
        #     gas.update_current_sccm_label(self.system.current_sccms[i])

        for num, temperature in self.system.current_temperatures.items():
            self.milw.temperature_block.temps[num].set_current_temperature(
                temperature
            )

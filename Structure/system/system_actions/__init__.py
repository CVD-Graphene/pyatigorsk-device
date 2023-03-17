import random

from coregraphene.conf import settings
from coregraphene.system_actions import (
    ManyDeviceSystemAction, ManyDeviceControllerAction,
    SystemAction,
)

LOCAL_MODE = settings.LOCAL_MODE


class SetTargetRrgSccmAction(ManyDeviceSystemAction):
    def _call_function(self, sccm, device_num):
        return self._system.rrgs_controller.set_target_sccm(sccm, device_num)


class FullCloseRrgAction(ManyDeviceSystemAction):
    def _call_function(self, device_num):
        return self._system.rrgs_controller.full_close(device_num)


class FullOpenRrgAction(ManyDeviceSystemAction):
    def _call_function(self, device_num):
        return self._system.rrgs_controller.full_open(device_num)


class ChangeAirValveStateAction(SystemAction):
    def _call_function(self, is_open):
        return self._system.air_valve_controller.set_is_open_state(is_open)


class ChangePumpValveStateAction(ManyDeviceSystemAction):
    def _call_function(self, is_open, device_num=None):
        return self._system._pumps[device_num].set_is_open_state(is_open)


class ChangeGasValveStateAction(ManyDeviceSystemAction):
    def _call_function(self, is_open, device_num=None):
        # print("Valve call...", is_open, device_num)
        ans = self._system._valves[device_num].set_is_open_state(is_open)
        # print("Valve call 2...", is_open, device_num, ans)
        return ans

    # def _filter_callback_array(self, *args, device_num=None, **kwargs):
    #     arr = super()._filter_callback_array(*args, device_num=device_num, **kwargs)
    #     # print("Valve state arr...", arr, 'dev', device_num)
    #     return arr


class SingleAnswerSystemAction(ManyDeviceSystemAction):
    def _call_function(self, value, device_num=None):
        # print("CALL FUNC CURRENT FLOW:", value, device_num)
        return value


class TurnOnAllTermodatsRegulationAction(SystemAction):
    def _call_function(self):
        return self._system.termodats_controller.turn_on_all_termodats_regulation()


class TurnOffAllTermodatsRegulationAction(SystemAction):
    def _call_function(self):
        return self._system.termodats_controller.turn_off_all_termodats_regulation()


class SetTemperatureAndSpeedAllTermodatsAction(SystemAction):
    def _call_function(self, temperature, speed):
        return self._system.termodats_controller.set_temperature_and_speed_all_termodats(
            temperature, speed
        )


class SetTemperatureAllTermodatsAction(SystemAction):
    def _call_function(self, temperature):
        return self._system.termodats_controller.set_temperature_all_termodats(temperature)


# =========== CONTROLLER ACTIONS ================= #


class GetCurrentFlowRrgControllerAction(ManyDeviceControllerAction):

    def _on_get_value(self, value):
        # print("CALL FUNC CURRENT FLOW CONTROLLER 2:", value)
        self._controller.current_sccms[self._controller._last_thread_command.device_num] = value

    def _call_function(self, value):
        if LOCAL_MODE:
            value = random.random() * 100 * 100
        value = float(value) / 100 * 2.0
        # print("CALL FUNC CURRENT FLOW CONTROLLER:", value)
        return value

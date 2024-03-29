from coregraphene.conf import settings
from coregraphene.system_effects import (
    ManyDeviceSystemEffect, ManyDeviceControllerEffect,
    SystemEffect,
)

LOCAL_MODE = settings.LOCAL_MODE


class SetTargetRrgSccmAction(ManyDeviceSystemEffect):
    def _call_function(self, sccm, device_num):
        return self._system.rrgs_controller.set_target_sccm(sccm, device_num)


class FullCloseRrgAction(ManyDeviceSystemEffect):
    def _call_function(self, device_num):
        return self._system.rrgs_controller.full_close(device_num)


class FullOpenRrgAction(ManyDeviceSystemEffect):
    def _call_function(self, device_num):
        return self._system.rrgs_controller.full_open(device_num)


class ChangeAirValveStateAction(SystemEffect):
    def _call_function(self, is_open):
        return self._system.air_valve_controller.set_is_open_state(is_open)


class ChangePumpValveStateAction(ManyDeviceSystemEffect):
    def _call_function(self, is_open, device_num=None):
        return self._system._pumps[device_num].set_is_open_state(is_open)


class ChangeGasValveStateAction(ManyDeviceSystemEffect):
    def _call_function(self, is_open, device_num=None):
        # print("Valve call...", is_open, device_num)
        ans = self._system._valves[device_num].set_is_open_state(is_open)
        # print("Valve call 2...", is_open, device_num, ans)
        return ans

    # def _filter_callback_array(self, *args, device_num=None, **kwargs):
    #     arr = super()._filter_callback_array(*args, device_num=device_num, **kwargs)
    #     # print("Valve state arr...", arr, 'dev', device_num)
    #     return arr


class TurnOnAllTermodatsRegulationAction(SystemEffect):
    def _call_function(self):
        return self._system.termodats_controller.turn_on_all_termodats_regulation()


class TurnOffAllTermodatsRegulationAction(SystemEffect):
    def _call_function(self):
        return self._system.termodats_controller.turn_off_all_termodats_regulation()


class SetTemperatureAndSpeedAllTermodatsAction(SystemEffect):
    def _call_function(self, temperature, speed):
        return self._system.termodats_controller.set_temperature_and_speed_all_termodats(
            temperature  # , speed
        )


class SetTemperatureAllTermodatsAction(SystemEffect):
    def _call_function(self, temperature):
        return self._system.termodats_controller.set_temperature_all_termodats(temperature)


# =========== CONTROLLER ACTIONS ================= #


# class GetCurrentFlowRrgControllerAction(ManyDeviceControllerEffect):
#
#     def _on_get_value(self, value):
#         # print("CALL FUNC CURRENT FLOW CONTROLLER 2:", value)
#         self._controller.current_sccms[self._controller._last_thread_command.device_num] = value
#
#     def _call_function(self, value):
#         max_sccm = self._controller.get_max_sccm_device(
#             device_num=self._controller._last_thread_command.device_num)
#         if LOCAL_MODE:
#             value = random.random() * 100 * 100
#         value = float(value) / (100 * 100) * max_sccm
#         # print("CALL FUNC CURRENT FLOW CONTROLLER:", value)
#         return value

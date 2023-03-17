import gc

from Core.recipe_runner import AppRecipeRunner
from Structure.system.system_actions import (
    SetTargetRrgSccmAction,
    FullCloseRrgAction,
    FullOpenRrgAction,
    SingleAnswerSystemAction, ChangeGasValveStateAction, ChangeAirValveStateAction, ChangePumpValveStateAction,
    TurnOnAllTermodatsRegulationAction, TurnOffAllTermodatsRegulationAction, SetTemperatureAndSpeedAllTermodatsAction,
    SetTemperatureAllTermodatsAction,
)
from coregraphene.components.controllers import (
    AbstractController,
    AccurateVakumetrController,
    ValveController,
    RrgModbusController,
    TermodatModbusController,
    SeveralTermodatModbusController,
    SeveralRrgModbusController,
)
from coregraphene.system import BaseSystem
from coregraphene.conf import settings
from coregraphene.utils import get_available_usb_ports

VALVES_CONFIGURATION = settings.VALVES_CONFIGURATION
PUMPS_CONFIGURATION = settings.PUMPS_CONFIGURATION
TERMODAT_CONFIGURATION = settings.TERMODAT_CONFIGURATION
LOCAL_MODE = settings.LOCAL_MODE


class CvdSystem(BaseSystem):

    recipe_class = AppRecipeRunner

    def _determine_attributes(self):
        used_ports = []
        self.vakumetr_port = None
        self.rrg_port = None
        self.termodat_port = None
        attributes = [
            ['rrg_port', RrgModbusController],
            ['termodat_port', TermodatModbusController],
            ['vakumetr_port', AccurateVakumetrController],
        ]
        usb_ports = get_available_usb_ports()
        if LOCAL_MODE:
            usb_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
        print("PORTS USB:", usb_ports)
        for port_name, controller_class in attributes:
            for port in usb_ports:  # ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']:
                if port in used_ports:
                    continue
                controller: AbstractController = controller_class(port=port)
                controller.setup()
                is_good = controller.check_command()
                if is_good:
                    setattr(self, port_name, port)
                    used_ports.append(port)
                    break

                controller.destructor()
                del controller

        print("|> FOUND PORTS:", self.vakumetr_port, self.rrg_port, self.termodat_port)
        assert self.vakumetr_port is not None
        assert self.rrg_port is not None
        assert self.termodat_port is not None

        gc.collect()

    def _init_controllers(self):
        self.accurate_vakumetr_controller = AccurateVakumetrController(
            port=self.vakumetr_port,
        )

        self.air_valve_controller = ValveController(
            port=settings.AIR_VALVE_CONFIGURATION['PORT'],
        )

        self._valves = dict()
        self._pumps = dict()
        # self._rrgs = dict()
        for i, valve_conf in enumerate(VALVES_CONFIGURATION):
            # valve_conf["NAME"]
            self._valves[i] = ValveController(port=valve_conf["PORT"])

        for i, pump_conf in enumerate(PUMPS_CONFIGURATION):
            self._pumps[i] = ValveController(port=pump_conf["PORT"])

        self.rrgs_controller = SeveralRrgModbusController(
            config=VALVES_CONFIGURATION,
            port=self.rrg_port,
        )

        self.termodats_controller = SeveralTermodatModbusController(
            config=TERMODAT_CONFIGURATION,
            port=self.termodat_port,
        )

        self._controllers: list[AbstractController] = [
            self.accurate_vakumetr_controller,
            self.rrgs_controller,
            self.termodats_controller,
            self.air_valve_controller,
        ]

        for valve in self._valves.values():
            self._controllers.append(valve)
        for pump in self._pumps.values():
            self._controllers.append(pump)

    def _init_values(self):
        self.accurate_vakumetr_value = 0.0
        self.current_sccms = {
            i: 0.0 for i in range(len(VALVES_CONFIGURATION))
        }
        self.target_sccms = {
            i: 0.0 for i in range(len(VALVES_CONFIGURATION))
        }
        self.current_temperatures = {
            i: 0.0 for i in range(len(TERMODAT_CONFIGURATION))
        }

    def _init_actions(self):
        super()._init_actions()

        # ===== RRGs ======= #
        self.set_target_rrg_sccm_action = SetTargetRrgSccmAction(system=self)
        self.full_close_rrg_action = FullCloseRrgAction(system=self)
        self.full_open_rrg_action = FullOpenRrgAction(system=self)

        self.get_current_rrg_sccm = SingleAnswerSystemAction(system=self)
        self.rrgs_controller.get_current_flow.connect(self.get_current_rrg_sccm)

        # ===== Valves ===== #
        self.change_gas_valve_opened = ChangeGasValveStateAction(system=self)
        self.change_air_valve_opened = ChangeAirValveStateAction(system=self)
        self.change_pump_valve_opened = ChangePumpValveStateAction(system=self)

        # ===== Termodats == #
        self.turn_on_all_termodats_action = TurnOnAllTermodatsRegulationAction(system=self)
        self.turn_off_all_termodats_action = TurnOffAllTermodatsRegulationAction(system=self)
        self.set_temperature_and_speed_all_termodats_action = \
            SetTemperatureAndSpeedAllTermodatsAction(system=self)
        self.set_temperature_all_termodats_action = SetTemperatureAllTermodatsAction(system=self)

    def check_conditions(self):
        return True

    def log_state(self):
        pass
        # for controller in self._controllers:
        #     value = controller.get_value()

    def _change_valve_state(self, valve, name):
        new_state = valve.change_state()
        # print(f"Valve {name} new state: {new_state}")
        return new_state

    @BaseSystem.action
    def change_valve_state(self, gas_num):
        valve = self._valves.get(gas_num, None)
        if valve is None:
            return False
        return self._change_valve_state(valve, gas_num)

    @BaseSystem.action
    def change_air_valve_state(self):
        return self._change_valve_state(self.air_valve_controller, "AIR")

    @BaseSystem.action
    def change_pump_valve_state(self, pump_num):
        pump = self._pumps.get(pump_num, None)
        if pump is None:
            return False
        return self._change_valve_state(pump, f"Pump {pump}")

    # @BaseSystem.action
    # def set_rrg_target_sccm(self, sccm, device_num):
    #     new_sccm = self.rrgs_controller.set_target_sccm(sccm, device_num)
    #     return new_sccm

    # =================== TERMODAT ====================== #

    @BaseSystem.action
    def set_target_temperature_to_all_termodat(self, temperature):
        new_temperature = temperature

        for device_num in range(self.termodats_controller.devices_amount):
            new_temperature = self.termodats_controller.set_target_temperature(
                temperature, device_num)

        return new_temperature

    @BaseSystem.action
    def set_target_temperature(self, temperature, device_num):
        new_temperature = self.termodats_controller.set_target_temperature(
            temperature, device_num)
        return new_temperature

    @BaseSystem.action
    def set_termodat_speed(self, speed, device_num):
        new_speed = self.termodats_controller.set_speed_regulation(
            speed, device_num)
        return new_speed

    @BaseSystem.action
    def set_termodat_is_active(self, is_active, device_num):
        new_is_active = self.termodats_controller.set_is_active_regulation(
            is_active, device_num)
        return new_is_active

    @BaseSystem.action
    def get_max_current_termodat_temperature(self):
        return max(list(self.current_temperatures.values()))

    @BaseSystem.action
    def get_mim_current_termodat_temperature(self):
        return min(list(self.current_temperatures.values()))

    def get_current_vakumetr_pressure(self):
        return self.accurate_vakumetr_value

    def _get_values(self):
        self.accurate_vakumetr_value = self.accurate_vakumetr_controller.vakumetr_value
        # for key in self.current_sccms.keys():
        #     self.current_sccms[key] = self.rrgs_controller.get_current_sccm(key)

        for key in self.current_temperatures.keys():
            self.current_temperatures[key] = \
                self.termodats_controller.current_temperatures[key]
        # print("VOLT VAL:", self.voltage_value)

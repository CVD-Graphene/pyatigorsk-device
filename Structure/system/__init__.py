import gc

from Core.recipe_runner import AppRecipeRunner
from Structure.system.system_actions import (
    SetTargetRrgSccmAction,
    FullCloseRrgAction,
    FullOpenRrgAction,
    ChangeGasValveStateAction,
    ChangeAirValveStateAction,
    ChangePumpValveStateAction,
    TurnOnAllTermodatsRegulationAction,
    TurnOffAllTermodatsRegulationAction,
    SetTemperatureAndSpeedAllTermodatsAction,
    SetTemperatureAllTermodatsAction,
)
from coregraphene.components.controllers import (
    AbstractController,
    AccurateVakumetrController,
    ValveController,
    RrgModbusController,
    TermodatModbusController,
    SeveralTermodatModbusController,
    SeveralRrgModbusController, DigitalFuseController, VakumetrAdcController,
)
from coregraphene.system import BaseSystem
from coregraphene.conf import settings
from coregraphene.system_effects import SingleAnswerSystemEffect
from coregraphene.utils import get_available_ttyusb_ports, get_available_ttyusb_port_by_usb

VALVES_CONFIGURATION = settings.VALVES_CONFIGURATION
PUMPS_CONFIGURATION = settings.PUMPS_CONFIGURATION
TERMODAT_CONFIGURATION = settings.TERMODAT_CONFIGURATION
LOCAL_MODE = settings.LOCAL_MODE


class AppSystem(BaseSystem):
    recipe_class = AppRecipeRunner

    _default_controllers_kwargs = {
        'vakumetr': {
            'port_communicator': settings.ACCURATE_VAKUMETR_COMMUNICATOR_PORT,
            # 'baudrate': settings.ACCURATE_VAKUMETR_BAUDRATE,
        },
    }

    _usb_devices_ports = {
        'vakumetr': settings.ACCURATE_VAKUMETR_USB_PORT,
        'rrg': settings.RRG_USB_PORT,
        'termodat': settings.TERMODAT_USB_PORT,
    }

    def _determine_attributes(self):
        used_ports = []
        self.vakumetr_port = None
        self.rrg_port = None
        self.termodat_port = None
        self._ports_attr_names = {
            'vakumetr': 'vakumetr_port',
            'rrg': 'rrg_port',
            'termodat': 'termodat_port',
        }
        self._controllers_check_classes = {
            'rrg': RrgModbusController,
            'termodat': TermodatModbusController,
            'vakumetr': AccurateVakumetrController,
        }
        # attributes = [
        #     ['rrg_port', RrgModbusController],
        #     ['termodat_port', TermodatModbusController],
        #     ['vakumetr_port', AccurateVakumetrController],
        # ]
        for controller_code, port_name_attr in self._ports_attr_names.items():
            if LOCAL_MODE:
                ttyusb_port = '/dev/ttyUSB0'
            else:
                ttyusb_port = get_available_ttyusb_port_by_usb(
                    self._usb_devices_ports.get(controller_code, '')
                )
            setattr(self, self._ports_attr_names[controller_code], ttyusb_port)

        # usb_ports = get_available_ttyusb_ports()
        # if LOCAL_MODE:
        #     usb_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
        # print("PORTS USB:", usb_ports)
        # for controller_code, controller_class in self._controllers_check_classes.items():
        #     for port in usb_ports:  # ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']:
        #         if port in used_ports:
        #             continue
        #         controller: AbstractController = controller_class(
        #             port=port,
        #             **self._default_controllers_kwargs.get(controller_code, {})
        #         )
        #         controller.setup()
        #         is_good = controller.check_command()
        #         if is_good:
        #             setattr(self, self._ports_attr_names[controller_code], port)
        #             used_ports.append(port)
        #             break
        #
        #         controller.destructor()
        #         del controller

        print(
            "|> FOUND PORTS:",
            "vakumetr:", self.vakumetr_port,
            "rrg:", self.rrg_port,
            "termodat:", self.termodat_port
        )
        assert self.vakumetr_port is not None
        assert self.rrg_port is not None
        assert self.termodat_port is not None

        self.ports = {
            'vakumetr': self.vakumetr_port,
            'rrg': self.rrg_port,
            'termodat': self.termodat_port,
        }

        gc.collect()

    def _init_controllers(self):
        self.accurate_vakumetr_controller = AccurateVakumetrController(
            get_potential_port=self.get_potential_controller_port_1,
            # port_communicator=settings.ACCURATE_VAKUMETR_COMMUNICATOR_PORT,
            **self._default_controllers_kwargs.get('vakumetr'),
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
            get_potential_port=self.get_potential_controller_port_1,
            port=self.rrg_port,
        )

        self.termodats_controller = SeveralTermodatModbusController(
            config=TERMODAT_CONFIGURATION,
            get_potential_port=self.get_potential_controller_port_1,
            port=self.termodat_port,
        )

        self.gases_pressure_controller = VakumetrAdcController(
            config=VALVES_CONFIGURATION,
            channel=settings.VAKUMETR_SPI_READ_CHANNEL,
            speed=settings.VAKUMETR_SPI_SPEED,
            device=settings.VAKUMETR_SPI_READ_DEVICE,
        )

        self._digital_fuses = {}
        for i, port in enumerate(settings.DIGITAL_FUSE_PORTS):
            self._digital_fuses[i] = DigitalFuseController(port=port)

        self._controllers: list[AbstractController] = [
            self.accurate_vakumetr_controller,
            self.gases_pressure_controller,
            self.rrgs_controller,
            self.termodats_controller,
            self.air_valve_controller,
        ]

        for valve in self._valves.values():
            self._controllers.append(valve)
        for pump in self._pumps.values():
            self._controllers.append(pump)

        for fuse in self._digital_fuses.values():
            self._controllers.append(fuse)

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

        self.get_current_rrg_sccm = SingleAnswerSystemEffect(system=self)
        self.rrgs_controller.get_current_flow.connect(self.get_current_rrg_sccm)

        # ===== Valves ===== #
        self.change_gas_valve_opened = ChangeGasValveStateAction(system=self)
        self.change_air_valve_opened = ChangeAirValveStateAction(system=self)
        self.change_pump_valve_opened = ChangePumpValveStateAction(system=self)

        # ===== Vakumetr gases ==== #
        self.current_gas_balloon_pressure_effect = SingleAnswerSystemEffect(system=self)
        self.gases_pressure_controller.get_current_pressure_action.connect(
            self.current_gas_balloon_pressure_effect)

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
        new_state = self._change_valve_state(valve, gas_num)
        self.change_gas_valve_opened(new_state, device_num=gas_num)

    @BaseSystem.action
    def change_air_valve_state(self):
        new_state = self._change_valve_state(self.air_valve_controller, "AIR")
        self.change_air_valve_opened(new_state)

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
    def get_min_current_termodat_temperature(self):
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

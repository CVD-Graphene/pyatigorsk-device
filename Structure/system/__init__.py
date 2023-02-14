from coregraphene.components.controllers import (
    AbstractController,
    AccurateVakumetrController,
    ValveController,
    CurrentSourceController,
    RrgModbusController,
    TermodatModbusController,
)
from coregraphene.system import BaseSystem
from coregraphene.conf import settings

VALVES_CONFIGURATION = settings.VALVES_CONFIGURATION


class CvdSystem(BaseSystem):

    def _determine_attributes(self):
        used_ports = []
        self.vakumetr_port = None
        self.rrg_port = None
        self.termodat_port = None
        attributes = [
            ['vakumetr_port', AccurateVakumetrController],
            ['rrg_port', RrgModbusController],
            ['termodat_port', TermodatModbusController],
        ]
        for port_name, controller_class in attributes:
            for port in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']:
                if port in used_ports:
                    continue
                controller: AbstractController = controller_class(port=port)
                controller.setup()
                is_good = controller.check_command()
                if is_good:
                    setattr(self, port_name, port)
                    used_ports.append(port)
                    break

        assert self.vakumetr_port is not None
        assert self.rrg_port is not None
        assert self.termodat_port is not None

    def _init_controllers(self):
        self.accurate_vakumetr_controller = AccurateVakumetrController(
            port=self.vakumetr_port,
        )
        self._valves = dict()
        self._rrgs = dict()
        for valve_conf in VALVES_CONFIGURATION:
            self._valves[valve_conf["NAME"]] = ValveController(port=valve_conf["PORT"])
            self._rrgs[valve_conf["NAME"]] = RrgModbusController(
                port=self.rrg_port,
                instrument_number=valve_conf['INSTRUMENT_NUMBER'],
            )

        self.current_source_controller = CurrentSourceController(
            on_change_current=self.on_change_current,
            on_change_voltage=self.on_change_voltage,
            on_set_current=None,  # ДОБАВИТЬ РЕАЛЬНОЕ ВЛИЯНИЕ - ПРОСТОЕ ВЫСТАВЛЕНИЕ АКТУАЛЬНОГО ЗНАЧЕНИЯ В UI
        )

        self._controllers: list[AbstractController] = [
            self.accurate_vakumetr_controller,
            self.current_source_controller,
        ]

        for valve in self._valves.values():
            self._controllers.append(valve)

    def _init_values(self):
        self.accurate_vakumetr_value = 0.0
        self.current_value = 0.0
        self.voltage_value = 0.0

    def check_conditions(self):
        return True

    def log_state(self):
        pass
        # for controller in self._controllers:
        #     value = controller.get_value()

    @BaseSystem.action
    def change_valve_state(self, gas):
        # t = Thread(target=self.long_function)
        # t.start()
        # return 1
        valve = self._valves.get(gas, None)
        if valve is None:
            return False
        return valve.change_state()

    def on_change_current(self, value):
        self.current_value = value

    def on_change_voltage(self, value):
        self.voltage_value = value

    @BaseSystem.action
    def set_current(self, value):
        return self.current_source_controller.set_current_value(value)

    def _get_values(self):
        # pass
        self.accurate_vakumetr_value = self.accurate_vakumetr_controller.get_value()
        # self.current_value = self.current_source_controller.get_current_value()
        # self.voltage_value = self.current_source_controller.get_voltage_value()
        # print("VOLT VAL:", self.voltage_value)

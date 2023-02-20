from coregraphene.utils import get_serial_port


SERIAL_PORT = get_serial_port()

ACCURATE_VAKUMETR_PORT = 1
ACCURATE_VAKUMETR_USB_PORT = '/dev/ttyUSB0'  # FOR CVD-GRAPHENE USE USB1 (?)
CURRENT_SOURCE_PORT = 3

VALVES_CONFIGURATION_1 = [
    {'PORT': 2, "NAME": "O_2", "IS_GAS": True, "INSTRUMENT_NUMBER": 1},
    {'PORT': 3, "NAME": "N_2", "IS_GAS": True},
    {'PORT': 4, "NAME": "Ar", "IS_GAS": True},
    {'PORT': 17, "NAME": "C_2", "IS_GAS": True},
    {'PORT': 6, "NAME": "F_2", "IS_GAS": True},
    # {'PORT': 12, "NAME": "PUMP", "IS_GAS": False},
    # {'PORT': 13, "NAME": "AIR", "IS_GAS": False},
]

AIR_VALVE_CONFIGURATION = {
    'PORT': 4,
}

VALVES_CONFIGURATION = [
    {'PORT': 2, "NAME": "H_2", "IS_GAS": True, "INSTRUMENT_NUMBER": 2},
    {'PORT': 3, "NAME": "Ar", "IS_GAS": True, "INSTRUMENT_NUMBER": 1},
    {'PORT': 17, "NAME": "CH_4", "IS_GAS": True, "INSTRUMENT_NUMBER": 3},
]

TERMODAT_CONFIGURATION = [
    {'INSTRUMENT_NUMBER': 1, 'LABEL': '-'},
    {'INSTRUMENT_NUMBER': 2, 'LABEL': '-'},
    {'INSTRUMENT_NUMBER': 3, 'LABEL': '-'},
]

# Used in modbus communication method
DEFAULT_MODBUS_BAUDRATE = 19200
DEFAULT_MODBUS_TIMEOUT = 0.2
DEFAULT_MODBUS_INSTRUMENT_NUMBER = 1

VALVE_LIST = list(map(lambda x: x.get('NAME'), VALVES_CONFIGURATION))
GAS_LIST = list(map(lambda x: x.get('NAME'), filter(lambda x: x.get("IS_GAS", False), VALVES_CONFIGURATION)))


TABLE_COLUMN_NAMES = ["Процесс", "Аргумент 1", "Аргумент 2", "Аргумент 3", "Комментарий"]

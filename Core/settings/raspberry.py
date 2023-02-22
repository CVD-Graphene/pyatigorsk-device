from coregraphene.utils import get_serial_port


SERIAL_PORT = get_serial_port()

ACCURATE_VAKUMETR_PORT = 1
ACCURATE_VAKUMETR_USB_PORT = '/dev/ttyUSB0'  # FOR CVD-GRAPHENE USE USB1 (?)
CURRENT_SOURCE_PORT = 3

AIR_VALVE_CONFIGURATION = {
    'PORT': 4,
}

VALVES_CONFIGURATION = [
    {'PORT': 2, "NAME": "H_2", "INSTRUMENT_NUMBER": 2},
    {'PORT': 17, "NAME": "Ar", "INSTRUMENT_NUMBER": 1},
    {'PORT': 3, "NAME": "CH_4", "INSTRUMENT_NUMBER": 3},
]

TERMODAT_CONFIGURATION = [
    {'INSTRUMENT_NUMBER': 1, 'LABEL': '-'},
    {'INSTRUMENT_NUMBER': 2, 'LABEL': '-'},
    {'INSTRUMENT_NUMBER': 3, 'LABEL': '-'},
]

TERMODAT_DEFAULT_SPEED = 500
TERMODAT_MAX_SPEED = 65001

# Used in modbus communication method
DEFAULT_MODBUS_BAUDRATE = 19200
DEFAULT_MODBUS_TIMEOUT = 0.2
DEFAULT_MODBUS_INSTRUMENT_NUMBER = 1

VALVE_LIST = list(map(lambda x: x.get('NAME'), VALVES_CONFIGURATION))
GAS_LIST = list(map(lambda x: x.get('NAME'), filter(lambda x: x.get("IS_GAS", False), VALVES_CONFIGURATION)))


TABLE_COLUMN_NAMES = ["Процесс", "Аргумент 1", "Аргумент 2", "Аргумент 3", "Комментарий"]

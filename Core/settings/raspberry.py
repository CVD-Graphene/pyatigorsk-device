MAX_RECIPE_STEP_SECONDS = 60 * 60 * 24 * 2  # set to None for remove limit for step time

ACCURATE_VAKUMETR_COMMUNICATOR_PORT = 1
ACCURATE_VAKUMETR_USB_PORT = '/dev/ttyUSB1'  # FOR CVD-GRAPHENE USE USB1 (?)
CURRENT_SOURCE_PORT = 3

VAKUMETR_SPI_READ_CHANNEL = 0
VAKUMETR_SPI_SPEED = 20000
VAKUMETR_SPI_READ_DEVICE = 0

DIGITAL_FUSE_PORTS = [6]

AIR_VALVE_CONFIGURATION = {
    'PORT': 4, "NAME": "Air",
}
AIR_VALVE_NAME = AIR_VALVE_CONFIGURATION['NAME']

VALVES_CONFIGURATION = [
    {
        'PORT': 2,  # gpio port for rele
        "NAME": "H_2",
        "IS_GAS": True,
        "MAX_SCCM": 606.0,  # max sccm for rrg, if not provided == `MAX_DEFAULT_SCCM_VALUE`
        "INSTRUMENT_NUMBER": 2,  # rrg modbus instrument number
        'VAKUMETR_ADDRESS': 1,
    },
    {'PORT': 17, "NAME": "CH_4", "IS_GAS": True, "MAX_SCCM": 43.2,
     "INSTRUMENT_NUMBER": 1, 'VAKUMETR_ADDRESS': 2, },
    {'PORT': 3, "NAME": "Ar", "IS_GAS": True, "MAX_SCCM": 2175,
     "INSTRUMENT_NUMBER": 3, 'VAKUMETR_ADDRESS': 3, },
]

MAX_DEFAULT_SCCM_VALUE = 200

PUMPS_CONFIGURATION = [
    {'PORT': 5, "NAME": "BIG_PUMP", },  # Не менять название !!!!!
    {'PORT': 22, "NAME": "SMALL_PUMP", },  # Не менять название !!!!!
]
BIG_PUMP_INDEX = 0
SMALL_PUMP_INDEX = 1

ALL_GPIO_VALVES_CONFIG = VALVES_CONFIGURATION + PUMPS_CONFIGURATION + [AIR_VALVE_CONFIGURATION]

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

VALVE_LIST = list(map(lambda x: x.get('NAME'), ALL_GPIO_VALVES_CONFIG))
# GAS_LIST = list(map(lambda x: x.get('NAME'), filter(lambda x: x.get("IS_GAS", False), VALVES_CONFIGURATION)))
GAS_LIST = list(map(lambda x: x.get('NAME'), VALVES_CONFIGURATION))


TABLE_COLUMN_NAMES = ["Процесс", "Аргумент 1", "Аргумент 2", "Аргумент 3", "Комментарий"]

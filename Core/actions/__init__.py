import time

from coregraphene.auto_actions import AppAction, IntKeyArgument, Argument, PositiveIntKeyArgument, \
    TimeEditArgument, GasListArgument, SccmArgument, ValveListArgument, PositiveFloatKeyArgument
from coregraphene.conf import settings
from coregraphene.constants import RECIPE_STATES
from coregraphene.recipe.exceptions import NotAchievingRecipeStepGoal

ACTIONS_NAMES = settings.ACTIONS_NAMES
TABLE_ACTIONS_NAMES = settings.TABLE_ACTIONS_NAMES
MAX_RECIPE_STEP_SECONDS = settings.MAX_RECIPE_STEP_SECONDS


class TermodatIndexArgument(IntKeyArgument):
    def _check(self, value):
        value = int(value)
        range_list = [0, len(settings.TERMODAT_CONFIGURATION)]
        if not range_list[0] <= value < range_list[1]:
            raise Exception(f"Termodat index value {value} not in range {range_list}")


class TermodatSpeedArgument(IntKeyArgument):
    arg_default = settings.TERMODAT_DEFAULT_SPEED

    def _check(self, value):
        value = int(value)
        range_list = [0, settings.TERMODAT_MAX_SPEED]
        if not range_list[0] <= value < range_list[1]:
            raise Exception(f"Termodat speed value {value} not in range {range_list}")


# class SetTemperatureForTermodatDeviceAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.SET_TEMPERATURE_FOR_TERMODAT_DEVICE
#     key = ACTIONS_NAMES.SET_TEMPERATURE_FOR_TERMODAT_DEVICE
#     args_info = [PositiveIntKeyArgument, TermodatIndexArgument]


# class SetSpeedForTermodatDeviceAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.SET_SPEED_FOR_TERMODAT_DEVICE
#     key = ACTIONS_NAMES.SET_SPEED_FOR_TERMODAT_DEVICE
#     args_info = [TermodatSpeedArgument, TermodatIndexArgument]


def get_total_seconds_from_time_arg(time_arg):
    mins, secs = list(map(int, time_arg.strip().split(':')))
    return mins * 60 + secs


class PauseAction(AppAction):
    name = TABLE_ACTIONS_NAMES.PAUSE
    key = ACTIONS_NAMES.PAUSE
    args_info = [TimeEditArgument]

    def set_functions(self, get_current_recipe_state=None, **kwargs):
        self.get_current_recipe_state = get_current_recipe_state

    def action(self, sleep_time, *args, **kwargs):
        seconds = get_total_seconds_from_time_arg(sleep_time)
        # print("SLEEP SECONDS:", seconds, time.time())
        start = time.time()
        while time.time() - start < seconds:
            time.sleep(1)
            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                break


def get_gas_index_by_name(name):
    for i, gas in enumerate(settings.VALVES_CONFIGURATION):
        if gas['NAME'] == name:
            return i


def get_pump_index_by_name(name):
    for i, pump in enumerate(settings.PUMPS_CONFIGURATION):
        if pump['NAME'] == name:
            return i


class TurnOnAllTermodatsTableAction(AppAction):
    """
    Включить все печки (термодаты)
    """
    name = TABLE_ACTIONS_NAMES.TURN_ON_ALL_TERMODATS
    key = ACTIONS_NAMES.TURN_ON_ALL_TERMODATS
    args_info = []

    def action(self):
        self.system.turn_on_all_termodats_action()


class TurnOffAllTermodatsTableAction(AppAction):
    """
    Выключить все печки (термодаты)
    """
    name = TABLE_ACTIONS_NAMES.TURN_OFF_ALL_TERMODATS
    key = ACTIONS_NAMES.TURN_OFF_ALL_TERMODATS
    args_info = []

    def action(self):
        self.system.turn_off_all_termodats_action()


class SetTemperatureAndSpeedAllTermodatsTableAction(AppAction):
    """
    Установить температуру и скорость на все печки (термодаты)
    """
    name = TABLE_ACTIONS_NAMES.SET_T_V_ALL_TERMODATS
    key = ACTIONS_NAMES.SET_T_V_ALL_TERMODATS
    args_info = [PositiveFloatKeyArgument, TermodatSpeedArgument]

    def action(self, temperature, speed):
        self.system.set_temperature_and_speed_all_termodats_action(temperature, speed)


class FullOpenSingleRrgAction(AppAction):
    """
    Полностью открыть ррг
    """
    name = TABLE_ACTIONS_NAMES.FULL_OPEN_RRG
    key = ACTIONS_NAMES.FULL_OPEN_RRG
    args_info = [GasListArgument]

    def action(self, valve_name):
        index = get_gas_index_by_name(valve_name)
        self.system.full_open_rrg_action(device_num=index)


class FullCloseSingleRrgAction(AppAction):
    """
    Полностью закрыть ррг
    """
    name = TABLE_ACTIONS_NAMES.FULL_CLOSE_RRG
    key = ACTIONS_NAMES.FULL_CLOSE_RRG
    args_info = [GasListArgument]

    def action(self, valve_name):
        index = get_gas_index_by_name(valve_name)
        self.system.full_close_rrg_action(device_num=index)


class SetRrgSccmValueAction(AppAction):
    """
    Установить значение sccm для ррг
    """
    name = TABLE_ACTIONS_NAMES.SET_RRG_VALUE
    key = ACTIONS_NAMES.SET_RRG_VALUE
    args_info = [GasListArgument, SccmArgument]

    def action(self, valve_name, sccm):
        sccm = float(sccm)
        index = get_gas_index_by_name(valve_name)
        self.system.set_target_rrg_sccm_action(sccm, device_num=index)


class SetRrgSccmAndKeepToPressureDeltaAction(AppAction):
    """
    Установить значение sccm для ррг и держать его до достижения разницы в давлении
    """
    name = TABLE_ACTIONS_NAMES.SET_RRG_AND_KEEP_TO_PRESSURE
    key = ACTIONS_NAMES.SET_RRG_AND_KEEP_TO_PRESSURE
    args_info = [GasListArgument, SccmArgument, PositiveFloatKeyArgument]

    def action(self, valve_name, sccm, delta_pressure):
        sccm = float(sccm)
        delta_pressure = float(delta_pressure)

        index = get_gas_index_by_name(valve_name)
        self.system.set_target_rrg_sccm_action(sccm, device_num=index)

        start_time = time.time()
        start_pressure = self.system.get_current_vakumetr_pressure()
        while self.system.get_current_vakumetr_pressure() - start_pressure < delta_pressure:
            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                break  # TODO: Or return here?
            time.sleep(1)
            if MAX_RECIPE_STEP_SECONDS and (time.time() - start_time >= MAX_RECIPE_STEP_SECONDS):
                raise NotAchievingRecipeStepGoal

        action_close_rrg = FullCloseSingleRrgAction()
        action_close_rrg.set_functions(system=self.system,)
        action_close_rrg.action(valve_name)


class SetRrgSccmValueWithPauseAction(AppAction):
    name = TABLE_ACTIONS_NAMES.SET_RRG_VALUE_WITH_PAUSE
    key = ACTIONS_NAMES.SET_RRG_VALUE_WITH_PAUSE
    args_info = [GasListArgument, SccmArgument, TimeEditArgument]

    def action(self, valve_name, sccm, time_pause):

        action_rrg = SetRrgSccmValueAction()
        action_rrg.set_functions(
            system=self.system,
        )
        action_rrg.action(valve_name, sccm)

        action_pause = PauseAction()
        action_pause.set_functions(get_current_recipe_state=self.get_current_recipe_state)
        action_pause.action(time_pause)


class SmallPumpOutToPressureAction(AppAction):
    """
    Медленно откачать камеру до заданного давления
    """
    name = TABLE_ACTIONS_NAMES.SMALL_PUMP_OUT_CAMERA
    key = ACTIONS_NAMES.SMALL_PUMP_OUT_CAMERA
    args_info = [PositiveFloatKeyArgument, TimeEditArgument]

    def action(self, target_pressure):
        target_pressure = float(target_pressure)
        index = settings.SMALL_PUMP_INDEX
        self.system.change_pump_valve_opened(True, index)

        start_time = time.time()

        while self.system.get_current_vakumetr_pressure() >= target_pressure:
            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                break  # TODO: Or return here?
            time.sleep(1)
            if MAX_RECIPE_STEP_SECONDS and (time.time() - start_time >= MAX_RECIPE_STEP_SECONDS):
                self.system.add_error_log(f"Откачка не завершилась до достижения максимального времени")
                raise NotAchievingRecipeStepGoal

        self.system.change_pump_valve_opened(False, index)


class BigPumpOutToPressureAction(AppAction):
    """
    Откачать камеру до заданного давления большим насосом (неигольчатым)
    """
    name = TABLE_ACTIONS_NAMES.PUMP_OUT_CAMERA
    key = ACTIONS_NAMES.PUMP_OUT_CAMERA
    args_info = [PositiveFloatKeyArgument, TimeEditArgument]

    def action(self, target_pressure, max_time):
        target_pressure = float(target_pressure)
        max_seconds = get_total_seconds_from_time_arg(max_time)

        index = settings.BIG_PUMP_INDEX
        self.system.change_pump_valve_opened(True, index)

        start_time = time.time()

        while self.system.get_current_vakumetr_pressure() > target_pressure:
            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                break  # TODO: Or return here?
            time.sleep(1)
            delta_time = time.time() - start_time
            if MAX_RECIPE_STEP_SECONDS and (delta_time >= MAX_RECIPE_STEP_SECONDS):
                raise NotAchievingRecipeStepGoal

            if delta_time >= max_seconds:
                self.system.add_error_log(f"Откачка не завершилась до достижения максимального времени")
                raise NotAchievingRecipeStepGoal

        self.system.change_pump_valve_opened(False, index)


class OpenValveAction(AppAction):
    name = TABLE_ACTIONS_NAMES.OPEN_VALVE
    key = ACTIONS_NAMES.OPEN_VALVE
    args_info = [ValveListArgument]

    def action(self, valve_name):
        is_gas = valve_name in list(map(lambda x: x['NAME'], settings.VALVES_CONFIGURATION))
        is_air = valve_name == settings.AIR_VALVE_CONFIGURATION['NAME']
        if is_air:
            self.system.change_air_valve_opened(True)
        elif is_gas:
            index = get_gas_index_by_name(valve_name)
            self.system.change_gas_valve_opened(True, device_num=index)
        else:
            index = get_pump_index_by_name(valve_name)
            self.system.change_pump_valve_opened(True, device_num=index)


class CloseValveAction(AppAction):
    name = TABLE_ACTIONS_NAMES.CLOSE_VALVE
    key = ACTIONS_NAMES.CLOSE_VALVE
    args_info = [ValveListArgument]

    def action(self, valve_name):
        is_gas = valve_name in list(map(lambda x: x['NAME'], settings.VALVES_CONFIGURATION))
        is_air = valve_name == settings.AIR_VALVE_CONFIGURATION['NAME']
        if is_air:
            self.system.change_air_valve_opened(False)
        elif is_gas:
            index = get_gas_index_by_name(valve_name)
            self.system.change_gas_valve_opened(False, device_num=index)
        else:
            index = get_pump_index_by_name(valve_name)
            self.system.change_pump_valve_opened(False, device_num=index)


class CloseAllValvesAction(AppAction):
    name = TABLE_ACTIONS_NAMES.CLOSE_ALL_VALVES
    key = ACTIONS_NAMES.CLOSE_ALL_VALVES

    def action(self, *args, **kwargs):

        self.system.change_air_valve_opened(False)

        for i, _ in enumerate(settings.VALVES_CONFIGURATION):
            self.system.change_gas_valve_opened(False, device_num=i)

        for i, _ in enumerate(settings.PUMPS_CONFIGURATION):
            self.system.change_pump_valve_opened(False, device_num=i)


class VentilateCameraTableAction(AppAction):
    """
    Провентилировать вакуумную камеру

    1. закрывает все клапаны,
    2. печку на 20 градусов (+ default speed)
    3. вырубить регуляцию,
    4. ждёт пока темрература не будет ниже заданной
    5. открывает клапан воздуха
    6. пока давдение не перестанет меняться более чем на х процентов за у секунд
    7. закрывает клапан воздуха
    """
    name = TABLE_ACTIONS_NAMES.VENTILATE_CAMERA
    key = ACTIONS_NAMES.VENTILATE_CAMERA
    args_info = [PositiveIntKeyArgument, PositiveIntKeyArgument, PositiveFloatKeyArgument]

    def action(self, x, y, target_temperature):
        start_time = time.time()
        x = int(x)
        y = int(y)
        target_temperature = float(target_temperature)

        # 1 STEP
        close_all = CloseAllValvesAction()
        close_all.set_functions(system=self.system)
        close_all.action()

        # 2 STEP
        set_termodat_values = SetTemperatureAndSpeedAllTermodatsTableAction()
        set_termodat_values.set_functions(system=self.system)
        set_termodat_values.action(20, settings.TERMODAT_DEFAULT_SPEED)

        # 3 STEP
        termodat_turn_off = TurnOffAllTermodatsTableAction()
        termodat_turn_off.set_functions(system=self.system)
        termodat_turn_off.action()

        # 4 STEP
        while self.system.get_max_current_termodat_temperature() > target_temperature:
            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                return  # TODO: Or break here?

            time.sleep(1)
            delta_time = time.time() - start_time
            if MAX_RECIPE_STEP_SECONDS and (delta_time >= MAX_RECIPE_STEP_SECONDS):
                raise NotAchievingRecipeStepGoal

        # 5 STEP
        open_air_valve = OpenValveAction()
        open_air_valve.set_functions(system=self.system)
        open_air_valve.action(settings.AIR_VALVE_NAME)

        # 6 STEP
        last_pressure = self.system.get_current_vakumetr_pressure()
        while True:
            time.sleep(y)
            new_pressure = self.system.get_current_vakumetr_pressure()
            max_p = max(last_pressure, new_pressure)
            min_p = min(last_pressure, new_pressure)

            if (max_p / min_p - 1.0) * 100 <= x:
                break

            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                break  # TODO: Or return here?

            delta_time = time.time() - start_time
            if MAX_RECIPE_STEP_SECONDS and (delta_time >= MAX_RECIPE_STEP_SECONDS):
                raise NotAchievingRecipeStepGoal

        # 7 STEP
        close_air_valve = CloseValveAction()
        close_air_valve.set_functions(system=self.system)
        close_air_valve.action(settings.AIR_VALVE_NAME)


class WaitForTemperatureAllTermodatsAction(AppAction):
    """
    Ждать установления температуры

    этот шаг длится до тех пор, пока температура на всех трёх печках не будет выше заданной.

    при исчерпании лимита пишем уведомление
    что не удалось установить температуру и останавливаем всю прогу
    """
    name = TABLE_ACTIONS_NAMES.WAIT_TARGET_TEMPERATURE
    key = ACTIONS_NAMES.WAIT_TARGET_TEMPERATURE
    args_info = [PositiveIntKeyArgument, TimeEditArgument]

    def action(self, target_temperature, time_limit):
        start_time = time.time()

        target_temperature = int(target_temperature)
        max_seconds = get_total_seconds_from_time_arg(time_limit)

        # 1 STEP
        self.system.set_temperature_all_termodats_action(target_temperature)

        # 4 STEP
        while self.system.get_min_current_termodat_temperature() < target_temperature:
            if self.get_current_recipe_state() == RECIPE_STATES.STOP:
                return  # TODO: Or break here?

            time.sleep(1)
            delta_time = time.time() - start_time
            if MAX_RECIPE_STEP_SECONDS and (delta_time >= MAX_RECIPE_STEP_SECONDS):
                raise NotAchievingRecipeStepGoal

            if delta_time >= max_seconds:
                self.system.add_error_log(f"Достижение температуры не завершилось до достижения максимального времени")
                raise NotAchievingRecipeStepGoal


class QuickShutdownAllDeviceElementsAction(AppAction):
    """
    Быстрое выключение всех активных приборов установки

    1. уставка печки на 20 градусов,
    2. печка выкл,
    3. выкл все клапаны,
    4. все ррг на ноль
    """
    name = TABLE_ACTIONS_NAMES.QUICK_SHUTDOWN_DEVICE
    key = ACTIONS_NAMES.QUICK_SHUTDOWN_DEVICE
    args_info = []

    def action(self):
        # 1 STEP: уставка печки на 20 градусов
        set_termodat_values = SetTemperatureAndSpeedAllTermodatsTableAction()
        set_termodat_values.set_functions(system=self.system)
        set_termodat_values.action(20, settings.TERMODAT_DEFAULT_SPEED)

        # 2 STEP: выключить печку
        turn_off_termodats = TurnOffAllTermodatsTableAction()
        turn_off_termodats.set_functions(system=self.system)
        turn_off_termodats.action()

        # 3 STEP: закрыть все клапаны
        close_all_valves = CloseAllValvesAction()
        close_all_valves.set_functions(system=self.system)
        close_all_valves.action()

        # 4 STEP: полностью закрыть все ррг
        close_rrg = FullCloseSingleRrgAction()
        close_rrg.set_functions(system=self.system)
        for gas_name in settings.GAS_LIST:
            close_rrg.action(gas_name)


ACTIONS = [
    CloseAllValvesAction(),
    OpenValveAction(),
    CloseValveAction(),

    SetRrgSccmValueAction(),
    FullOpenSingleRrgAction(),
    FullCloseSingleRrgAction(),
    SetRrgSccmValueWithPauseAction(),
    SetRrgSccmAndKeepToPressureDeltaAction(),

    TurnOnAllTermodatsTableAction(),
    TurnOffAllTermodatsTableAction(),
    SetTemperatureAndSpeedAllTermodatsTableAction(),

    PauseAction(),

    SmallPumpOutToPressureAction(),
    BigPumpOutToPressureAction(),
]

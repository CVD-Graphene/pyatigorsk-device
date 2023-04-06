import datetime
import gc
import logging
import tracemalloc
from time import sleep

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import (
    QFrame, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
    QLineEdit, QWidget, QMainWindow, QGridLayout, QFileDialog,
)

from Structure.dialog_ui.MainBlockWidget import MainBlockWidget
from Structure.dialog_ui.RightButtonsWidget import RightButtonsWidget
from Structure.dialog_ui.TableWidget import AppTableWidget
from Structure.system import CvdSystem
from grapheneqtui.components import LogWidget

from coregraphene.constants import RECIPE_STATES, NOTIFICATIONS
from Core.actions import ACTIONS

RECIPE_STATES_TO_STR = {
    RECIPE_STATES.RUN: "Running",
    RECIPE_STATES.PAUSE: "Pause",
    RECIPE_STATES.STOP: "Stop",
}


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("CVD-Graphene")

        ##############################################################################
        # ======================= SYSTEM SETUP + RECIPES =========================== #

        self.system = CvdSystem(actions_list=ACTIONS)
        self.system.setup()
        self.system.threads_setup()

        self._recipe_history = []
        self._current_recipe_step = None
        self._recipe_state = RECIPE_STATES.STOP

        ##############################################################################

        self.main_window = QHBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setObjectName("main_widget")
        # self.main_widget.setStyleSheet("background-color: rgb(240, 220, 255);")
        self.main_widget.setStyleSheet(
            "QWidget#main_widget {background-color: rgb(240, 240, 240);}"
        )
        self.main_widget.setLayout(self.main_window)

        self.main_interface_layout_widget = MainBlockWidget()
        self.milw = self.main_interface_layout_widget
        self.main_window.addWidget(self.main_interface_layout_widget)

        self.right_buttons_layout_widget = RightButtonsWidget(
            on_close=self.close,
            on_create_recipe=self.on_create_recipe,
            on_open_recipe=self.on_open_recipe,
            on_stop_recipe=self.system.on_stop_recipe,
            on_pause_recipe=self.system.on_pause_recipe,
            on_get_recipe_state=self.system.get_recipe_state,
        )
        self.main_window.addWidget(self.right_buttons_layout_widget)

        # Устанавливаем центральный виджет Window.
        self.setCentralWidget(self.main_widget)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.get_values_and_log_state)
        self.timer.start(500)

        # TABLE WIDGET FOR RECIPE ###################################
        self.table_widget = AppTableWidget(
            parent=self,
            actions_list=ACTIONS,
            save_recipe_file=self.system.save_recipe_file,
            get_recipe_file_data=self.system.get_recipe_file_data,
            start_recipe=self.start_recipe,
        )

        # LOG NOTIFICATION WIDGET ###################################
        self.log = None
        self.log_widget = LogWidget(
            on_close=self.clear_log,
            parent=self,
            notification_types=NOTIFICATIONS,
        )
        self.log_widget.move(100, 100)

        # return

        # self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        # self.close()

        #######################################################################
        # ======================= CONNECT FUNCTIONS ========================= #

        for gas in self.main_interface_layout_widget.pressure_block.gases:
            num = gas.number

            gas.connect_valve_function(self.system.change_valve_state)
            self.system.change_gas_valve_opened.connect(gas.draw_is_open, device_num=num)

            gas.connect_change_sccm_function(self.system.set_target_rrg_sccm_action)
            self.system.set_target_rrg_sccm_action.connect(gas.draw_set_target_sccm, device_num=gas.number)
            self.system.full_open_rrg_action.connect(gas.draw_set_target_sccm, device_num=gas.number)
            self.system.full_close_rrg_action.connect(gas.draw_set_target_sccm, device_num=gas.number)

            self.system.get_current_rrg_sccm.connect(gas.update_current_sccm_label, device_num=gas.number)

        # AIR #################
        self.milw.pressure_block.air.\
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

        # RECIPE #############
        self.system.set_current_recipe_step_action.connect(self.add_recipe_step)

        ######################

    def on_create_recipe(self):
        try:
            self.table_widget.on_create_recipe()
        except Exception as e:
            print("On create recipe function error:", e)

    def on_open_recipe(self):
        try:
            file_path = QFileDialog.getOpenFileName(self, 'Выбрать рецепт', '')[0]
            if file_path:
                data = self.system.get_recipe_file_data(file_path)
                self.table_widget.on_open_recipe_file(file_path, data)
        except Exception as e:
            print("On open recipe error:", e)

    def close(self) -> bool:
        self.system.stop()
        return super().close()

    def clear_log(self, uid):
        self.system.clear_log(uid=uid)
        self.log = None

    def __del__(self):
        # print("Window del")
        self.system.destructor()

    def show_time(self):
        print("TIME:", datetime.datetime.now())

    def start_recipe(self):
        try:
            recipe = self.table_widget.get_values()
            self.system.set_recipe(recipe)
            ready = self.system.check_recipe_is_correct()
            # ready = self.system.run_recipe(recipe)
            if not ready:
                return
            # self.system.start_recipe()
            self.system.run_recipe()
            self._recipe_history = []
            self.add_recipe_step({'name': "Инициализация рецепта"})
            self.table_widget.on_close()
            self.main_interface_layout_widget.deactivate_interface()
            self.right_buttons_layout_widget.activate_manage_recipe_buttons()
        except Exception as e:
            self.system.add_error("Start recipe UI error:" + str(e))
            print("Start recipe UI error:", e)

    def add_recipe_step(self, step: dict):  # name="---", index=None):
        name = step.get('name', '-----')
        index = step.get('index', None)
        index = index if index else len(self._recipe_history)
        if self._current_recipe_step:
            if self._current_recipe_step.get('index', -1) == index:
                return
        self._current_recipe_step = {"name": name, "index": index}
        now_time = datetime.datetime.utcnow()
        now_time_str = f"{now_time.hour}:{now_time.minute}:{now_time.second}"
        self._recipe_history.append(f"{now_time_str} | ШАГ №{index}: {name}")
        try:
            self.main_interface_layout_widget.set_current_step(self._recipe_history[-1])
        except:
            pass

    def _update_ui_values(self):
        self.main_interface_layout_widget.temperature_block.show_pressure_block.set_value(
            self.system.accurate_vakumetr_value
        )

        # for i, gas in enumerate(self.main_interface_layout_widget.pressure_block.gases):
        #     gas.update_current_sccm_label(self.system.current_sccms[i])

        for num, temperature in self.system.current_temperatures.items():
            self.main_interface_layout_widget.temperature_block.temps[num].set_current_temperature(
                temperature
            )

    def memory_snapshot(self):
        pass
        # print("MEMORY:", deep_getsizeof(self, set()))
        # gc.collect()
        # snapshot = tracemalloc.take_snapshot()
        # # snapshot.dump(f'test_{datetime.datetime.now()}.txt')
        #
        # for i, stat in enumerate(snapshot.statistics(f'filename')[:5], 1):
        #     print("top_current", i, str(stat))
        #     # logging.info("top_current", i=i, stat=str(stat))

    def get_values_and_log_state(self):
        try:
            self.memory_snapshot()
            self.system.get_values()
            # recipe_step = self.system.current_recipe_step
            # if recipe_step:
            #     last_recipe_steps = self.system.last_recipe_steps
            #     self.add_recipe_step(**recipe_step)
            recipe_state = self.system.recipe_state
            if recipe_state != self._recipe_state:
                self._recipe_state = recipe_state
                self.main_interface_layout_widget.set_current_recipe_status(
                    RECIPE_STATES_TO_STR.get(self._recipe_state, "UNDEFINED")
                )
                if recipe_state == RECIPE_STATES.STOP:
                    self.main_interface_layout_widget.activate_interface()
                    self.right_buttons_layout_widget.deactivate_manage_recipe_buttons()

            self._update_ui_values()

        except Exception as e:
            self.system.add_error(Exception("Ошибка считывания значения: " + str(e)))
            # self.close()
            print("ERROR [get_values_and_log_state]:", e)
        finally:
            try:
            # print("FINALLY:", self.log, "| has logs:",  self.system.has_logs)
                if self.log is None and self.system.has_logs:
                    self.log = self.system.first_log
                    self.log_widget.set_log(self.log)
            except Exception as e:
                print("Set log error:", e)

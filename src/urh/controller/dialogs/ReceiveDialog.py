from datetime import datetime
import locale
import time

import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QCloseEvent, QTransform, QIcon
from PyQt5.QtWidgets import QDialog, QGraphicsView, QWidget, QMessageBox

from urh import constants
from urh.controller.widgets.DeviceSettingsWidget import DeviceSettingsWidget
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.ui.painting.LiveSceneManager import LiveSceneManager
from urh.ui.ui_send_recv import Ui_SendRecvDialog
from urh.util import util, FileOperator
from urh.util.Formatter import Formatter
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager
from urh.ui.my_new_form import Ui_MainWindow
from urh.controller.MyController import MyMon, MyDevSet, MyDB

class RecvDialog(QWidget):
    device_parameters_changed = pyqtSignal(dict)
    change_tab = pyqtSignal()
    start_after_close = pyqtSignal()

    def __init__(self, project_manager: ProjectManager, is_tx: bool, continuous_send_mode=False, parent=None, testing_mode=False):
        super().__init__(parent)
        self.is_tx = is_tx
        self.update_interval = 25

        # This flag is needed. Will cause memory leak otherwise.
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowFlags(Qt.Window)

        self.testing_mode = testing_mode

        self.ui = Ui_SendRecvDialog()
        self.ui.setupUi(self)
        self.setFixedSize(QtCore.QSize(1000, 300))
        # self.setMaximumSize(QtCore.QSize(500, 500))


        util.set_splitter_stylesheet(self.ui.splitter)

        self.graphics_view = None  # type: QGraphicsView

        self.backend_handler = BackendHandler()

        self.ui.btnStop.setEnabled(False)
        # self.ui.btnSave.setEnabled(False)

        self.start = 0
        self.hide_send_ui_items()

        self.device_settings_widget = DeviceSettingsWidget(project_manager, is_tx,
                                                           backend_handler=self.backend_handler,
                                                           continuous_send_mode=continuous_send_mode)
        self.device_settings_widget.setMaximumSize(500,300)


        # self.ui.scrollAreaWidgetContents_2.layout().insertWidget(0, self.device_settings_widget)


        if testing_mode:
            self.device_settings_widget.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        self.timer = QTimer(self)

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

        self.ui.splitter.setSizes([0.3 * self.width(), 0.7 * self.width()])
        # self.ui.splitter.setFixedSize(0.3 * self.width(), 0.7 * self.width())

    @property
    def is_rx(self) -> bool:
        return not self.is_tx

    @property
    def has_empty_device_list(self):
        return self.device_settings_widget.ui.cbDevice.count() == 0

    @property
    def device(self) -> VirtualDevice:
        return self.device_settings_widget.device

    @device.setter
    def device(self, value):
        self.device_settings_widget.device = value

    @property
    def selected_device_name(self) -> str:
        return self.device_settings_widget.ui.cbDevice.currentText()

    def _eliminate_graphic_view(self):
        if self.graphics_view is not None:
            self.graphics_view.eliminate()

        self.graphics_view = None

    def hide_send_ui_items(self):
        for item in ("sliderYscale1","sliderYscale2","label_y_scale","label_y_scale2","btnMon","btnNuke2","btnNuke1","lcdNumber","btnRecordIQ","btnConf","btnSave","lblCurrentRepeatValue", "progressBarMessage",
                     "lblRepeatText", "lSamplesSentText", "progressBarSample", "labelCurrentMessage"):
            getattr(self.ui, item).hide()

    def hide_receive_ui_items(self):
        for item in ("lSamplesCaptured", "lSamplesCapturedText", "lSignalSize", "lSignalSizeText",
                     "lTime", "lTimeText", "labelReceiveBufferFull", "lReceiveBufferFullText"):     #btnSave
            getattr(self.ui, item).hide()

    def set_device_ui_items_enabled(self, enabled: bool):
        self.device_settings_widget.setEnabled(enabled)

    def create_connects(self):
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        self.ui.btnStop.clicked.connect(self.on_stop_clicked)
        self.ui.btnClear.clicked.connect(self.on_clear_clicked)


        self.timer.timeout.connect(self.update_view)
        self.ui.sliderYscale.valueChanged.connect(self.on_slider_y_scale_value_changed)

        self.device_settings_widget.selected_device_changed.connect(self.on_selected_device_changed)
        self.device_settings_widget.device_parameters_changed.connect(self.device_parameters_changed.emit)

    def _create_device_connects(self):

        self.device.stopped.connect(self.on_device_stopped)
        self.device.started.connect(self.on_device_started)
        self.device.sender_needs_restart.connect(self._restart_device_thread)

    def reset(self):
        self.device.current_index = 0
        self.device.current_iteration = 0
        self.ui.lSamplesCaptured.setText("0")
        self.ui.lSignalSize.setText("0")
        self.ui.lTime.setText("0")
        self.ui.lblCurrentRepeatValue.setText("-")
        self.ui.progressBarSample.setValue(0)
        self.ui.progressBarMessage.setValue(0)
        # self.ui.btnSave.setEnabled(False)

    # def init_device(self):
    #     pass

    def save_before_close(self):
        return True

    def emit_editing_finished_signals(self):
        self.device_settings_widget.emit_editing_finished_signals()

    @pyqtSlot()
    def on_selected_device_changed(self):
        if hasattr(self.scene_manager, "plot_data"):
            self.scene_manager.plot_data = None

        self.init_device()

        self.graphics_view.scene_manager = self.scene_manager
        self.graphics_view.setScene(self.scene_manager.scene)

    @pyqtSlot()
    def on_start_clicked(self):
        self.emit_editing_finished_signals()

    @pyqtSlot()
    def on_stop_clicked(self):
        self.device.stop("Stopped receiving: Stop button clicked")

    @pyqtSlot()
    def on_device_stopped(self):
        if self.graphics_view is not None:
            self.graphics_view.capturing_data = False
        self.set_device_ui_items_enabled(True)
        self.ui.btnStart.setEnabled(True)
        self.ui.btnSetting.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        # self.ui.btnStop.setEnabled(False)
        # self.ui.btnSave.setEnabled(self.device.current_index > 0)
        self.device_settings_widget.ui.comboBoxDeviceIdentifier.setEnabled(True)
        self.device_settings_widget.ui.btnRefreshDeviceIdentifier.setEnabled(True)
        self.device_settings_widget.set_bandwidth_status()

        self.timer.stop()
        self.update_view()

    @pyqtSlot()
    def on_device_started(self):
        self.ui.txtEditErrors.clear()
        if self.graphics_view is not None:
            self.graphics_view.capturing_data = True
        #---------------------------------------
        self.ui.btnSave.setEnabled(True)
        # ---------------------------------------
        self.ui.btnStart.setEnabled(False)
        self.ui.btnStop.setEnabled(True)
        # self.ui.btnSetting.setEnabled(True)

        self.device_settings_widget.ui.comboBoxDeviceIdentifier.setEnabled(False)
        self.device_settings_widget.ui.btnRefreshDeviceIdentifier.setEnabled(False)

        self.timer.start(self.update_interval)

    def __parse_error_messages(self, messages):
        messages = messages.lower()

        if "no devices found for" in messages:
            self.device.stop_on_error("Could not establish connection to USRP")
            Errors.usrp_found()
            self.on_clear_clicked()

        elif any(e in messages for e in ("hackrf_error_not_found", "hackrf_error_libusb")):
            self.device.stop_on_error("Could not establish connection to HackRF")
            Errors.hackrf_not_found()
            self.on_clear_clicked()

        elif "no module named gnuradio" in messages:
            self.device.stop_on_error("Did not find gnuradio.")
            Errors.gnuradio_not_installed()
            self.on_clear_clicked()

        elif "rtlsdr-open: error code: -1" in messages:
            self.device.stop_on_error("Could not open a RTL-SDR device.")
            self.on_clear_clicked()

        elif "rtlsdr-open: error code: -12" in messages:
            self.device.stop_on_error("Could not open a RTL-SDR device")
            Errors.rtlsdr_sdr_driver()
            self.on_clear_clicked()

        elif "Address already in use" in messages:
            self._restart_device_thread()

    def update_view(self):
        try:
            self.ui.sliderYscale.setValue(int(self.graphics_view.transform().m22()))
        except AttributeError:
            return

        txt = self.ui.txtEditErrors.toPlainText()
        new_messages = self.device.read_messages()

        self.__parse_error_messages(new_messages)

        if len(new_messages) > 1:
            self.ui.txtEditErrors.setPlainText(txt + new_messages)

        self.ui.lSamplesCaptured.setText(Formatter.big_value_with_suffix(self.device.current_index, decimals=1))
        self.ui.lSignalSize.setText(locale.format_string("%.2f Мб", (8 * self.device.current_index) / (1024 ** 2)))
        self.ui.lTime.setText(locale.format_string("%.2f с", self.device.current_index / self.device.sample_rate))

        # if self.is_rx and self.device.data is not None and len(self.device.data) > 0:
        #     self.ui.labelReceiveBufferFull.setText("{0}%".format(int(100 * self.device.current_index /
        #                                                              len(self.device.data))))

        if self.device.current_index == 0:
            return False

        return True

    def _restart_device_thread(self):
        self.device.stop("Restarting with new port")

        if self.device.backend == Backends.grc:
            self.device.increase_gr_port()

        self.device.start()

    @pyqtSlot()
    def on_clear_clicked(self):
        pass

    def closeEvent(self, event: QCloseEvent):

        if self.device.backend is not Backends.none:
            self.emit_editing_finished_signals()

        self.timer.stop()

        self.device.stop("Dialog closed. Killing recording process.")
        logger.debug("Device stopped successfully.")

        if not self.testing_mode:
            if not self.save_before_close():
                event.ignore()
                return

        time.sleep(0.1)
        if self.device.backend not in (Backends.none, Backends.network):
            # Backend none is selected, when no device is available
            logger.debug("Cleaning up device")
            self.device.cleanup()
            logger.debug("Successfully cleaned up device")
            self.device_settings_widget.emit_device_parameters_changed()

        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())

        if self.device is not None:
            self.device.free_data()

        self.scene_manager.eliminate()

        self._eliminate_graphic_view()
        self.on_stop_clicked()

        self.start_after_close.emit()
        super().closeEvent(event)

    @pyqtSlot(int)
    def on_slider_y_scale_value_changed(self, new_value: int):
        pass
        # Scale Up = Top Half, Scale Down = Lower Half
        # print(new_value)

        # transform = self.graphics_view.transform()
        # self.graphics_view.setTransform(QTransform(transform.m11(), transform.m12(), transform.m13(),
        #                                            transform.m21(), new_value, transform.m23(),
        #                                            transform.m31(), transform.m32(), transform.m33()))

class ReceiveDialog(RecvDialog):
    files_recorded = pyqtSignal(list, float)

    def __init__(self, project_manager, parent=None, testing_mode=False,param_of_dev=[1.8e9,15]):
        try:
            super().__init__(project_manager, is_tx=False, parent=parent, testing_mode=testing_mode)
        except ValueError:
            return

        self.graphics_view = self.ui.graphicsViewReceive
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_receive)
        self.hide_send_ui_items()
        self.already_saved = True
        self.recorded_files = []
        self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Реєстрація IQ відліків")
        self.setWindowIcon(QIcon.fromTheme("media-record"))
        # set really in on_device_started
        self.scene_manager = None  # type: LiveSceneManager
        self.create_connects()
        self.device_settings_widget.update_for_new_device(overwrite_settings=False)

        self.device.frequency = param_of_dev[0]
        self.device.gain = param_of_dev[1]
        self.device.bandwidth = 20e6
        self.ui.btnSetting.setEnabled(False)
        # self.ui.setMaximumSize(QtCore.QSize(400, 40))

    def create_connects(self):
        super().create_connects()
        self.init_device()
        self.ui.btnSetting.clicked.connect(self.on_save_clicked)



    def save_before_close(self):
        if not self.already_saved and self.device.current_index > 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Збереження сигналу")
            msg.setText("Бажаєте зберегти записаний сигнал?")
            okButton = msg.addButton("Так", QMessageBox.ActionRole)
            okAbort = msg.addButton("Відхилити",QMessageBox.NoRole)
            msg.addButton("Ні", QMessageBox.RejectRole)
            msg.exec()
            if msg.clickedButton() == okButton:
                self.on_save_clicked()
            elif msg.clickedButton() == okAbort:
                return False

            # reply = QMessageBox.question(self, self.tr("Збереження сигналу"),
            #                              self.tr("Бажаєте зберегти записаний сигнал?"),
            #                              QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
            # if reply == QMessageBox.Yes:
            #     self.on_save_clicked()
            # elif reply == QMessageBox.Abort:
            #     return False

        try:
            sample_rate = self.device.sample_rate
        except:
            sample_rate = 1e6

        self.files_recorded.emit(self.recorded_files, sample_rate)
        return True

    def update_view(self):
        if super().update_view():
            self.scene_manager.end = self.device.current_index
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.update()

    def init_device(self):
        self.device = VirtualDevice(self.backend_handler, self.selected_device_name, Mode.receive,
                                    device_ip="192.168.10.2", parent=self)

        self._create_device_connects()

        self.scene_manager = LiveSceneManager(np.array([], dtype=self.device.data_type), parent=self)

        self.ui.graphicsViewReceive.Clicable = False
        # self.graphics_view.Clicable:

    @pyqtSlot()
    def on_start_clicked(self):

        super().on_start_clicked()

        self.device.start()



    @pyqtSlot()
    def on_device_started(self):
        print('\t\t\t\t', self.device.frequency)
        time.sleep(0.1)
        # try:
        #
        # except:
        #     print('\t\t\t\t\t123123')
        #     self.device.stop()
        self.scene_manager.plot_data = self.device.data.real if self.device.data is not None else None
        super().on_device_started()

        self.already_saved = False
        self.ui.btnStart.setEnabled(False)
        self.set_device_ui_items_enabled(False)

    @pyqtSlot()
    def on_clear_clicked(self):
        self.ui.btnSetting.setEnabled(False)
        self.scene_manager.clear_path()
        self.reset()

    @pyqtSlot()
    def on_save_clicked(self):
        data = self.device.data[:self.device.current_index]

        dev = self.device
        big_val = Formatter.big_value_with_suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        initial_name = "{0}-{1}-{2}Hz-{3}Sps".format(dev.name, timestamp,
                                                     big_val(dev.frequency), big_val(dev.sample_rate))

        if dev.bandwidth_is_adjustable:
            initial_name += "-{}Hz.wav".format(big_val(dev.bandwidth))

        initial_name = initial_name.replace(Formatter.local_decimal_seperator(), "_").replace("_000", "")

        FileOperator.save_data(data, initial_name, sample_rate=20e6, long_record = True)
        # filename = FileOperator.save_data_dialog(initial_name, data,
        #                                          sample_rate=dev.sample_rate)
        # filename = self.recorded_files

        self.already_saved = True

        # if filename is not None and filename not in self.recorded_files:
        #     self.recorded_files.append(filename)

        self.close()





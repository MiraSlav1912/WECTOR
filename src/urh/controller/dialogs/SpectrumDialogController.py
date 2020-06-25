import socket
from errno import ENETUNREACH
import paramiko
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, pyqtSlot,QPoint, QThread
from PyQt5.QtGui import QWheelEvent, QIcon, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QGraphicsScene, QMessageBox
from urh.controller.dialogs.ReceiveDialog import ReceiveDialog
from urh.dev import config
from urh.controller.dialogs.SendRecvDialog import SendRecvDialog
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.painting.FFTSceneManager import FFTSceneManager
from urh.util import FileOperator
from urh.util.Formatter import Formatter
from datetime import datetime
import time
from PyQt5.QtCore import pyqtSignal
from urh.dev.BackendHandler import BackendHandler
from urh.controller.MyController import MyMon, MyDevSet, MyDB, MyMon_Dialog, MyConf
from urh.util.Errors import Errors
from urh.util.Logger import logger

class SpectrumDialogController(SendRecvDialog):
    files_recorded = pyqtSignal(str)
    left_click = QtCore.pyqtSignal()
    right_click = QtCore.pyqtSignal()
    drag_started = pyqtSignal(QPoint)
    my_start = pyqtSignal(bool)
    change_tab = pyqtSignal()
    un_freaze_scroll = pyqtSignal(bool)
    freaze_scroll = pyqtSignal(bool)
    un_freaze_scroll2 = pyqtSignal(bool)
    freaze_scroll2 = pyqtSignal(bool)


    def __init__(self, project_manager, parent=None, testing_mode=False):
        super().__init__(project_manager, is_tx=False, parent=parent, testing_mode=testing_mode)
        self.project_manager = project_manager
        self.graphics_view = self.ui.graphicsViewFFT
        self.update_interval = 1
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_spectrum)
        self.hide_send_ui_items()
        self.index = ''

        self.ui.btnSave.hide()
        self.setWindowTitle("Spectrum Analyzer")
        self.setWindowIcon(QIcon(":/icons/icons/spectrum.svg"))
        self.ui.btnStart.setToolTip(self.tr("Старт"))
        self.ui.btnStop.setToolTip(self.tr("Стоп"))
        self.ui.btnNuke1.setToolTip(self.tr("   Включення/виключення \nприймачів діапазону 4-6 ГГц"))
        self.ui.btnNuke2.setToolTip(self.tr("   Включення/виключення \nприймачів діапазону 6-8 ГГц"))
        self.ui.btnRecordIQ.setToolTip(self.tr("Реєстрація IQ відліків тривалістю до 15 секунд"))
        self.ui.btnMon.setToolTip(self.tr("Додаткове вікно завантаженності діапазонів"))

        self.scene_manager = FFTSceneManager(parent=self, graphic_view=self.graphics_view)
        self.graphics_view.setScene(self.scene_manager.scene)
        self.graphics_view.scene_manager = self.scene_manager
        self.ui.graphicsViewSpectrogram.setScene(QGraphicsScene())
        self.__clear_spectrogram()

        self.gain_timer = QTimer(self)
        self.gain_timer.setSingleShot(True)
        self.if_gain_timer = QTimer(self)
        self.if_gain_timer.setSingleShot(True)
        self.bb_gain_timer = QTimer(self)
        self.bb_gain_timer.setSingleShot(True)

        self.my_overlap_factor = 0.5
        self.my_clear_timer = QTimer(self)
        self.my_clear_timer.setSingleShot(True)

        self.old_freq = None
        self.hide_receive_ui_items()
        self.create_connects()
        self.device_settings_widget.update_for_new_device(overwrite_settings=False)
        self.value1 = []
        self.value1.append(20950)
        self.summ = []
        self.tick = 0
        self.click = 0
        self.my_save = False
        self.ui.btnSave.setEnabled(False)
        self.my_start.emit(True)
        self.bd_freq =''
        self.my_monitor_controller = MyMon(parent=self.ui.groupBox)
        self.ui.groupBox.layout().addWidget(self.my_monitor_controller)
        self.my_monitor_controller.BarIndex.connect(self.change)
        self.status_k = 0
        self.mymy_freq = None
        self.chek_freq = 0
        self.MyConf = MyConf()
        self.my_mass_vodopad = []
        self.my_monitor_dialog = MyMon_Dialog()
        self.ui.btnSetting.setChecked(True)
        self.ui.btnRecordIQ.setEnabled(False)
        self.ui.btnSetting.setStyleSheet("background-color: green")
        self.ui.btnMon.clicked.connect(self.MonDialog)
        self.ui.btnConf.clicked.connect(self.ConfDialog)


    @pyqtSlot(list)
    def my_tr(self,data):
        self.my_monitor_dialog.new_series(data)

    def MonDialog(self):
        self.my_monitor_controller.tr_sig_1.connect(self.my_tr)
        self.my_monitor_controller.tr_sig_2.connect(self.my_tr)
        self.my_monitor_controller.tr_sig_3.connect(self.my_tr)
        self.my_monitor_controller.tr_sig_4.connect(self.my_tr)
        self.my_monitor_dialog.show()

    def ConfDialog(self):
        self.MyConf.show()

    def __clear_spectrogram(self):
        self.my_mass_vodopad = []
        self.ui.graphicsViewSpectrogram.scene().clear()
        window_size = Spectrogram.DEFAULT_FFT_WINDOW_SIZE
        self.ui.graphicsViewSpectrogram.scene().setSceneRect(0, 0, window_size, 20 * window_size)
        self.spectrogram_y_pos = 0
        self.ui.graphicsViewSpectrogram.fitInView(self.ui.graphicsViewSpectrogram.sceneRect())


    def __update_spectrogram(self):
        spectrogram = Spectrogram(self.device.data,overlap_factor=self.my_overlap_factor)
        spectrogram.data_min = -80
        spectrogram.data_max = 10
        scene = self.ui.graphicsViewSpectrogram.scene()
        pixmap = QPixmap.fromImage(spectrogram.create_spectrogram_image(transpose=True))
        pixmap_item = scene.addPixmap(pixmap)
        self.my_mass_vodopad.append(pixmap)
        pixmap_item.moveBy(0, self.spectrogram_y_pos)
        self.spectrogram_y_pos += pixmap.height()

        if self.spectrogram_y_pos >= scene.sceneRect().height():

            while sum(map(lambda x:x.height(), self.my_mass_vodopad)) >= 20480:
                scene.setSceneRect(0, 0, Spectrogram.DEFAULT_FFT_WINDOW_SIZE, self.spectrogram_y_pos)
                self.ui.graphicsViewSpectrogram.ensureVisible(pixmap_item)

                scene.removeItem(scene.items().pop(-1))
                self.my_mass_vodopad.pop(-1)

    def _eliminate_graphic_view(self):
        super()._eliminate_graphic_view()
        if self.ui.graphicsViewSpectrogram and self.ui.graphicsViewSpectrogram.scene() is not None:
            self.ui.graphicsViewSpectrogram.scene().clear()
            self.ui.graphicsViewSpectrogram.scene().setParent(None)
            self.ui.graphicsViewSpectrogram.setScene(None)
        self.ui.graphicsViewSpectrogram = None

    @pyqtSlot(int)
    def my_overlap_factor_func(self,value):
        if value == 1:
            self.my_overlap_factor = 0.1
            self.on_clear_clicked()
        elif value == 2:
            self.my_overlap_factor = 0.5
            self.on_clear_clicked()
        elif value == 3:
            self.my_overlap_factor = 0.9
            self.on_clear_clicked()

    def save_trigger(self):
        self.ui.btnSave.setEnabled(False)
        self.my_save = True

    def create_connects(self):
        super().create_connects()
        self.ui.btnSave.clicked.connect(self.save_trigger)
        self.graphics_view.my_freq_wheel.connect(self.on_graphics_view_freq_clicked) #---------- перестраиваеться частота насколько далеко мышка от центральной частоти
        self.graphics_view.my_wheel_event_freq.connect(self.scroll_freq)
        self.graphics_view.wheel_event_triggered.connect(self.on_graphics_view_wheel_event_triggered)
        self.graphics_view.my_freq_to_main.connect(self.my_selecte_freq)
        self.ui.btnSetting.clicked.connect(self.click_active)
        self.ui.sliderYscale1.valueChanged.connect(self.device_settings_widget.on_slider_gain_value_changed)
        self.ui.sliderYscale2.valueChanged.connect(self.my_overlap_factor_func)
        self.device_settings_widget.ui.sliderGain.valueChanged.connect(self.on_slider_gain_value_changed)
        self.device_settings_widget.ui.sliderBasebandGain.valueChanged.connect(
            self.on_slider_baseband_gain_value_changed)
        self.device_settings_widget.ui.sliderIFGain.valueChanged.connect(self.on_slider_if_gain_value_changed)
        self.device_settings_widget.ui.spinBoxFreq.valueChanged.connect(self.on_spinbox_frequency_editing_finished)
        self.device_settings_widget.ui.spinBoxFreq.valueChanged.connect(self.on_clear_changed)
        self.ui.btnRecordIQ.clicked.connect(self.my_record_long_iq_data)
        self.gain_timer.timeout.connect(self.device_settings_widget.ui.spinBoxGain.editingFinished.emit)
        self.if_gain_timer.timeout.connect(self.device_settings_widget.ui.spinBoxIFGain.editingFinished.emit)
        self.bb_gain_timer.timeout.connect(self.device_settings_widget.ui.spinBoxBasebandGain.editingFinished.emit)
        self.my_clear_timer.timeout.connect(self.on_clear_clicked)
        self.ui.btnNuke1.clicked.connect(self.start_Nuke1)
        self.ui.btnNuke2.clicked.connect(self.start_Nuke2)

    def my_record_long_iq_data(self):
        pm = self.project_manager
        try:
            self.on_stop_clicked()
            self.on_clear_clicked()
            self.r = ReceiveDialog(pm, parent=self,param_of_dev =[self.device.frequency,self.device.gain])
            self.r.ui.btnSave.hide()
        except OSError as e:
            logger.error(repr(e))
            return
        if self.r.has_empty_device_list:
            Errors.no_device()
            self.r.close()
            return

        self.r.device_parameters_changed.connect(pm.set_device_parameters)
        self.r.show()
        self.r.start_after_close.connect(self.on_start_clicked)


    def stop_iq_read(self):
        self.on_stop_clicked()
        data = self.device.data[:self.device.current_index]
        dev = self.device
        big_val = Formatter.big_value_with_suffix
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        initial_name = "{0}-{1}-{2}Hz-{3}Sps".format(dev.name, timestamp,
                                                     big_val(dev.frequency), big_val(dev.sample_rate))
        if dev.bandwidth_is_adjustable:
            initial_name += "-{}Hz.wav".format(big_val(dev.bandwidth))

        initial_name = initial_name.replace(Formatter.local_decimal_seperator(), "_").replace("_000", "")

        FileOperator.save_data(data, initial_name, sample_rate=dev.sample_rate)
        self.files_recorded.emit(initial_name)
        self.init_device()
        self.device.frequency = self.old_freq
        self.old_freq = None
        self.on_start_clicked()
        self.change_tab.emit()

    def scroll_freq(self, a: int):
            print(self.device.frequency)
            if self.ui.btnStop.isEnabled():
                if a < 0:
                    self.device_settings_widget.ui.spinBoxFreq.stepDown()
                else:
                    self.device_settings_widget.ui.spinBoxFreq.stepUp()
            self.ui.lcdNumber.display(self.real_freq())
            name = ['4...5ГГц', '5...6ГГц', '6...7ГГц', '7...8ГГц']
            if self.real_freq() > 4000e6 and self.real_freq() < 8000e6:
                if self.chek_freq - self.real_freq() >= 10e6:
                    self.chek_freq = self.chek_freq - 20e6
                    if self.my_monitor_controller.check_index[1] - 1 > 0:
                        self.my_monitor_controller.check_index[1] = self.my_monitor_controller.check_index[1] - 1
                    else:
                        new_name = name.index(self.my_monitor_controller.check_index[0])
                        if new_name != 0:
                            self.my_monitor_controller.check_index = [name[new_name - 1], 49]
                elif self.real_freq() - self.chek_freq >= 10e6:
                    self.chek_freq = self.chek_freq + 20e6
                    if self.my_monitor_controller.check_index[1] + 1 < 50:
                        self.my_monitor_controller.check_index[1] = self.my_monitor_controller.check_index[1] + 1
                    else:
                        try:
                            new_name = name.index(self.my_monitor_controller.check_index[0])
                        except Exception as E:
                            return
                        if new_name != 3:
                            self.my_monitor_controller.check_index = [name[new_name + 1], 0]

    def click_active(self):
        if self.ui.btnSetting.isChecked() == False:
            self.ui.btnSetting.setStyleSheet("background-color: red")
            self.mymy_freq = None
            self.scene_manager.scene.my_clear()
        elif self.ui.btnSetting.isChecked():
            self.ui.btnSetting.setStyleSheet("background-color: green")
            if self.mymy_freq != None:
                self.record_markered_diapazone(self.mymy_freq)

    @pyqtSlot(list)
    def my_selecte_freq(self, my_sel_freq):
        if self.ui.btnSetting.isChecked():
            self.record_markered_diapazone(my_sel_freq)
        else:
            self.mymy_freq = my_sel_freq

    def record_markered_diapazone(self,my_sel_freq):
        try:
            bw = abs(my_sel_freq[1] - my_sel_freq[0])
        except:
            return
        old_freq = self.device.frequency
        old_gain = self.device.gain
        self.on_stop_clicked()
        self.device = VirtualDevice(BackendHandler(), self.selected_device_name, Mode.receive)
        self.device.frequency = my_sel_freq[0] + bw / 2
        sample_rate = 20e6
        self.device.sample_rate = sample_rate
        self.device.bandwidth = bw
        self.device.start()
        time.sleep(0.1)
        while self.device.data[:self.device.current_index].size < 1 * sample_rate: pass
        self.device.stop('lol_1')
        data = self.device.data[:self.device.current_index]
        dev = self.device
        big_val = Formatter.big_value_with_suffix
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        freq = 6800e6 + self.status_k - my_sel_freq[0] + bw /2
        initial_name = "{0}-{1}-{2}Hz-{3}Sps".format(dev.name, timestamp,
                                                     big_val(freq), big_val(dev.sample_rate))
        if dev.bandwidth_is_adjustable:
            initial_name += "-{}Hz.wav".format(big_val(dev.bandwidth))

        initial_name = initial_name.replace(Formatter.local_decimal_seperator(), "_").replace("_000", "")
        FileOperator.save_data(data, initial_name,sample_rate=sample_rate)
        self.files_recorded.emit(initial_name)
        self.init_device()
        self.device.frequency = old_freq
        self.device.gain = old_gain
        self.device.sample_rate = 20e6
        self.change_tab.emit()

    @pyqtSlot(int)
    def change(self, index):
        self.ui.btnStart.setEnabled(True)
        if index >=100:
              self.status_k = 2000e6
              self.graphics_view.status_k_in_LiveGraphicView = 2000e6
              self.graphics_view.scene().status_k = 2000e6
        else:
            self.status_k = 0
            self.graphics_view.status_k_in_LiveGraphicView = 0
            self.graphics_view.scene().status_k = 0
        self.on_stop_clicked()

        def rng(start, end, div):
            return range(int(start), int(end), (int(end) - int(start)) // int(div))

        TCP_IP = '192.168.0.10'
        TCP_PORT = 1032
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            com_index = index
            b = rng(4010e6, 8010e6, 200)
            d = {i: b[i] for i in range(len(b))}
            self.device_settings_widget.ui.labelDCCorrection2.setText(str(int(d[index] / 10e5)) + " МГц")

            index_input = 2790e6 - index * 20e6
            if com_index >= 100:
                index_input = 2790e6 - (com_index - 100) * 20e6
            self.device_settings_widget.ui.spinBoxFreq.setValue(index_input)
            if com_index < 100:
                s.send(b'\t\t\t')
                data = s.recv(10)
                operation = list(data)[3]
                operation_send = operation | 128
                send_data = [0, 0, 0]
                send_data.append(operation_send)
                tcp = bytes(send_data)
                s.send(tcp)
            if com_index >= 100:
                s.send(b'\t\t\t')
                data = s.recv(10)
                if data[3] & 128 == 128:
                    operation = list(data)[3]
                    operation_send = operation ^ 128
                    send_data = [0, 0, 0]
                    send_data.append(operation_send)
                    tcp = bytes(send_data)
                    s.send(tcp)
            s.close()

        except IOError as e:
            if e.errno == ENETUNREACH:
                print("M lost")
                QMessageBox.information(self, "Відсутність підключення до мережі", "Зв'язок втрачено. Перевірте мережеве підключення до РКП")
            else:
                raise

        self.chek_freq = self.real_freq()
        self.ui.lcdNumber.display(self.real_freq())
        self.on_start_clicked()

    def real_freq(self):
        return 6800e6 + self.status_k - self.device_settings_widget.ui.spinBoxFreq.value()

    def resizeEvent(self, event: QResizeEvent):
        if self.ui.graphicsViewSpectrogram and self.ui.graphicsViewSpectrogram.sceneRect():
            self.ui.graphicsViewSpectrogram.fitInView(QtCore.QRectF(0.0, 0.0, 1024.0, 20480.0))

    def update_view(self):
        if super().update_view():
            x, y = self.device.spectrum
            if x is None or y is None:
                return
            self.scene_manager.scene.frequencies = x
            self.scene_manager.plot_data = y
            self.scene_manager.init_scene()
            self.scene_manager.show_full_scene()
            self.graphics_view.fitInView(self.graphics_view.sceneRect())
            try:
                self.__update_spectrogram()
            except MemoryError:
                self.__clear_spectrogram()
                self.__update_spectrogram()

    def init_device(self):
        self.device = VirtualDevice(self.backend_handler, self.selected_device_name,
                                    Mode.spectrum,
                                    device_ip="192.168.10.2", parent=self)
        self._create_device_connects()

    @pyqtSlot(QWheelEvent)
    def on_graphics_view_wheel_event_triggered(self, event: QWheelEvent):
        self.ui.sliderYscale.wheelEvent(event)

    @pyqtSlot(float)
    def on_graphics_view_freq_clicked(self, freq: float):
        pass
        self.device_settings_widget.ui.spinBoxFreq.setValue(freq)
        self.device_settings_widget.ui.spinBoxFreq.editingFinished.emit()
        self.ui.lcdNumber.display(self.real_freq())

    @pyqtSlot()
    def on_spinbox_frequency_editing_finished(self):
        frequency = self.device_settings_widget.ui.spinBoxFreq.value()
        self.device.frequency = frequency
        self.scene_manager.scene.center_freq = frequency

    @pyqtSlot()
    def on_start_clicked(self):
        self.ui.btnConf.setEnabled(False)
        self.ui.btnRecordIQ.setEnabled(True)
        super().on_start_clicked()
        self.device.start()
        self.on_clear_clicked()
        self.ui.btnSave.setEnabled(True)
        self.my_save = False
        self.summ = []
        self.tick = 0

    @pyqtSlot()
    def on_device_started(self):
        self.ui.graphicsViewSpectrogram.scene().sceneRect()
        super().on_device_started()
        self.device_settings_widget.ui.spinBoxPort.setEnabled(False)
        self.device_settings_widget.ui.lineEditIP.setEnabled(False)
        self.device_settings_widget.ui.cbDevice.setEnabled(False)
        self.ui.btnStart.setEnabled(False)
        self.my_start.emit(False)

    @pyqtSlot()
    def on_device_stopped(self):
        self.ui.btnConf.setEnabled(True)
        self.ui.btnRecordIQ.setEnabled(False)
        self.device_settings_widget.ui.spinBoxPort.setEnabled(True)
        self.device_settings_widget.ui.lineEditIP.setEnabled(True)
        self.device_settings_widget.ui.cbDevice.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        super().on_device_stopped()
        self.my_start.emit(True)

    @pyqtSlot()
    def on_clear_clicked(self):
        self.__clear_spectrogram()
        self.scene_manager.clear_path()
        self.scene_manager.clear_peak()
        self.scene_manager.scene.my_clear()

    # затримка 100 мс при події
    def on_clear_changed(self):
        self.my_clear_timer.start(100)

    @pyqtSlot(int)
    def on_slider_gain_value_changed(self, value: int):
        self.gain_timer.start(250)

    @pyqtSlot(int)
    def on_slider_if_gain_value_changed(self, value: int):
        self.if_gain_timer.start(250)

    @pyqtSlot(int)
    def on_slider_baseband_gain_value_changed(self, value: int):
        self.bb_gain_timer.start(250)

    @pyqtSlot()
    def kill_thread(self):
        self.index = 1
        self.stop()

    @pyqtSlot()
    def kill_thread2(self):
        self.index2 = 1
        self.stop2()

    def stop(self):

        if self.index == 1:
            self.my_ssh1 = My_SSH_Thread()
            self.my_ssh1.terminate()
            self.freaze_scroll.emit(True)

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname='192.168.0.9', username=config.USER_NUKE_1, password=config.PASS_NUKE_1,
                               port=22)
                stdin, stdout, stderr = client.exec_command("ps -x")
                data = stdout.read() + stderr.read()

                list_process = str(data).split('\\n')
                # print(data)
                for i in list_process:
                    if 'IQRead.py' in i:
                        splt = i.split()
                        client.exec_command("kill {}".format(splt[0]))

                client.close()
                self.ui.btnNuke1.setStyleSheet("background-color: red")
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

    def stop2(self):

        if self.index2 == 1:

            self.my_ssh2 = My_SSH_Thread()
            self.my_ssh2.terminate()
            self.freaze_scroll2.emit(True)

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname='192.168.0.132', username=config.USER_NUKE_2, password=config.PASS_NUKE_2,
                               port=22)
                stdin, stdout, stderr = client.exec_command("ps -x")
                data = stdout.read() + stderr.read()

                list_process = str(data).split('\\n')
                print(data)
                for i in list_process:
                    if 'IQRead.py' in i:
                        splt = i.split()
                        client.exec_command("kill {}".format(splt[0]))

                client.close()
                self.ui.btnNuke2.setStyleSheet("background-color: red")
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

    def start_Nuke1(self):
        if self.ui.btnNuke1.isChecked() == True:

            self.ui.btnNuke1.setStyleSheet("background-color: green")
            self.my_ssh = My_SSH_Thread()
            self.my_ssh.start()
            self.my_ssh.my_kill.connect(self.kill_thread)
            # self.my_ssh.terminate()
            self.un_freaze_scroll.emit(True)

        else:
            self.my_ssh.terminate()
            self.freaze_scroll.emit(True)

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname='192.168.0.9', username=config.USER_NUKE_1, password=config.PASS_NUKE_1,
                               port=22)
                stdin, stdout, stderr = client.exec_command("ps -x")
                data = stdout.read() + stderr.read()

                list_process = str(data).split('\\n')
                print(data)
                for i in list_process:
                    if 'IQRead.py' in i:
                        splt = i.split()
                        client.exec_command("kill {}".format(splt[0]))

                client.close()
                self.ui.btnNuke1.setStyleSheet("background-color: red")
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

    def start_Nuke2(self):
        if self.ui.btnNuke2.isChecked() == True:

            self.my_ssh2 = My_SSH_Thread2()
            self.my_ssh2.start()
            self.my_ssh2.my_kill2.connect(self.kill_thread2)
            self.un_freaze_scroll2.emit(True)
            self.ui.btnNuke2.setStyleSheet("background-color: green")

        else:
            self.my_ssh2.terminate()
            self.freaze_scroll2.emit(True)

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname='192.168.0.132', username=config.USER_NUKE_2, password=config.PASS_NUKE_2,
                               port=22)
                stdin, stdout, stderr = client.exec_command("ps -x")
                data = stdout.read() + stderr.read()

                list_process = str(data).split('\\n')
                print(data)
                for i in list_process:
                    if 'IQRead.py' in i:
                        splt = i.split()
                        client.exec_command("kill {}".format(splt[0]))

                client.close()
                self.ui.btnNuke2.setStyleSheet("background-color: red")
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass


class My_SSH_Thread(QThread):
    my_kill = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname='192.168.0.9', username=config.USER_NUKE_1, password=config.PASS_NUKE_1,
                                port=22)
            stdin, stdout, stderr = self.client.exec_command("python3 /home/nuke/PycharmProjects/IQREAD/IQRead.py",
                                                             get_pty=True)

            for line in iter(stdout.readline, ""):
                print(line, end="")
            self.client.close()
            self.my_kill.emit()
            print("Finished")

        except Exception as e:
            self.client.close()


class My_SSH_Thread2(QThread):
    my_kill2 = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname='192.168.0.132', username=config.USER_NUKE_2, password=config.PASS_NUKE_2,
                                port=22)
            stdin, stdout, stderr = self.client.exec_command("python3 /home/nuke-2/PycharmProjects/IQRead/IQRead.py",
                                                             get_pty=True)

            for line in iter(stdout.readline, ""):
                print(line, end="")
            self.client.close()
            self.my_kill2.emit()
            print("Finished")

        except IOError as e:
            self.client.close()
            if e.errno == ENETUNREACH:
                pass

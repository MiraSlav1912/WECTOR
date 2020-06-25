import shutil
from tkinter import filedialog
from PyQt5.QtCore import QDir, QTimer
from PyQt5.QtGui import QColor
from urh.dev import config
from urh.ui.ui_my_mon import MonitorTab, MonitorTab_Dialog
from PyQt5.QtChart import *
from urh.ui.ui_send_recv import Ui_SendRecvDialog
import subprocess as sp
from urh.dev.BackendHandler import BackendHandler
from urh.controller.widgets.DeviceSettingsWidget import DeviceSettingsWidget
from PyQt5.QtCore import QThread, pyqtSignal
import zmq
from functools import partial
import datetime
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
from tkinter import *
from urh.ui.ui_my_bd import UI_TAB
import os
import webbrowser
import subprocess
import paramiko,time
from urh.ui.my_new_form import Ui_MainWindow
from errno import ENETUNREACH
import pickle
from urh.ui.ui_my_new_database_insert import Ui_MainWindow1

# MY_PATH = '/WECTOR/src/urh'

class MyThread(QThread):
    mysignal = pyqtSignal(list)
    def __init__(self,ip_adress,number, parent=None):
        QThread.__init__(self, parent)
        self.number = number
        self.ip_adress = ip_adress
    def run(self):
        # SET TIMEOUT
        self.context = zmq.Context()
        self.consumer_receiver = self.context.socket(zmq.PULL)
        self.consumer_receiver.connect("{}".format(self.ip_adress))
        while True:
            self.mysignal.emit([self.consumer_receiver.recv_json()[::-1],str(self.number)]) # 4...5ГГц

class MyThreadStatusNetwork(QThread):
    myStatusNuke = pyqtSignal(str)
    myStatusNuke2 = pyqtSignal(str)
    myStatusRPK = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        while True:
            self.status(config.IP_NUKE_1, self.myStatusNuke)
            self.status(config.IP_NUKE_2, self.myStatusNuke2)
            self.status(config.IP_RPK, self.myStatusRPK)

    def status(self, ip, signal):
        status, result = sp.getstatusoutput("ping -c1 -w2  " + str(ip))
        if status == 0:
            signal.emit(ip + " Up")
        else:
            signal.emit(ip + " Down")


class MyMon(QWidget):
    BarIndex = pyqtSignal(int)
    tr_sig_1 = pyqtSignal(list)
    tr_sig_2 = pyqtSignal(list)
    tr_sig_3 = pyqtSignal(list)
    tr_sig_4 = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = MonitorTab()
        self.ui.setupUi(self)


        self.check_index = [0 for i in range(50)]
        self.gain = [15,15,15,15]

        self.mythread1 = MyThread("tcp://{}:5550".format(config.IP_NUKE_1),0)  # 4...5ГГц
        self.mythread1.start()
        self.mythread1.mysignal.connect(self.new_series)
        self.mythread1.mysignal.connect(self.tr_1) # передача даних для відбворення на MAIN_Mon

        self.mythread2 = MyThread("tcp://{}:5551".format(config.IP_NUKE_1),1)  # 5...6ГГц
        self.mythread2.start()
        self.mythread2.mysignal.connect(self.new_series)
        self.mythread2.mysignal.connect(self.tr_2)


        self.mythread3 = MyThread("tcp://{}:5552".format(config.IP_NUKE_2),2)  # 6...7ГГц
        self.mythread3.start()
        self.mythread3.mysignal.connect(self.new_series)
        self.mythread3.mysignal.connect(self.tr_3)

        self.mythread4 = MyThread("tcp://{}:5553".format(config.IP_NUKE_2),3)  # 7...8ГГц
        self.mythread4.start()
        self.mythread4.mysignal.connect(self.new_series)
        self.mythread4.mysignal.connect(self.tr_4)

        try:
            self.context = zmq.Context()
            self.zmq_socket = self.context.socket(zmq.PUSH)
            self.zmq_socket.bind("tcp://{}:5560".format(config.IP_MAIN_ARM))
        except Exception as e:
            print('Помилка MAIN ARM', e)

        self.ui.verticalSlider.sliderReleased.connect(self.set_value)
        self.ui.verticalSlider2.sliderReleased.connect(self.set_value)
        self.ui.verticalSlider3.sliderReleased.connect(self.set_value)
        self.ui.verticalSlider4.sliderReleased.connect(self.set_value)

        self.ui.verticalSlider.valueChanged.connect(partial(self.set_value_lable_gain,0))
        self.ui.verticalSlider2.valueChanged.connect(partial(self.set_value_lable_gain,1))
        self.ui.verticalSlider3.valueChanged.connect(partial(self.set_value_lable_gain,2))
        self.ui.verticalSlider4.valueChanged.connect(partial(self.set_value_lable_gain,3))

    def tr_1(self,data):
        self.tr_sig_1.emit(data)
    def tr_2(self,data):
        self.tr_sig_2.emit(data)
    def tr_3(self,data):
        self.tr_sig_3.emit(data)
    def tr_4(self,data):
        self.tr_sig_4.emit(data)

    def set_value_lable_gain(self,num,data):

        self.gain[num] = data
        [value.setText(str(self.gain[index])) for index,value in enumerate([self.ui.label_GAIN,self.ui.label_2GAIN,self.ui.label_3GAIN,self.ui.label_4GAIN])]

    def set_value(self):
        try:
            self.context = zmq.Context()
            self.zmq_socket.send_json(self.gain, zmq.NOBLOCK)
            self.zmq_socket.send_json(self.gain, zmq.NOBLOCK)
            self.zmq_socket.send_json(self.gain, zmq.NOBLOCK)
            self.zmq_socket.send_json(self.gain, zmq.NOBLOCK)
            
        except Exception as E:
            self.zmq_socket.close()
            print("Помилка встановлення підсилення на чотири приймача на місці АРМ 192.168.0.20")

    def new_series(self, data):
        axis = QBarCategoryAxis()
        axis.append(['{0}00'.format(i) for i in range(10)])
        axis.setLabelsAngle(0)
        axis.setLabelsColor(QColor('white'))
        axis.setGridLineColor(QColor(0,0,0,0))

        if   data[1] == '0':
            self.update_series(self.ui.chart1,data,'4...5ГГц',axis) # QBarCategoryAxis()
        elif data[1] == '1':
            self.update_series(self.ui.chart2,data,'5...6ГГц',axis)
        elif data[1] == '2':
            self.update_series(self.ui.chart3,data,'6...7ГГц',axis)
        elif data[1] == '3':
            self.update_series(self.ui.chart4, data,'7...8ГГц', axis)

    def update_series(self,chart,data,my_id,axis):
        chart.removeAllSeries()
        chart.setAxisX(axis)
        chart.addSeries(self.append_series(data[0], my_id))
        chart.legend().setLabelColor(QColor('white'))
        chart.legend().setShowToolTips(False)



    def append_series(self, data, name, doubleClickedOn = True):
        # HEIGHT OF BARSET
        set1 = QBarSet('')
        set1.setBorderColor(QColor(0, 0, 0, 0))
        self.series = QStackedBarSeries()

        if self.check_index[0] == name:
            set1.setColor(QColor('yellow'))
            set1.append([0 for i in range(self.check_index[1])]+[data[self.check_index[1]]])
            set0 = QBarSet(name)
            set0.setColor(QColor(144, 238, 144, 255))
            data[self.check_index[1]] = 0
            set0.append(data)
            set2 = QBarSet('')
            set2.setColor(QColor(0, 0, 0, 0))
            set2.setBorderColor(QColor(0, 0, 0, 0))
            set2.append([500])
            self.series.append(set0)
            self.series.append(set1)
            self.series.append(set2)
        else:
            set1.setColor(QColor(0, 0, 0, 0))
            set1.append([500])
            set0 = QBarSet(name)
            set0.setColor(QColor(144, 238, 144, 255))
            set0.append(data)
            self.series.append(set0)
            self.series.append(set1)

        if doubleClickedOn:
            self.series.doubleClicked.connect(self._on_click_series)

        self.series.hovered.connect(self.on_hover)
        self.series.setBarWidth(1)

        return self.series

    def on_hover(self,isHovered,Index,Bar_set):
        if isHovered:
            Hf = MyMon.Hovered_frequency(Bar_set.label(),Index)
            if Hf != None:
                QToolTip.showText(QtCore.QPoint(QCursor.pos()),'{} G'.format(Hf))

    def _on_click_series(self, index, bar_set):
        self.check_index = [bar_set.label(), index]
        print(self.check_index)
        if bar_set.label() == '4...5ГГц':
            self.BarIndex.emit(index)
        if bar_set.label() == '5...6ГГц':
            self.BarIndex.emit(index+50)
        if bar_set.label() == '6...7ГГц':
            self.BarIndex.emit(index+100)
        if bar_set.label() == '7...8ГГц':
            self.BarIndex.emit(index+150)

    @staticmethod
    def rng(start, end, div):
        return range(int(start), int(end), (int(end) - int(start)) // int(div))

    @staticmethod
    def Hovered_frequency(Bar_set, Index):
        Freq = MyMon.rng(4010e6, 8010e6, 200)
        if Bar_set == '4...5ГГц':
            return Freq[0 + Index] / 1e9
        if Bar_set == '5...6ГГц':
            return Freq[50 + Index] / 1e9
        if Bar_set == '6...7ГГц':
            return Freq[100 + Index] / 1e9
        if Bar_set == '7...8ГГц':
            return Freq[150 + Index] / 1e9

class MyMon_Dialog(QDialog):

    def __init__(self):
        super().__init__()
        self.ui = MonitorTab_Dialog()
        self.ui.setupUi(self)
        self.check_index = [0 for i in range(50)]

    def new_series(self, data):
        MyMon.new_series(self,data)

    def update_series(self, chart, data, my_id, axis):
        MyMon.update_series(self,chart, data, my_id, axis)

    def append_series(self, data, name):
        # MyMon.append_series(self,data,name,False)
        set0 = QBarSet(name)
        set0.setColor(QColor(144, 238, 144, 255))
        set0.append(data)

        # HEIGHT OF BARSET
        set1 = QBarSet('')
        set1.setBorderColor(QColor(0,0,0,0))
        set1.setColor(QColor(0,0,0,0))
        set1.append([1500])

        self.series = QStackedBarSeries()
        self.series.hovered.connect(self.on_hover)
        self.series.append(set0)
        self.series.append(set1)

        self.series.setBarWidth(1)
        return self.series

    def on_hover(self,isHovered,Index,Bar_set):
        MyMon.on_hover(self,isHovered,Index,Bar_set)

def rng(start, end, div):
    return range(int(start), int(end), (int(end) - int(start)) // int(div))

def Hovered_frequency(Bar_set,Index):
    Freq = rng(4010e6, 8010e6, 200)
    if Bar_set =='4...5ГГц':
        return Freq[0+Index]/1e9
    if Bar_set =='5...6ГГц':
        return Freq[50+Index]/1e9
    if Bar_set == '6...7ГГц':
        return Freq[100+Index]/1e9
    if Bar_set == '7...8ГГц':
        return Freq[150+Index]/1e9

class MyDevSet(QWidget):
    def __init__(self, project_manager):
        super().__init__()
        self.ui = Ui_SendRecvDialog()

        self.ui.setupUi(self)
        self.hide_ui_items()

        self.backend_handler = BackendHandler()

        self.device_settings_widget = DeviceSettingsWidget(project_manager, is_tx=False,
                                                           backend_handler=self.backend_handler,
                                                           continuous_send_mode=False)
        self.ui.scrollAreaWidgetContents_2.layout().insertWidget(0, self.device_settings_widget)

        self.ui.btnSave.hide()
        self.ui.btnClear.hide()

    def hide_ui_items(self):
        self.ui.layoutWidget.setVisible(False)


class MyDB(QtWidgets.QMainWindow):
    my_new_session_bd = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py


        self._my_pulse = '0 мs'
        self._my_pulse_auto = '0 ms'
        self._my_period_auto = '0 mm'
        self._my_freq_auto = '0 kHz'
        self._my_name = ''
        self.enter = ''
        self.fint = ''
        self.data = ''
        self.path = ''

        self.fileName = ''
        self.fileName1 = ''

        self.path_image_station = ''
        self.path_image_spectrum = ''

        self.ui = UI_TAB()
        self.ui.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.ui.tableWidget_2.cellClicked[int, int].connect(self.clickedStandby)
        self.ui.tableWidget.cellClicked[int, int].connect(self.clickedEl_intel)
        self.ui.pushButton.clicked.connect(self.find_in_El_intel)
        self.ui.pushButton2.clicked.connect(self.delete)
        self.ui.pushButton3.clicked.connect(self.edit)
        self.ui.pushButton_2.clicked.connect(self.selection)
        self.ui.pushButton6.clicked.connect(self.open_sesion)

        self.ui.label_14.mousePressEvent = self.openSpectrumImage
        self.ui.label_2.mousePressEvent = self.openStationImage

        self.ui.pushButton4.clicked.connect(self.open_record_folder)
        self.ui.pushButton5.clicked.connect(self.creat_new_sesion)

        self.showEl_int()
        pixmap = QPixmap(QDir.currentPath() + config.MY_PATH+"/main_window.png")
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label_14.setPixmap(pixmap)



    def open_sesion(self):
        root = Tk()
        root.withdraw()
        root.fileName = filedialog.askopenfilename(initialdir ="/home", title="Виберіть Базу Даних", filetypes=(("Файл Бази Даних","*.db"),("Будь-який файл","*.*")))
        root.destroy()
        if root.fileName == ():
            QMessageBox.information(self, "База данних", "Файл бази даних не вибрано")

        else:
            self.new_session = root.fileName
        #
        # if self.new_session[-2:] != "db":
        #     QMessageBox.warning(self, "База данних", "Невірно відкритий файл")
        # else:
            self.selection()
            self.selection()



    def creat_new_sesion(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        try:
            self.new_session = pickle.load(open(QDir.currentPath()+config.MY_PATH+"/path.pickle", "rb")) + "/"+ timestamp + ".db"
            pickle_out = open(QDir.currentPath()+config.MY_PATH+"/path_bd.pickle", "wb")
            pickle.dump(self.new_session, pickle_out)
            pickle_out.close()

            self.my_new_session_bd.emit(self.new_session)
            shutil.copy(QDir.currentPath() + config.MY_PATH+"/datatimes.db", self.new_session)
        except Exception as E:
            print("Файл не знайдено в цьому каталозі")
#-------------------------
        pickle_in = open(QDir.currentPath() + config.MY_PATH+"/path_bd.pickle", "rb")
        self.path_db = pickle.load(pickle_in)
        self.conn = sqlite3.connect("{0}".format(self.path_db))
        cur = self.conn.cursor()
        cur.execute(
            '''INSERT INTO table2 (Date, Freq, Spectrum_width, Type_modulation, Pulse_duration, Follow, Comment, path) values (?,?,?,?,?,?,?,?)''',
            ('','','','','','',timestamp,''))
        self.conn.commit()
        cur.close()
        self.conn.close()
#-------------------------

        self.selection()
        self.selection()

    def open_in_detail(self):
        self.path_image_station = QDir.currentPath()+config.MY_PATH+"/" + str(self.ui.tableWidget.model().index(0, 9).data())
        self.path_image_spectrum = QDir.currentPath()+config.MY_PATH+"/" + str(self.ui.tableWidget.model().index(0, 8).data())


    def find_in_El_intel(self):
        self.conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
        Type = self.ui.lineEdit.text()
        Freq = self.ui.lineEdit_14.text()
        Comment = self.ui.lineEdit_11.text()
        Band = self.ui.lineEdit_13.text()
        Mod = self.ui.lineEdit_10.text()
        impulse = self.ui.lineEdit_12.text()
        follow = self.ui.lineEdit_16.text()

        sql = "SELECT * FROM El_intel where Type like '%{}%' and Comment like '%{}%' and Freq_kHz like '{}%' and Spectrum_width_kHz like '{}%' and Type_modulation like '{}%' and Pulse_duration_mcs like '{}%' and Follow_period like '{}%' ".format(
            Type, Comment, Freq, Band, Mod, impulse, follow)

        cur = self.conn.cursor()
        cur.execute(sql)
        self.ui.tableWidget.setRowCount(0)
        data = cur.fetchall()

        for row_number, row_data in enumerate(data):
            self.ui.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.ui.tableWidget.resizeColumnsToContents()
        self.conn.close()

    def open_record_folder(self):
        self.path = '/'.join(self.path.split('/')[:-1])
        subprocess.Popen(['xdg-open','{0}'.format(self.path)])


    def openSpectrumImage(self, event):
        try:
            if self.path_image_spectrum == QDir.currentPath()+config.MY_PATH+"/urh/":
                print("Spectruym is not present")
            else:
                webbrowser.open(self.path_image_spectrum)
        except Exception as E:
            print("Spectruym error openSpectrumImage")

    def openStationImage(self, event):
        try:
            if self.path_image_station == QDir.currentPath() +config.MY_PATH:

                print("station is not presen")
            else:
                webbrowser.open(self.path_image_station)

        except Exception as E:
            print("station error openStationImage")


    def image(self):
        self.fileName1, filetype1 = QFileDialog.getOpenFileName(self, "Виберіть зображення станції", "All Files (*)")
        self.ui.label_2.setPixmap(QPixmap(self.fileName1))
        self.ui.label_2.setScaledContents(True)

        self.fileName, filetype = QFileDialog.getOpenFileName(self,"Виберіть загальне зображення сигналу", "All Files (*)")
        self.ui.label_14.setPixmap(QPixmap(self.fileName))
        self.ui.label_14.setScaledContents(True)
#-----------------------------------------


    def selection(self):
        try:
            connection = "{0}".format(self.new_session)
            self.conn = sqlite3.connect('{0}'.format(connection))   #("/home/aleksey/Desktop/123.db")
        except Exception as E:
            pass
        Date = self.ui.lineEdit_15.text()
        Freq = self.ui.lineEdit_14.text()
        Comment = self.ui.lineEdit_11.text()
        Band = self.ui.lineEdit_13.text()
        Mod = self.ui.lineEdit_10.text()
        impulse = self.ui.lineEdit_12.text()
        follow = self.ui.lineEdit_16.text()

        sql = "SELECT * FROM table2 where Date like '{0}%' and Comment like '%{1}%' and Freq like '%{2}%' and Spectrum_width like '%{3}%' and Type_modulation like '%{4}%' and Pulse_duration like '%{5}%' and Follow like '%{6}%' order by id desc".format(Date, Comment, Freq, Band, Mod, impulse, follow)

        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.ui.tableWidget_2.setRowCount(0)
            data = cur.fetchall()

            for row_number, row_data in enumerate(data):
                self.ui.tableWidget_2.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ui.tableWidget_2.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    # self.ui.tableWidget_2.resizeColumnsToContents()

                    if data == '':
                        self.ui.tableWidget_2.item(row_number, column_number).setBackground(
                            QtGui.QColor(255, 0, 0, 100))
            self.conn.close()
        except Exception as E:
            print("Error to read DB (def selection)")
            # QMessageBox.warning(self, "База данних", "Помилка зчитування бази даних")


    def show(self):
        self.conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
        # self.conn = pymysql.connect(host="localhost", user="admin", password="admin", db="vector")
        sql = "SELECT * FROM el_intel where Type = '{}'".format(self._my_name)  ## limit 0, 10

        cur = self.conn.cursor()
        cur.execute(sql)
        self.ui.tableWidget.setRowCount(0)
        data = cur.fetchall()
        for row_number, row_data in enumerate(data):
            self.ui.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                self.ui.tableWidget.cellClicked[int, int].connect(self.clickedEl_intel)


                for index,j in enumerate([self.ui.lineEdit_Name,self.ui.lineEdit_2,self.ui.lineEdit_3,self.ui.lineEdit_4,self.ui.lineEdit_5,self.ui.lineEdit_6,self.ui.lineEdit_7]):
                    j.setText(self.ui.tableWidget.model().index(0,index +1).data())
                    j.setReadOnly(True)
                    pixmap = QPixmap(QDir.currentPath()+config.MY_PATH+ "/"+ str(self.ui.tableWidget.model().index(0, 9).data()))
                    self.ui.label_2.setPixmap(pixmap)
                    pixmap = QPixmap(QDir.currentPath()+config.MY_PATH+ "/"+str(self.ui.tableWidget.model().index(0, 8).data()))
                    self.ui.label_14.setPixmap(pixmap)

        self.conn.close()

    
    def showEl_int(self):

        self.conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
        #self.conn = pymysql.connect(host="localhost", user="admin", password="admin", db="vector")

        sql = "SELECT * FROM el_intel"

        cur = self.conn.cursor()
        cur.execute(sql)
        self.ui.tableWidget.setRowCount(0)
        data = cur.fetchall()
        for row_number, row_data in enumerate(data):
            self.ui.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.ui.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.conn.close()



    def showStand(self):
        try:
            connection = "{0}".format(self.new_session)
            self.conn = sqlite3.connect('{0}'.format(connection))

            # self.conn = sqlite3.connect("database.db")
            sql = "SELECT * FROM table2 order by id desc"  ## limit 0, 10

            cur = self.conn.cursor()
            cur.execute(sql)
            self.ui.tableWidget_2.setRowCount(0)
            data = cur.fetchall()

            for row_number, row_data in enumerate(data):
                self.ui.tableWidget_2.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.ui.tableWidget_2.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    # self.ui.tableWidget_2.resizeColumnsToContents()
                    if data =='':
                        self.ui.tableWidget_2.item(row_number, column_number).setBackground(QtGui.QColor(255,0,0,100))
        except Exception as E:
            pass

    def clickedStandby(self, r, ):
        pixmap = QPixmap()
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label_14.setPixmap(pixmap)
        [i.setText("") for i in [self.ui.lineEdit_2,self.ui.lineEdit_3,self.ui.lineEdit_4,self.ui.lineEdit_5,
                                 self.ui.lineEdit_6,self.ui.lineEdit_7,self.ui.lineEdit_Name]]

        for index, obj in enumerate([self.ui.lineEdit_date,self.ui.lineEdit_2,self.ui.lineEdit_3,self.ui.lineEdit_4,
                                     self.ui.lineEdit_5,self.ui.lineEdit_6,self.ui.lineEdit_7]):
            obj.setText(self.ui.tableWidget_2.model().index(r, index).data())

        [i.setReadOnly(False) for i in
         [self.ui.lineEdit_2, self.ui.lineEdit_3, self.ui.lineEdit_4, self.ui.lineEdit_5, self.ui.lineEdit_6,
          self.ui.lineEdit_7,self.ui.lineEdit_Name]]

        self.path = self.ui.tableWidget_2.model().index(r, 7).data()

        pixmap = QPixmap(QDir.currentPath() + config.MY_PATH+"/main_window.png")
        self.ui.label_2.setPixmap(pixmap)

        #--------------------
        pixmapScreen = QPixmap(str(self.ui.tableWidget_2.model().index(r, 7).data())[:-4]+".jpg")
        self.ui.label_14.setPixmap(pixmapScreen)
        #-----------------------
        self.path_image_spectrum = ''
        self.path_image_station = ""


#------------------------------------------

    def edit(self, r,):
        try:
            connection = "{0}".format(self.new_session)
            conn = sqlite3.connect('{0}'.format(connection))

            # conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            self.data = self.ui.tableWidget_2.model().index(r, 0).data()
            try:
                cur.execute('''update table2 set Freq = ?, Spectrum_width = ?, Type_modulation = ?,Pulse_duration = ?, Follow = ?, Comment = ?
                                                               where Date = ?''',
                            (self.ui.lineEdit_2.text(),
                             self.ui.lineEdit_3.text(),
                             self.ui.lineEdit_4.text(),
                             self.ui.lineEdit_5.text(),
                             self.ui.lineEdit_6.text(),
                             self.ui.lineEdit_7.text(),
                             self.ui.lineEdit_date.text()))
            except Exception as E:
                pass

            conn.commit()
            cur.close()
            conn.close()

            # self.conn = sqlite3.connect("database.db")
            # self.conn = pymysql.connect(host="localhost", user="admin", password="admin", db="vector")

            self.selection()
            QMessageBox.information(self, "База данних", "Дані відредактовано!")
        except Exception as E:
            pass

    def delete(self):
        try:
            connection = "{0}".format(self.new_session)
            conn = sqlite3.connect('{0}'.format(connection))

            # conn = sqlite3.connect('database.db')
            c = conn.cursor()
            t = (self.ui.lineEdit_date.text(),)

            c.execute('DELETE FROM table2 WHERE Date=?', t)
            conn.commit()
            self.conn = sqlite3.connect("database.db")
            # self.conn = pymysql.connect(host="localhost", user="admin", password="admin", db="vector")
            self.selection()
            try:
                os.remove(self.path)
                os.remove(self.path[:-4]+".jpg")
            except FileNotFoundError as Ex:
                print('файл не знайдено')
            QMessageBox.information(self, "База данних", "Дані успішно видалено!")

        except Exception as e:
            print(121)
#----- вместо пустоты изображеие картинки-------

#------------------------------------------------------------------------------------------------------------------------
    def clickedEl_intel(self, r, ):

        self.ui.lineEdit_2.setText(self.ui.tableWidget.model().index(r, 2).data())
        self.ui.lineEdit_2.setReadOnly(True)
        self.ui.lineEdit_3.setText(self.ui.tableWidget.model().index(r, 3).data())
        self.ui.lineEdit_3.setReadOnly(True)
        self.ui.lineEdit_4.setText(self.ui.tableWidget.model().index(r, 4).data())
        self.ui.lineEdit_4.setReadOnly(True)
        self.ui.lineEdit_5.setText(self.ui.tableWidget.model().index(r, 5).data())
        self.ui.lineEdit_5.setReadOnly(True)
        self.ui.lineEdit_6.setText(self.ui.tableWidget.model().index(r, 6).data())
        self.ui.lineEdit_6.setReadOnly(True)
        self.ui.lineEdit_7.setText(self.ui.tableWidget.model().index(r, 7).data())
        self.ui.lineEdit_7.setReadOnly(True)

        pixmap = QPixmap(QDir.currentPath() + config.MY_PATH+ "/"+self.ui.tableWidget.model().index(r, 9).data())
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label_2.setScaledContents(True)

        self.ui.lineEdit_Name.setText(self.ui.tableWidget.model().data(self.ui.tableWidget.currentIndex()))
        self.ui.lineEdit_Name.setReadOnly(True)

        pixmap = QPixmap(QDir.currentPath() +config.MY_PATH+"/"+self.ui.tableWidget.model().index(r, 8).data())
        self.ui.label_14.setPixmap(pixmap)
        print(QDir.currentPath() + config.MY_PATH+ "/"+self.ui.tableWidget.model().index(r, 9).data())

        self.ui.lineEdit_id.setText(self.ui.tableWidget.model().index(r, 0).data())
        self.ui.lineEdit_img.setText(self.ui.tableWidget.model().index(r, 8).data())
        self.ui.lineEdit_image.setText(self.ui.tableWidget.model().index(r, 9).data())


        if self.ui.tableWidget.model().index(r, 9).data() == '':
            self.path_image_station = ""
        else:
            self.path_image_station = QDir.currentPath() + config.MY_PATH+"/"+self.ui.tableWidget.model().index(r, 9).data()
        if self.ui.tableWidget.model().index(r, 8).data() == '':
            self.path_image_spectrum = ''
        else:
            self.path_image_spectrum = QDir.currentPath() + config.MY_PATH+"/"+self.ui.tableWidget.model().index(r, 8).data()
        print(self.path_image_station)

        if self.ui.tableWidget.model().index(r, 9).data() == "":
            pixmap = QPixmap(QDir.currentPath() + config.MY_PATH+"/main_window.png")
            self.ui.label_2.setPixmap(pixmap)
        else:
            pass
        if self.ui.tableWidget.model().index(r, 8).data() == "":
            pixmap = QPixmap(QDir.currentPath() + config.MY_PATH+"/main_window.png")
            self.ui.label_14.setPixmap(pixmap)
        else:
            pass

    def delete_el_Intel(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Видалення з бази данних")
        msg.setText("Видалити еталонну станцію з переліку?")
        okButton = msg.addButton("Так", QMessageBox.AcceptRole)
        msg.addButton("Ні", QMessageBox.RejectRole)
        msg.exec()

        if msg.clickedButton() == okButton:
            conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
            c = conn.cursor()
            t = (self.ui.lineEdit_id.text(), )
            spec = self.ui.lineEdit_image.text()
            station = self.ui.lineEdit_img.text()
            c.execute('DELETE FROM el_intel WHERE id = ?', t)
            conn.commit()
            print(QDir.currentPath() + config.MY_PATH + "/"+spec,"---------------", QDir.currentPath() + config.MY_PATH + "/"+station)
            if spec != "":
                try:
                    os.remove(QDir.currentPath() + config.MY_PATH + "/"+spec)
                except Exception as E:
                    pass
            if station != "":
                try:
                    os.remove(QDir.currentPath() + config.MY_PATH+"/"+station)
                except Exception as E:
                   pass
            QMessageBox.information(self, "База данних", "Дані успішно видалено!")



    def edit_el_intel(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Редагування бази данних")
        msg.setText("Бажаєте внести зміни до станції з переліку?")
        okButton = msg.addButton("Так", QMessageBox.AcceptRole)
        msg.addButton("Ні", QMessageBox.RejectRole)
        msg.exec()
        if msg.clickedButton() == okButton:
            self.ui.lineEdit_id.setReadOnly(False)
            self.ui.lineEdit_Name.setReadOnly(False)
            self.ui.lineEdit_2.setReadOnly(False)
            self.ui.lineEdit_3.setReadOnly(False)
            self.ui.lineEdit_4.setReadOnly(False)
            self.ui.lineEdit_5.setReadOnly(False)
            self.ui.lineEdit_6.setReadOnly(False)
            self.ui.lineEdit_7.setReadOnly(False)
            self.ui.lineEdit_image.setReadOnly(False)
            self.ui.lineEdit_img.setReadOnly(False)


            if self.ui.lineEdit_img.text() == "":
                self.img = 0
                print("-")
            else:
                self.img = 1
                print("+")

            if self.ui.lineEdit_image.text() == "":
                self.image = 0
                print("-")
            else:
                self.image = 1
                print("+")

    def insert_edited_el_intel(self):
        if self.image == 1 and self.img ==1:
            conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
            cur = conn.cursor()
            t = (self.ui.lineEdit_id.text(),)
            cur.execute('''update el_intel set Type = ?, Freq_kHz = ?, Spectrum_width_kHz = ?,Type_modulation = ?, Pulse_duration_mcs = ?, Follow_period = ?, Comment = ?
                                                                                                                  where id = ?''',
                        (self.ui.lineEdit_Name.text(),
                         self.ui.lineEdit_2.text(),
                         self.ui.lineEdit_3.text(),
                         self.ui.lineEdit_4.text(),
                         self.ui.lineEdit_5.text(),
                         self.ui.lineEdit_6.text(),
                         self.ui.lineEdit_7.text(),
                         self.ui.lineEdit_id.text()))
            conn.commit()
            cur.close()
            conn.close()
            self.selection()

        if self.image == 0 and self.img == 0:
            self.fileName1, filetype1 = QFileDialog.getOpenFileName(self, "Виберіть зображення станції", "All Files (*)")
            pixmap1 = QPixmap(self.fileName1)
            self.ui.label_2.setPixmap(pixmap1)
            self.ui.label_2.setScaledContents(True)

            self.fileName, filetype = QFileDialog.getOpenFileName(self, "Виберіть загальне зображення сигналу", "All Files (*)")
            pixmap = QPixmap(self.fileName)
            self.ui.label_14.setPixmap(pixmap)
            self.ui.label_14.setScaledContents(True)
            try:
                a = shutil.copy(self.fileName, QDir.currentPath() + config.MY_PATH+'/db/imageSpectrum')
                a1 = a.split("/")[-3:]
                a2 = a1[0] + "/" + a1[1] + "/" + a1[2]
                self.ui.lineEdit_image.setText(a2)
            except OSError as err:
                print("spectrum Error")
                self.ui.lineEdit_image.setText("")
            try:
                b = shutil.copy(self.fileName1, QDir.currentPath() + config.MY_PATH+'/db/imageStation')
                b1 = b.split("/")[-3:]
                b2 = b1[0]+ "/" +b1[1] + "/" + b1[2]
                self.ui.lineEdit_img.setText(b2)
            except OSError as err:
                print("image Error")
                self.ui.lineEdit_img.setText("")
            conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
            cur = conn.cursor()
            t = (self.ui.lineEdit_id.text(),)
            cur.execute('''update el_intel set Type = ?, Freq_kHz = ?, Spectrum_width_kHz = ?,Type_modulation = ?, Pulse_duration_mcs = ?, Follow_period = ?, Comment = ?, Image = ?, img = ?
                                                                                                                              where id = ?''',
                        (self.ui.lineEdit_Name.text(),
                         self.ui.lineEdit_2.text(),
                         self.ui.lineEdit_3.text(),
                         self.ui.lineEdit_4.text(),
                         self.ui.lineEdit_5.text(),
                         self.ui.lineEdit_6.text(),
                         self.ui.lineEdit_7.text(),
                         self.ui.lineEdit_image.text(),
                         self.ui.lineEdit_img.text(),
                         self.ui.lineEdit_id.text()))
            conn.commit()
            cur.close()
            conn.close()
            self.selection()

        if self.image == 1 and self.img == 0:
            self.fileName, filetype = QFileDialog.getOpenFileName(self, "Виберіть загальне зображення сигналу", "All Files (*)")
            pixmap = QPixmap(self.fileName)
            self.ui.label_14.setPixmap(pixmap)
            self.ui.label_14.setScaledContents(True)
            try:
                a = shutil.copy(self.fileName, QDir.currentPath() + config.MY_PATH+'/db/imageSpectrum')
                a1 = a.split("/")[-3:]
                a2 = a1[0]+ "/" +a1[1] + "/" + a1[2]
                self.ui.lineEdit_image.setText(a2)
            except OSError as err:
                print("spectrum Error")
                self.ui.lineEdit_image.setText("")

            conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
            cur = conn.cursor()
            t = (self.ui.lineEdit_id.text(),)
            cur.execute('''update el_intel set Type = ?, Freq_kHz = ?, Spectrum_width_kHz = ?,Type_modulation = ?, Pulse_duration_mcs = ?, Follow_period = ?, Comment = ?, Image = ?
                                                                                                                              where id = ?''',
                        (self.ui.lineEdit_Name.text(),
                         self.ui.lineEdit_2.text(),
                         self.ui.lineEdit_3.text(),
                         self.ui.lineEdit_4.text(),
                         self.ui.lineEdit_5.text(),
                         self.ui.lineEdit_6.text(),
                         self.ui.lineEdit_7.text(),
                         self.ui.lineEdit_image.text(),
                         self.ui.lineEdit_id.text()))
            conn.commit()
            cur.close()
            conn.close()
            self.selection()

        if self.image == 0 and self.img == 1:
            self.fileName1, filetype1 = QFileDialog.getOpenFileName(self, "Виберіть зображення станції",
                                                                    "All Files (*)")
            pixmap1 = QPixmap(self.fileName1)
            self.ui.label_2.setPixmap(pixmap1)
            self.ui.label_2.setScaledContents(True)
            try:
                b = shutil.copy(self.fileName1, QDir.currentPath() + config.MY_PATH+'/db/imageStation')
                b1 = b.split("/")[-3:]
                b2 = b1[0] +"/" + b1[1] + "/" + b1[2]
                self.ui.lineEdit_img.setText(b2)
            except OSError as err:
                print("image Error")
                self.ui.lineEdit_img.setText("")

            conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
            cur = conn.cursor()
            t = (self.ui.lineEdit_id.text(),)
            cur.execute('''update el_intel set Type = ?, Freq_kHz = ?, Spectrum_width_kHz = ?,Type_modulation = ?, Pulse_duration_mcs = ?, Follow_period = ?, Comment = ?, img = ?
                                                                                                                              where id = ?''',
                        (self.ui.lineEdit_Name.text(),
                         self.ui.lineEdit_2.text(),
                         self.ui.lineEdit_3.text(),
                         self.ui.lineEdit_4.text(),
                         self.ui.lineEdit_5.text(),
                         self.ui.lineEdit_6.text(),
                         self.ui.lineEdit_7.text(),
                         self.ui.lineEdit_img.text(),
                         self.ui.lineEdit_id.text()))
            conn.commit()
            cur.close()
            conn.close()
            self.selection()

        self.ui.lineEdit_Name.setReadOnly(True)
        self.ui.lineEdit_2.setReadOnly(True)
        self.ui.lineEdit_3.setReadOnly(True)
        self.ui.lineEdit_4.setReadOnly(True)
        self.ui.lineEdit_5.setReadOnly(True)
        self.ui.lineEdit_6.setReadOnly(True)
        self.ui.lineEdit_7.setReadOnly(True)
        QMessageBox.information(self, "База данних", "Дані відредактовано!")


class MyConf(QDialog):
    my_choise_dir1 = pyqtSignal(str)
    windowsClose = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.count_network = 0

        self.ui.btnPathOpen.clicked.connect(self.path)
        self.ui.btnPathIQ.clicked.connect(self.pathIQRecord)

        self.ui.btnOffN1.clicked.connect(self.power_off1)
        self.ui.btnRebootN1.clicked.connect(self.reboot1)

        self.ui.btnOffN2.clicked.connect(self.power_off2)
        self.ui.btnRebootN2.clicked.connect(self.reboot2)



        self.path_default()

    def closeEvent(self, event):
        self.windowsClose.emit()
        print(event)

    def path_default(self):
        pickle_in = open(QDir.currentPath()+config.MY_PATH+"/path.pickle", "rb")
        self.path_default_text = pickle.load(pickle_in)
        self.ui.path_textbox.setText(self.path_default_text)
        self.my_choise_dir1.emit(self.path_default_text)

        pickle_in = open(QDir.currentPath()+config.MY_PATH+"/path_IQRecord.pickle", "rb")
        self.path_long_record = pickle.load(pickle_in)
        self.ui.path_textbox_bd.setText(self.path_long_record)

#-----
        # self.path_default_text = QDir.currentPath() + '/tmp_wav'
        # self.ui.path_textbox.setText(self.path_default_text)
        # self.my_choise_dir1.emit(self.path_default_text)

    def path(self):
        self.dir = QFileDialog.getExistingDirectory(self, self.tr("Шлях збереження "))
        if self.dir != '':
            pickle_out = open(QDir.currentPath()+config.MY_PATH+"/path.pickle", "wb")
            pickle.dump(self.dir, pickle_out)
            pickle_out.close()
            self.ui.path_textbox.setText(self.dir)
            self.my_choise_dir1.emit(self.dir)

    def pathIQRecord(self):

        self.IQ = QFileDialog.getExistingDirectory(self, self.tr("Шлях збереження "))
        if self.IQ != '':
            pickle_out = open(QDir.currentPath()+config.MY_PATH+"/path_IQRecord.pickle", "wb")
            pickle.dump(self.IQ, pickle_out)
            pickle_out.close()
            self.ui.path_textbox_bd.setText(self.IQ)


    def power_off1(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Завершення роботи АРМ 1")
        msg.setText("Завершити роботу АРМ 1?")
        okButton = msg.addButton("Так", QMessageBox.ActionRole)
        msg.addButton("Ні", QMessageBox.RejectRole)
        msg.exec()
        if msg.clickedButton() == okButton:

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=config.IP_NUKE_1, username='admin', password='kolopok', port=22)
                stdin, stdout, stderr = client.exec_command("shutdown now -h")
                data = stdout.read() + stderr.read()
                print(data)
                client.close()
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

    def reboot1(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Перезавантаження АРМ 1")
        msg.setText("Перезавантажити АРМ 1?")
        okButton = msg.addButton("Так", QMessageBox.ActionRole)
        msg.addButton("Ні", QMessageBox.RejectRole)
        msg.exec()
        if msg.clickedButton() == okButton:

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=config.IP_NUKE_1, username='admin', password='kolopok', port=22)
                stdin, stdout, stderr = client.exec_command("reboot")
                data = stdout.read() + stderr.read()
                print(data)
                client.close()
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

    def power_off2(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Завершення роботи АРМ 2")
        msg.setText("Завершити роботу АРМ 2?")
        okButton = msg.addButton("Так", QMessageBox.ActionRole)
        msg.addButton("Ні", QMessageBox.RejectRole)
        msg.exec()
        if msg.clickedButton() == okButton:

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=config.IP_NUKE_2, username='admin', password='123456789', port=22)
                stdin, stdout, stderr = client.exec_command("shutdown now -h")
                data = stdout.read() + stderr.read()
                print(data)
                client.close()
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

    def reboot2(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Перезавантаження АРМ 2")
        msg.setText("Перезавантажити АРМ 2?")
        okButton = msg.addButton("Так", QMessageBox.ActionRole)
        msg.addButton("Ні", QMessageBox.RejectRole)
        msg.exec()
        if msg.clickedButton() == okButton:

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=config.IP_NUKE_2, username='admin', password='123456789', port=22)
                stdin, stdout, stderr = client.exec_command("reboot")
                data = stdout.read() + stderr.read()
                print(data)
                client.close()
            except IOError as e:
                if e.errno == ENETUNREACH:
                    pass

class MyDialog(QDialog):
    my_show = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow1()
        self.ui.setupUi(self)

        self.ui.btn_insert.clicked.connect(self.insert)
        self.ui.pushButton.clicked.connect(self.image_station)
        self.ui.pushButton_5.clicked.connect(self.image_spectrum)

        self.fileName_station = ""
        self.fileName_spectrum = ""

    def image_station(self):
        self.fileName_station, filetype = QFileDialog.getOpenFileName(self, "Виберіть зображення станції", "All Files (*)")
        pixmap = QPixmap(self.fileName_station)
        self.ui.label_9.setPixmap(pixmap)
        self.ui.label_9.setScaledContents(True)

    def image_spectrum(self):
        self.fileName_spectrum, filetype = QFileDialog.getOpenFileName(self, "Виберіть загальне зображення сигналу",
                                                              "All Files (*)")
        pixmap = QPixmap(self.fileName_spectrum)
        self.ui.label_8.setPixmap(pixmap)
        self.ui.label_8.setScaledContents(True)

    def insert(self, MyDB):
        try:
            self.a = shutil.copy(self.fileName_station, QDir.currentPath() + config.MY_PATH+'/db/imageStation')
            self.a1 = self.a.split("/")[-3:]
            self.station_path = self.a1[0] + "/" + self.a1[1] + "/" + self.a1[2]
        except Exception as E:
            self.station_path = ""
        try:
            self.b = shutil.copy(self.fileName_spectrum, QDir.currentPath() + config.MY_PATH+'/db/imageSpectrum')
            self.b1 = self.b.split("/")[-3:]
            self.spectrum_path = self.b1[0] + "/" + self.b1[1] + "/" + self.b1[2]
        except Exception as E:
            self.spectrum_path = ""

        self.conn = sqlite3.connect(QDir.currentPath()+config.MY_PATH+"/database.db")
        cur = self.conn.cursor()
        cur.execute(
            '''INSERT INTO el_intel (Type, Freq_kHz, Spectrum_width_kHz, Type_modulation, Pulse_duration_mcs, Follow_period, Comment, img,Image) values (?,?,?,?,?,?,?,?,?)''',
            (self.ui.lineEdit_new_name.text(),
             self.ui.lineEdit_freq.text(),
             self.ui.lineEdit_bandwidth.text(),
             self.ui.lineEdit_modulation.text(),
             self.ui.lineEdit_pulse.text(),
             self.ui.lineEdit_period.text(),
             self.ui.lineEdit_comment.text(), self.station_path, self.spectrum_path
             ))
        self.conn.commit()
        cur.close()
        self.conn.close()
        self.close()
        a = "1"
        self.my_show.emit(a)
        QMessageBox.information(self, "База данних", "Дані успішно додано!")


# def get_data(self):
    #
    #         TCP_IP = config.IP_RPK
    #         TCP_PORT = 1032
    #         BUFFERSIZE = 10
    #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         try:
    #             s.connect((TCP_IP, TCP_PORT))
    #
    #             comand = b'\t\t\t'
    #             s.send(comand)
    #             data = s.recv(10)
    #
    #             s.close()
    #
    #             if data[3] & 32 == 32:
    #                 self.ui.pushButton_7.setStyleSheet("background-color: green")
    #             else:
    #                 self.ui.pushButton_7.setStyleSheet("background-color: red")
    #
    #             if data[3] & 64 == 64:
    #                 self.ui.pushButton_8.setStyleSheet("background-color: green")
    #             else:
    #                 self.ui.pushButton_8.setStyleSheet("background-color: red")
    #
    #             if len(data) > 1:
    #                 self.ui.bConnect.setStyleSheet("background-color: green")
    #             else:
    #                 self.ui.bConnect.setStyleSheet("background-color: red")
    #                 # QMessageBox.information(self, "Відсутність підключення до мережі", "Зв'язок втрачено. Перевірте мережеве підключення")
    #
    #             cur1 = (list(data)[5])
    #             cur2 = (list(data)[6])
    #             cu1 = int(cur1)
    #             cu2 = int(cur2)
    #             tok1 = cu1 * 510.0 / 153.0
    #             c1 = round(tok1, 2)
    #             # print(c1)
    #             tok11 = str(c1)
    #             tok2 = cu2 * 510.0 / 153.0
    #             c2 = round(tok2, 2)
    #             # print(c2)
    #             tok22 = str(c2)
    #             self.ui.label_3.setText(tok11)
    #             self.ui.label_4.setText(tok22)
    #
    #             self.count_network = 0
    #             time.sleep(1)
    #         except socket.error:
    #
    #             if self.count_network < 1:
    #                 self.count_network += 1
    #
    #                 self.ui.pushButton_7.setStyleSheet("background-color: red")
    #                 self.ui.pushButton_8.setStyleSheet("background-color: red")
    # def K1(self):
    #     TCP_IP = config.IP_RPK
    #     TCP_PORT = 1032
    #     BUFFERSIZE = 10
    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         s.connect((TCP_IP, TCP_PORT))
    #         s.send(b'\t\t\t')
    #         data = s.recv(10)
    #         if self.ui.chbK1.isChecked():
    #             s.send(b'\t\t\t')
    #             operation = list(data)[3]
    #             operation_send = operation | 32
    #             send_data = [0, 0, 0]
    #             send_data.append(operation_send)
    #             tcp = bytes(send_data)
    #             s.send(tcp)
    #         else:
    #             operation = list(data)[3]
    #             operation_send = operation ^ 32
    #             send_data = [0, 0, 0]
    #             send_data.append(operation_send)
    #             tcp = bytes(send_data)
    #             s.send(tcp)
    #         s.close()
    #
    #     except IOError as e:
    #         if e.errno == ENETUNREACH:
    #             print("K1 lost")
    #             # QMessageBox.information(self, "No connection", "Connection TCP/IP lost Try again")
    #         else:
    #             raise
    #
    # def K2(self):
    #     TCP_IP = config.IP_RPK
    #     TCP_PORT = 1032
    #     BUFFERSIZE = 10
    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         s.connect((TCP_IP, TCP_PORT))
    #         s.send(b'\t\t\t')
    #         data = s.recv(10)
    #         if self.ui.chbK2.isChecked():
    #             s.send(b'\t\t\t')
    #             operation = list(data)[3]
    #             operation_send = operation | 64
    #             send_data = [0, 0, 0]
    #             send_data.append(operation_send)
    #             tcp = bytes(send_data)
    #             s.send(tcp)
    #         else:
    #             operation = list(data)[3]
    #             operation_send = operation ^ 64
    #             send_data = [0, 0, 0]
    #             send_data.append(operation_send)
    #             tcp = bytes(send_data)
    #             s.send(tcp)
    #         s.close()
    #
    #     except IOError as e:
    #         if e.errno == ENETUNREACH:
    #             print("K2 lost")
    #             # QMessageBox.information(self, "No connection", "Connection TCP/IP lost Try again")
    #         else:
    #             raise

    # -----------------------------------------------------------------------------------------------


    # def insert(self):
    #     try:
    #         a = shutil.copy(self.fileName, QDir.currentPath() + '/db/imageSpectrum')
    #         a1 = a.split("/")[-3:]
    #         a2 = a1[0] + "/" + a1[1] + "/" + a1[2]
    #         q = 0
    #     except OSError as err:
    #         print("spectrum Error")
    #         q = 1
    #
    #     try:
    #         b = shutil.copy(self.fileName1, QDir.currentPath() + '/db/imageStation')
    #         b1 = b.split("/")[-3:]
    #         b2 = b1[0] + "/" + b1[1] + "/" + b1[2]
    #         w = 0
    #     except OSError as err:
    #         print("image Error")
    #         w = 1
    #
    #     if q == 1 and w == 1:
    #         self.conn = sqlite3.connect("database.db")
    #         cur = self.conn.cursor()
    #         cur.execute(
    #             '''INSERT INTO el_intel (Type, Freq_kHz, Spectrum_width_kHz, Type_modulation, Pulse_duration_mcs, Follow_period, Comment, Image, img) values (?,?,?,?,?,?,?,?,?)''',
    #             (self.ui.lineEdit_Name.text(),
    #              self.ui.lineEdit_2.text(),
    #              self.ui.lineEdit_3.text(),
    #              self.ui.lineEdit_4.text(),
    #              self.ui.lineEdit_5.text(),
    #              self.ui.lineEdit_6.text(),
    #              self.ui.lineEdit_7.text(),"",""
    #              ))
    #         self.conn.commit()
    #         cur.close()
    #         self.conn.close()
    #
    #         self.findEl_intel()
    #         QMessageBox.information(self, "База данних", "Дані успішно додано!")
    #
    #     self.fileName = ('')
    #     self.fileName1 = ('')
    #
    #     if q == 0 and w == 0:
    #         self.conn = sqlite3.connect("database.db")
    #         cur = self.conn.cursor()
    #         cur.execute(
    #             '''INSERT INTO el_intel (Type, Freq_kHz, Spectrum_width_kHz, Type_modulation, Pulse_duration_mcs, Follow_period, Comment, Image, img) values (?,?,?,?,?,?,?,?,?)''',
    #             (self.ui.lineEdit_Name.text(),
    #              self.ui.lineEdit_2.text(),
    #              self.ui.lineEdit_3.text(),
    #              self.ui.lineEdit_4.text(),
    #              self.ui.lineEdit_5.text(),
    #              self.ui.lineEdit_6.text(),
    #              self.ui.lineEdit_7.text(),
    #              a2, b2))
    #         self.conn.commit()
    #         cur.close()
    #         self.conn.close()
    #
    #         self.findEl_intel()
    #         QMessageBox.information(self, "База данних", "Дані успішно додано!")
    #
    #     self.fileName = ('')
    #     self.fileName1 = ('')
    #
    #     if q == 0 and w == 1:
    #         self.conn = sqlite3.connect("database.db")
    #         cur = self.conn.cursor()
    #         cur.execute(
    #             '''INSERT INTO el_intel (Type, Freq_kHz, Spectrum_width_kHz, Type_modulation, Pulse_duration_mcs, Follow_period, Comment, Image, img) values (?,?,?,?,?,?,?,?,?)''',
    #             (self.ui.lineEdit_Name.text(),
    #              self.ui.lineEdit_2.text(),
    #              self.ui.lineEdit_3.text(),
    #              self.ui.lineEdit_4.text(),
    #              self.ui.lineEdit_5.text(),
    #              self.ui.lineEdit_6.text(),
    #              self.ui.lineEdit_7.text(),
    #              a2,""))
    #         self.conn.commit()
    #         cur.close()
    #         self.conn.close()
    #
    #         self.findEl_intel()
    #         QMessageBox.information(self, "База данних", "Дані успішно додано!")
    #
    #     self.fileName = ('')
    #     self.fileName1 = ('')
    #
    #     if q == 1 and w == 0:
    #         self.conn = sqlite3.connect("database.db")
    #         cur = self.conn.cursor()
    #         cur.execute(
    #             '''INSERT INTO el_intel (Type, Freq_kHz, Spectrum_width_kHz, Type_modulation, Pulse_duration_mcs, Follow_period, Comment, img,Image) values (?,?,?,?,?,?,?,?,?)''',
    #             (self.ui.lineEdit_Name.text(),
    #              self.ui.lineEdit_2.text(),
    #              self.ui.lineEdit_3.text(),
    #              self.ui.lineEdit_4.text(),
    #              self.ui.lineEdit_5.text(),
    #              self.ui.lineEdit_6.text(),
    #              self.ui.lineEdit_7.text(),
    #              b2,""))
    #         self.conn.commit()
    #         cur.close()
    #         self.conn.close()
    #
    #         self.findEl_intel()
    #         QMessageBox.information(self, "База данних", "Дані успішно додано!")
    #
    #     self.fileName = ('')
    #     self.fileName1 = ('')

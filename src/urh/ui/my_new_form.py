# Form implementation generated from reading ui file '1_new.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(320,390)
        # MainWindow.setMaximumSize(320, 350)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gbConnection = QtWidgets.QGroupBox(self.centralwidget)
        self.gbConnection.setGeometry(QtCore.QRect(10, 350, 301, 62))
        self.gbConnection.setObjectName("gbConnection")
        self.gbConnection.hide()

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.gbConnection)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.leIP = QtWidgets.QLineEdit(self.gbConnection)
        self.leIP.setObjectName("leIP")
        self.horizontalLayout_2.addWidget(self.leIP)
        self.bConnect = QtWidgets.QPushButton(self.gbConnection)
        self.bConnect.setCheckable(True)
        self.bConnect.setObjectName("bConnect")
        self.horizontalLayout_2.addWidget(self.bConnect)
        self.gbControls = QtWidgets.QGroupBox(self.centralwidget)
        self.gbControls.setEnabled(True)
        self.gbControls.setGeometry(QtCore.QRect(80, 260, 111, 61))
        self.gbControls.setObjectName("gbControls")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gbControls)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.chbK2 = QtWidgets.QCheckBox(self.gbControls)
        self.chbK2.setText("")
        self.chbK2.setObjectName("chbK2")
        self.gridLayout_3.addWidget(self.chbK2, 1, 1, 1, 1)
        self.lR1 = QtWidgets.QLabel(self.gbControls)
        self.lR1.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lR1.setObjectName("lR1")
        self.gridLayout_3.addWidget(self.lR1, 0, 7, 1, 1)
        self.lR5 = QtWidgets.QLabel(self.gbControls)
        self.lR5.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lR5.setObjectName("lR5")
        self.gridLayout_3.addWidget(self.lR5, 0, 3, 1, 1)
        self.chbR3 = QtWidgets.QCheckBox(self.gbControls)
        self.chbR3.setText("")
        self.chbR3.setObjectName("chbR3")
        self.gridLayout_3.addWidget(self.chbR3, 1, 5, 1, 1)
        self.chbK1 = QtWidgets.QCheckBox(self.gbControls)
        self.chbK1.setText("")
        self.chbK1.setObjectName("chbK1")
        self.gridLayout_3.addWidget(self.chbK1, 1, 2, 1, 1)
        self.chbM = QtWidgets.QCheckBox(self.gbControls)
        self.chbM.setText("")
        self.chbM.setObjectName("chbM")
        self.gridLayout_3.addWidget(self.chbM, 1, 0, 1, 1)
        self.lR2 = QtWidgets.QLabel(self.gbControls)
        self.lR2.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lR2.setObjectName("lR2")
        self.gridLayout_3.addWidget(self.lR2, 0, 6, 1, 1)
        self.lR4 = QtWidgets.QLabel(self.gbControls)
        self.lR4.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lR4.setObjectName("lR4")
        self.gridLayout_3.addWidget(self.lR4, 0, 4, 1, 1)
        self.chbR4 = QtWidgets.QCheckBox(self.gbControls)
        self.chbR4.setText("")
        self.chbR4.setObjectName("chbR4")
        self.gridLayout_3.addWidget(self.chbR4, 1, 4, 1, 1)
        self.lR3 = QtWidgets.QLabel(self.gbControls)
        self.lR3.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lR3.setObjectName("lR3")
        self.gridLayout_3.addWidget(self.lR3, 0, 5, 1, 1)
        self.chbR2 = QtWidgets.QCheckBox(self.gbControls)
        self.chbR2.setText("")
        self.chbR2.setObjectName("chbR2")
        self.gridLayout_3.addWidget(self.chbR2, 1, 6, 1, 1)
        self.chbR5 = QtWidgets.QCheckBox(self.gbControls)
        self.chbR5.setText("")
        self.chbR5.setObjectName("chbR5")
        self.gridLayout_3.addWidget(self.chbR5, 1, 3, 1, 1)
        self.chbR1 = QtWidgets.QCheckBox(self.gbControls)
        self.chbR1.setText("")
        self.chbR1.setObjectName("chbR1")
        self.gridLayout_3.addWidget(self.chbR1, 1, 7, 1, 1)
        self.lK1 = QtWidgets.QLabel(self.gbControls)
        self.lK1.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lK1.setObjectName("lK1")
        self.gridLayout_3.addWidget(self.lK1, 0, 2, 1, 1)
        self.lM = QtWidgets.QLabel(self.gbControls)
        self.lM.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lM.setObjectName("lM")
        self.gridLayout_3.addWidget(self.lM, 0, 0, 1, 1)
        self.lK2 = QtWidgets.QLabel(self.gbControls)
        self.lK2.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.lK2.setObjectName("lK2")
        self.gridLayout_3.addWidget(self.lK2, 0, 1, 1, 1)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 70, 90, 20))
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.hide()

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(10, 100, 90, 20))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.hide()
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(10, 130, 90, 20))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.hide()
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(10, 160, 90, 20))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.hide()
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(10, 190, 90, 20))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.hide()

        self.pushButton_9 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_9.setGeometry(QtCore.QRect(160, 190, 90, 20))
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.hide()

        self.gbControls1 = QtWidgets.QGroupBox(self.centralwidget)
        self.gbControls1.setEnabled(True)
        self.gbControls1.setGeometry(QtCore.QRect(10, 100, 300,75))
        self.gbControls1.setObjectName("gbControls")

        self.btnPathOpen = QtWidgets.QPushButton(self.gbControls1)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.btnPathOpen.setIcon(icon)
        self.btnPathOpen.setGeometry(QtCore.QRect(3, 25, 80, 20))
        self.btnPathOpen.setObjectName("btnPathOpen")

        self.path_textbox = QtWidgets.QLineEdit(self.gbControls1)
        self.path_textbox.setReadOnly(True)
        self.path_textbox.setObjectName("path_textbox")
        self.path_textbox.setGeometry(QtCore.QRect(3, 50, 295, 20))
# ----------
        self.gbControls_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.gbControls_3.setEnabled(True)
        self.gbControls_3.setGeometry(QtCore.QRect(20, 10, 120, 80))
        self.gbControls_3.setObjectName("gbControls_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gbControls_3)

        self.btnOffN1 = QtWidgets.QPushButton(self.centralwidget)
        self.btnOffN1.setObjectName("btnOffN1")
        self.btnOffN1.setMinimumSize(QtCore.QSize(25, 25))
        icon = QtGui.QIcon.fromTheme("system-shutdown")
        self.btnOffN1.setIconSize(QtCore.QSize(25, 25))
        self.btnOffN1.setIcon(icon)
        self.gridLayout_4.addWidget(self.btnOffN1, 0, 0, 1, 1)

        self.btnRebootN1 = QtWidgets.QPushButton(self.centralwidget)
        self.btnRebootN1.setObjectName("btnRebootN1")
        self.btnRebootN1.setMinimumSize(QtCore.QSize(25, 25))
        icon = QtGui.QIcon.fromTheme("system-reboot")
        self.btnRebootN1.setIconSize(QtCore.QSize(25, 25))
        self.btnRebootN1.setIcon(icon)
        self.gridLayout_4.addWidget(self.btnRebootN1, 0, 1, 1, 1)

#---------------------------------------------

        self.gbControls_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.gbControls_4.setEnabled(True)
        self.gbControls_4.setGeometry(QtCore.QRect(170, 10, 120, 80))
        self.gbControls_4.setObjectName("gbControls_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gbControls_4)

        self.btnOffN2 = QtWidgets.QPushButton(self.centralwidget)
        self.btnOffN2.setObjectName("btnOffN2")
        self.btnOffN2.setMinimumSize(QtCore.QSize(25, 25))
        icon = QtGui.QIcon.fromTheme("system-shutdown")
        self.btnOffN2.setIconSize(QtCore.QSize(25, 25))
        self.btnOffN2.setIcon(icon)
        self.gridLayout_4.addWidget(self.btnOffN2, 0, 0, 1, 1)

        self.btnRebootN2 = QtWidgets.QPushButton(self.centralwidget)
        self.btnRebootN2.setObjectName("btnRebootN2")
        self.btnRebootN2.setMinimumSize(QtCore.QSize(25, 25))
        icon = QtGui.QIcon.fromTheme("system-reboot")
        self.btnRebootN2.setIconSize(QtCore.QSize(25, 25))
        self.btnRebootN2.setIcon(icon)
        self.gridLayout_4.addWidget(self.btnRebootN2, 0, 1, 1, 1)

        # self.gbControls_8 = QtWidgets.QGroupBox(self.centralwidget)
        # self.gbControls_8.setEnabled(True)
        # self.gbControls_8.setGeometry(QtCore.QRect(10, 265, 300, 90))
        # self.gbControls_8.setObjectName("gbControls_8")
        #
        # self.gridLayout_5 = QtWidgets.QGridLayout(self.gbControls_8)
        # self.gridLayout_5.setObjectName("gridLayout_5")
#-------------------- N E T W O R K ------------------------------------

        self.gbControls_9 = QtWidgets.QGroupBox(self.centralwidget)
        self.gbControls_9.setEnabled(True)
        self.gbControls_9.setGeometry(QtCore.QRect(10, 260, 300, 100))
        self.gbControls_9.setObjectName("gbControls_8")

        self.gridLayout_6 = QtWidgets.QGridLayout(self.gbControls_9)
        self.gridLayout_6.setObjectName("gridLayout_5")


        self.network_RPK = QtWidgets.QLabel(self.centralwidget)
        self.network_RPK.setObjectName("network_RPK")
        self.network_RPK.setStyleSheet("background-color: grey")
        self.network_RPK.setGeometry(QtCore.QRect(25, 290, 15, 15))


        self.network_Nuke = QtWidgets.QLabel(self.centralwidget)
        self.network_Nuke.setObjectName("network_Nuke")
        self.network_Nuke.setStyleSheet("background-color: grey")
        self.network_Nuke.setGeometry(QtCore.QRect(25, 310, 15, 15))


        self.network_Nuke2 = QtWidgets.QLabel(self.centralwidget)
        self.network_Nuke2.setObjectName("network_Nuke2")
        self.network_Nuke2.setStyleSheet("background-color: grey")
        self.network_Nuke2.setGeometry(QtCore.QRect(25, 330, 15, 15))

        self.network_RPK_label = QtWidgets.QLabel(self.centralwidget)
        self.network_RPK_label.setObjectName("network_RPK_label")
        self.network_RPK_label.setGeometry(QtCore.QRect(60, 290, 200, 15))

        self.network_Nuke_label = QtWidgets.QLabel(self.centralwidget)
        self.network_Nuke_label.setObjectName("network_Nuke_label")
        self.network_Nuke_label.setGeometry(QtCore.QRect(60, 310, 200, 15))

        self.network_Nuke2_label = QtWidgets.QLabel(self.centralwidget)
        self.network_Nuke2_label.setObjectName("network_Nuke2_label")
        self.network_Nuke2_label.setGeometry(QtCore.QRect(60, 330, 200, 15))



        self.gbControls2 = QtWidgets.QGroupBox(self.centralwidget)
        self.gbControls2.setEnabled(True)
        self.gbControls2.setGeometry(QtCore.QRect(10, 180, 300, 75))
        self.gbControls2.setObjectName("gbControls2")

        self.btnPathIQ = QtWidgets.QPushButton(self.gbControls2)
        icon = QtGui.QIcon.fromTheme("document-open")
        self.btnPathIQ.setIcon(icon)
        self.btnPathIQ.setGeometry(QtCore.QRect(3, 25, 80, 20))
        self.btnPathIQ.setObjectName("btnPathIQ")

        self.path_textbox_bd = QtWidgets.QLineEdit(self.gbControls2)
        self.path_textbox_bd.setObjectName("path_textbox_bd")
        self.path_textbox_bd.setReadOnly(True)
        self.path_textbox_bd.setGeometry(QtCore.QRect(3, 50, 295, 20))
        #-----------

        # self.path_where_record_signals = QtWidgets.QLabel(self.centralwidget)
        # self.path_where_record_signals.setObjectName("path_where_record_signals")
        # self.path_where_record_signals.setGeometry(QtCore.QRect(10, 365, 200, 15))
        #----------


        self.gbControls.raise_()
        self.gbControls.hide()
        self.gbConnection.raise_()
        self.pushButton_2.raise_()
        self.pushButton_3.raise_()
        self.pushButton_4.raise_()
        self.pushButton_5.raise_()
        self.pushButton_6.raise_()
        # self.pushButton_7.raise_()
        # self.pushButton_8.raise_()
        self.pushButton_9.raise_()
        self.btnPathOpen.raise_()

        # self.gbControls_2.raise_()
        self.gbControls1.raise_()
        # MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Налаштування"))
        self.gbConnection.setTitle(_translate("MainWindow", "Параметри з\'єднання з РКП"))
        self.leIP.setInputMask(_translate("MainWindow", "000.000.0.00:0000;_"))
        self.leIP.setText(_translate("MainWindow", "192.168.0.10:1032"))
        self.bConnect.setText(_translate("MainWindow", "З\'єднати"))
        self.gbControls.setTitle(_translate("MainWindow", "Управління"))
        self.chbK2.setToolTip(_translate("MainWindow", "Включення живлення каналу №2 конвертора"))
        self.lR1.setText(_translate("MainWindow", "R1"))
        self.lR5.setText(_translate("MainWindow", "R5"))
        self.chbR3.setToolTip(_translate("MainWindow", "Включення живлення приймача №3"))
        self.chbK1.setToolTip(_translate("MainWindow", "Включення живлення каналу №1 конвертора"))
        self.chbM.setToolTip(_translate("MainWindow", "Переключення каналів конвертора"))
        self.lR2.setText(_translate("MainWindow", "R2"))
        self.lR4.setText(_translate("MainWindow", "R4"))
        self.chbR4.setToolTip(_translate("MainWindow", "Включення живлення приймача №4"))
        self.lR3.setText(_translate("MainWindow", "R3"))
        self.chbR2.setToolTip(_translate("MainWindow", "Включення живлення приймача №2"))
        self.chbR5.setToolTip(_translate("MainWindow", "Включення живлення приймача №5"))
        self.chbR1.setToolTip(_translate("MainWindow", "Включення живлення приймача №1"))
        self.lK1.setText(_translate("MainWindow", "K1"))
        self.lM.setText(_translate("MainWindow", " M"))
        self.lK2.setText(_translate("MainWindow", "K2"))

        self.pushButton_2.setText(_translate("MainWindow", "Приймач 1"))
        self.pushButton_3.setText(_translate("MainWindow", "Приймач 2"))

        self.pushButton_4.setText(_translate("MainWindow", "Приймач 3"))
        self.pushButton_5.setText(_translate("MainWindow", "Приймач 4"))
        self.pushButton_6.setText(_translate("MainWindow", "Приймач 5"))

        self.pushButton_9.setText(_translate("MainWindow", "1/2 канал"))
        self.gbControls1.setTitle(_translate("MainWindow", "Шлях збереження сесії та файлів"))
        self.btnPathOpen.setText(_translate("MainWindow", "  Огляд"))

        self.btnPathIQ.setText(_translate("MainWindow", "  Огляд"))
        self.btnPathIQ.setToolTip(_translate("MainWindow", "Вибір каталогу для збереження IQ відліків"))

        self.btnPathOpen.setToolTip(_translate("MainWindow", "Вибір каталогу для збереження\n    записаних сигналів та сессії"))


        self.gbControls_3.setTitle(_translate("MainWindow", "Живлення АРМ 1"))
        self.gbControls_4.setTitle(_translate("MainWindow", "Живлення АРМ 2"))

        self.btnOffN1.setToolTip(_translate("MainWindow", "Вимкнення живлення на АРМ 1"))
        self.btnOffN2.setToolTip(_translate("MainWindow", "Вимкнення живлення на АРМ 2"))

        self.btnRebootN2.setToolTip(_translate("MainWindow", "Перезавантаження АРМ 2"))
        self.btnRebootN1.setToolTip(_translate("MainWindow", "Перезавантаження АРМ 1"))

        self.gbControls_9.setTitle(_translate("MainWindow", "Статус мережі"))

        self.network_RPK_label.setText(_translate("MainWindow", "Зв'язок з РКП"))
        self.network_Nuke_label.setText(_translate("MainWindow", "Зв'язок з АРМ 1"))
        self.network_Nuke2_label.setText(_translate("MainWindow", "Зв'язок з АРМ 2"))

        self.gbControls2.setTitle(_translate("MainWindow", "Шлях реєстрації IQ відліків"))

        # self.path_where_record_signals.setText(_translate("MainWindow", "1/2 канал"))


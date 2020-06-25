from PyQt5 import QtCore, QtGui, QtWidgets
import sys, random
from PyQt5.Qt import *
from PyQt5.QtGui import QPainter
# from PyQt5.QtChart import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

class MonitorTab_Dialog(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1550, 750)
        Form.setMinimumSize(QtCore.QSize(1550, 750))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")


        self.chart1 = QtChart.QChart()
        self.chart1.setBackgroundVisible(False)
        self.chartView = QtChart.QChartView(self.chart1)
        self.gridLayout.addWidget(self.chartView, 0, 0, 1, 1)

        self.chart2 = QtChart.QChart()
        self.chart2.setBackgroundVisible(False)
        self.chartView2 = QtChart.QChartView(self.chart2)
        self.gridLayout.addWidget(self.chartView2, 0, 1, 1, 1)

        self.chart3 = QtChart.QChart()
        self.chart3.setBackgroundVisible(False)
        self.chartView3 = QtChart.QChartView(self.chart3)
        self.gridLayout.addWidget(self.chartView3, 1, 0, 1, 1)

        self.chart4 = QtChart.QChart()
        self.chart4.setBackgroundVisible(False)
        self.chartView4 = QtChart.QChartView(self.chart4)
        self.gridLayout.addWidget(self.chartView4, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)





    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Програмний додаток ЕЗ ВЕКТОР"))


class MonitorTab(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1550, 750)

        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
# -------------------
        self.chart1 = QtChart.QChart()
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.setBackgroundVisible(False)
        self.chartView = QtChart.QChartView(self.chart1)
        self.chart1.legend().setVisible(False)
        self.gridLayout.addWidget(self.chartView, 1, 0, 1, 1)

        self.chart2 = QtChart.QChart()
        self.chart2.setMargins(QMargins(0, 0, 0, 0))
        self.chart2.setBackgroundVisible(False)
        self.chart2.legend().setVisible(False)
        self.chartView2 = QtChart.QChartView(self.chart2)
        self.gridLayout.addWidget(self.chartView2, 3, 0, 1, 1)

        self.chart3 = QtChart.QChart()
        self.chart3.setMargins(QMargins(0, 0, 0, 0))
        self.chart3.setBackgroundVisible(False)
        self.chart3.legend().setVisible(False)
        self.chartView3 = QtChart.QChartView(self.chart3)
        self.gridLayout.addWidget(self.chartView3, 5, 0, 1, 1)

        self.chart4 = QtChart.QChart()
        self.chart4.setMargins(QMargins(0, 0, 0, 0))
        self.chart4.setBackgroundVisible(False)
        self.chart4.legend().setVisible(False)
        self.chartView4 = QtChart.QChartView(self.chart4)
        self.gridLayout.addWidget(self.chartView4, 7, 0, 1, 1)
#-------------------
        self.label = QtWidgets.QLabel()
        self.label.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.label_GAIN = QtWidgets.QLabel('15')
        self.label_GAIN.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_GAIN.setFont(font)
        self.label_GAIN.setAlignment(QtCore.Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_GAIN, 0, 1, 1, 2)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)




        self.label2 = QtWidgets.QLabel()
        self.label2.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label2.setFont(font)
        self.label2.setAlignment(QtCore.Qt.AlignCenter)

        self.label_2GAIN = QtWidgets.QLabel('15')
        self.label_2GAIN.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2GAIN.setFont(font)
        self.label_2GAIN.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_2GAIN, 2, 1, 1, 2)
        self.gridLayout.addWidget(self.label2, 2, 0, 1, 2)


        self.label3 = QtWidgets.QLabel()
        self.label3.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label3.setFont(font)
        self.label3.setAlignment(QtCore.Qt.AlignCenter)

        self.label_3GAIN = QtWidgets.QLabel('15')
        self.label_3GAIN.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3GAIN.setFont(font)
        self.label_3GAIN.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_3GAIN, 4, 1, 1, 2)

        self.gridLayout.addWidget(self.label3, 4, 0, 1, 2)

        self.label4 = QtWidgets.QLabel()
        self.label4.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label4.setFont(font)
        self.label4.setAlignment(QtCore.Qt.AlignCenter)

        self.label_4GAIN = QtWidgets.QLabel('15')
        self.label_4GAIN.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4GAIN.setFont(font)
        self.label_4GAIN.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_4GAIN, 6, 1, 1, 2)
        self.gridLayout.addWidget(self.label4, 6, 0, 1, 2)
# -------------------

        self.verticalSlider = QtWidgets.QSlider()
        self.verticalSlider.setSliderPosition(15)
        self.verticalSlider.setMaximum(40)
        self.verticalSlider.setMinimum(10)
        self.verticalSlider.setSingleStep(1)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setEnabled(False)
        # self.verticalSlider.setTickInterval(10)
        # self.verticalSlider.setTracking(False)
        self.gridLayout.addWidget(self.verticalSlider, 1, 1, 1, 1)

        self.verticalSlider2 = QtWidgets.QSlider()
        self.verticalSlider2.setSingleStep(1)
        self.verticalSlider2.setSliderPosition(15)
        self.verticalSlider2.setMaximum(40)
        self.verticalSlider2.setMinimum(10)
        self.verticalSlider2.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider2.setObjectName("verticalSlider")
        self.verticalSlider2.setEnabled(False)
        self.gridLayout.addWidget(self.verticalSlider2, 3, 1, 1, 1)

        self.verticalSlider3 = QtWidgets.QSlider()
        # self.verticalSlider3.setTickInterval(10)
        self.verticalSlider3.setSingleStep(1)
        self.verticalSlider3.setSliderPosition(15)
        self.verticalSlider3.setMaximum(40)
        self.verticalSlider3.setMinimum(10)
        self.verticalSlider3.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider3.setObjectName("verticalSlider")
        self.verticalSlider3.setEnabled(False)
        self.gridLayout.addWidget(self.verticalSlider3, 5, 1, 1, 1)

        self.verticalSlider4 = QtWidgets.QSlider()
        self.verticalSlider4.setSingleStep(1)
        self.verticalSlider4.setSliderPosition(15)
        self.verticalSlider4.setMaximum(40)
        self.verticalSlider4.setMinimum(10)
        self.verticalSlider4.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider4.setObjectName("verticalSlider")
        self.verticalSlider4.setEnabled(False)
        self.gridLayout.addWidget(self.verticalSlider4, 7, 1, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "MyForm"))
        self.label.setText(_translate("Form", "4-5 ГГц"))
        self.label2.setText(_translate("Form", "5-6 ГГц"))
        self.label3.setText(_translate("Form", "6-7 ГГц"))
        self.label4.setText(_translate("Form", "7-8 ГГц"))


        self.verticalSlider.setToolTip(_translate("Form",  "Встановлення підсилення\n           на 1 приймач"))
        self.verticalSlider2.setToolTip(_translate("Form", "Встановлення підсилення\n           на 2 приймач"))
        self.verticalSlider3.setToolTip(_translate("Form", "Встановлення підсилення\n           на 3 приймач"))
        self.verticalSlider4.setToolTip(_translate("Form", "Встановлення підсилення\n           на 4 приймач"))




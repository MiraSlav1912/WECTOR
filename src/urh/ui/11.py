# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitl11111ed.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtChart import QChart, QChartView
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QFont


class MonitorTab(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1550, 750)


        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")


        self.chart4 = QChart()
        self.chart4.setMargins(QMargins(0, 0, 0, 0))
        self.chart4.setBackgroundVisible(False)
        self.chart4.legend().setVisible(False)
        self.chartView4 = QChartView(self.chart4)
        self.gridLayout.addWidget(self.chartView4, 7, 0, 1, 1)

        self.chart3 = QChart()
        self.chart3.setMargins(QMargins(0, 0, 0, 0))
        self.chart3.setBackgroundVisible(False)
        self.chart3.legend().setVisible(False)
        self.chartView3 = QChartView(self.chart3)
        self.gridLayout.addWidget(self.chartView3, 5, 0, 1, 1)

        self.chart2 = QChart()
        self.chart2.setMargins(QMargins(0, 0, 0, 0))
        self.chart2.setBackgroundVisible(False)
        self.chart2.legend().setVisible(False)
        self.chartView2 = QChartView(self.chart2)
        self.gridLayout.addWidget(self.chartView2, 3, 0, 1, 1)


        self.chart1 = QChart()
        self.chart1.setMargins(QMargins(0, 0, 0, 0))
        self.chart1.setBackgroundVisible(False)
        self.chartView = QChartView(self.chart1)
        self.chart1.legend().setVisible(False)
        self.gridLayout.addWidget(self.chartView, 1, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "MyForm"))


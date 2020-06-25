from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QEvent, QRect
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPainter, QPen, QBrush

from urh.ui.painting.GridScene import GridScene
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView
#-------------
from PyQt5.QtGui import QColor
#------------
class LiveGraphicView(ZoomableGraphicView):
    my_freq_wheel = pyqtSignal(float)
    my_freq_to_main = pyqtSignal(list)
    freq_clicked = pyqtSignal(float)
    wheel_event_triggered = pyqtSignal(QWheelEvent)
    #-----
    my_wheel_event_freq = pyqtSignal(int)
    #-----

    def __init__(self, parent=None):
        super().__init__(parent)
        self.capturing_data = True
        self.setMouseTracking(True)
        self.tickk = [0,[]]
        self.d = False
        self.Clicable = True

        self.status_k_in_LiveGraphicView = 0
        self.my_select_freq = []
    def wheelEvent(self, event: QWheelEvent):
        #------
        if self.Clicable:
            a = event.angleDelta().y()
            self.my_wheel_event_freq.emit(a)
            #------
            self.wheel_event_triggered.emit(event)
            if event.globalPos:

                self.scene().get_freq_for_pos(int(self.mapToScene(event.pos()).x()))
            #     self.my_freq_wheel.emit(freq)
            if self.capturing_data:
                return

            super().wheelEvent(event)
    def leaveEvent(self, event: QEvent):
        super().leaveEvent(event)
        if self.Clicable:
            if isinstance(self.scene(), GridScene):
                self.scene().clear_frequency_marker()


    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.Clicable:
            if isinstance(self.scene(), GridScene):
                x = int(self.mapToScene(event.pos()).x())

                freq = self.scene().get_freq_for_pos(x)
                # !!!!!!!!!
                if freq != None:
                    freq = 6800e6 + self.status_k_in_LiveGraphicView - freq
                    # freq = (2800e6 - freq)*2 + 4000e6
                # rint(self.status_k_in_LiveGraphicView)
                self.scene().draw_frequency_marker(x, freq)
                # -------------

                if self.d == True:
                    if abs(self.x - x) > 4095:
                        self.scene().my_draw(self.x, x, freq, QColor(7, 188, 70, 100))
                    else:
                        self.scene().my_draw(self.x, x, freq, QColor(188, 47, 70, 100))

                    if self.x - x < 0:
                        self.scene().my_line(self.x + abs((self.x - x) / 2), freq)
                    else:
                        self.scene().my_line(x + (self.x - x) / 2, freq)



    def mousePressEvent(self, event: QMouseEvent):
        if self.Clicable:

            if isinstance(self.scene(), GridScene):
                freq = self.scene().get_freq_for_pos(int(self.mapToScene(event.pos()).x()))
                if freq is not None:
                    self.freq_clicked.emit(freq)

            x = int(self.mapToScene(event.pos()).x())

            if event.button() == QtCore.Qt.LeftButton:
                if self.d :
                    self.d = False
                    print(self.x,x,abs(self.x - x))
                else:
                    self.d = True
                    self.x = x

                # and
                if self.my_select_freq.__len__() == 0:
                    self.my_select_freq.append(freq)
                elif self.my_select_freq.__len__() ==1 and abs(self.x - x) >= 4095:
                    self.my_select_freq.append(freq)
                    self.my_freq_to_main.emit(self.my_select_freq)
                    self.my_select_freq = []



                # print(self.my_select_freq)

            if event.button() == QtCore.Qt.MidButton:
                self.d = False
                self.my_select_freq = []
                self.scene().my_clear()



        # self.scene().addRect(x-10,self.sceneRect().y()+1.5,2000,self.sceneRect().y()+5.5,QPen(QColor(150, 50, 50, 50) )  )

    def update(self, *__args):
        try:
            super().update(*__args)
            super().show_full_scene()
        except RuntimeError:
            pass

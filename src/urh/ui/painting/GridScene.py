import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QRectF, QLineF,QMimeData,QPoint,Qt
from PyQt5.QtGui import QPainter, QFont, QFontMetrics, QPen, QTransform, QBrush

from urh import constants
from urh.ui.painting.HorizontalSelection import HorizontalSelection
from urh.ui.painting.ZoomableScene import ZoomableScene
from urh.util import util
from urh.util.Formatter import Formatter

from PyQt5.QtGui import QIcon, QDrag, QPixmap, QRegion, QDropEvent, QTextCursor, QContextMenuEvent, \
    QResizeEvent, QColor

class GridScene(ZoomableScene):
    def __init__(self, parent=None):
        self.draw_grid = False
        self.font_metrics = QFontMetrics(QFont())
        self.center_freq = 588.93e6
        #self.center_freq = 433.92e6
        self.frequencies = []
        self.frequency_marker = None

        super().__init__(parent)
        self.setSceneRect(0,0,10,10)
        #-----------
        self.status_k = 0
        self.ttick = []
        self.my_marker = []
        self.x = None
        self.y = None
    def drawBackground(self, painter: QPainter, rect: QRectF):

        # freqs = np.fft.fftfreq(len(w), 1 / self.sample_rate)
        if self.draw_grid and len(self.frequencies) > 0:
            painter.setPen(QPen(painter.pen().color(), 0))
            parent_width = self.parent().width() if hasattr(self.parent(), "width") else 750
            view_rect = self.parent().view_rect() if hasattr(self.parent(), "view_rect") else rect

            font_width = self.font_metrics.width(Formatter.big_value_with_suffix(self.center_freq) + "   ")
            x_grid_size = int(view_rect.width() / parent_width * font_width)
            # x_grid_size = int(0.1 * view_rect.width()) if 0.1 * view_rect.width() > 1 else 1
            y_grid_size = 1
            x_mid = np.where(self.frequencies == 0)[0]
            x_mid = int(x_mid[0]) if len(x_mid) > 0 else 0

            left = int(rect.left()) - (int(rect.left()) % x_grid_size)
            left = left if left > 0 else 0

            top = rect.top() - (rect.top() % y_grid_size)
            bottom = rect.bottom() - (rect.bottom() % y_grid_size)
            right_border = int(rect.right()) if rect.right() < len(self.frequencies) else len(self.frequencies)

            x_range = list(range(x_mid, left, -x_grid_size)) + list(range(x_mid, right_border, x_grid_size))
            lines = [QLineF(x, rect.top(), x, bottom) for x in x_range] \
                    + [QLineF(rect.left(), y, rect.right(), y) for y in np.arange(top, bottom, y_grid_size)]

            painter.drawLines(lines)
            scale_x, scale_y = util.calc_x_y_scale(rect, self.parent())

            painter.scale(scale_x, scale_y)
            counter = -1  # Counter for Label for every second line

            for x in x_range:
                freq = self.frequencies[x]
                counter += 1

                if freq != 0 and (counter % 2 != 0): # Label for every second line
                    continue

                if freq != 0:
                    prefix = "+" if freq > 0 else ""
                    value = prefix+Formatter.big_value_with_suffix(freq, 2)
                else:
                    counter = 0
                    value = Formatter.big_value_with_suffix(6800e6 - self.center_freq + self.status_k)
                font_width = self.font_metrics.width(value)
                painter.drawText(x / scale_x - font_width / 2, bottom / scale_y, value)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.drag_started.emit(self.mapToParent(event.pos()))
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setText("Move Signal")
            pixmap = QPixmap(self.rect().size())
            self.render(pixmap, QPoint(), QRegion(self.rect()))
            drag.setPixmap(pixmap)
            drag.setMimeData(mimeData)
            drag.exec_()

    def my_line(self,x_pos,frequency):
        if frequency is None:
            self.clear_frequency_marker()
            return

        pen = QPen(QColor.fromRgb(255, 255, 0,100),100)
        y1 = self.sceneRect().y()
        y2 = self.sceneRect().y() + self.sceneRect().height()

        self.my_marker.append(self.addLine(x_pos, y1, x_pos, y2, pen))
        if self.my_marker.__len__() >=2:
            [self.removeItem(i) for i in self.my_marker[:-1]]
            self.my_marker = [self.my_marker[-1]]

    def draw_frequency_marker(self, x_pos, frequency):

        if frequency is None:
            self.clear_frequency_marker()
            return

        y1 = self.sceneRect().y()
        y2 = self.sceneRect().y() + self.sceneRect().height()

        if self.frequency_marker is None:
            pen = QPen(constants.LINECOLOR, 0)

            self.frequency_marker = [None, None]

            self.frequency_marker[0] = self.addLine(x_pos, y1, x_pos, y2, pen)
            self.frequency_marker[1] = self.addSimpleText("")
            self.frequency_marker[1].setBrush(QBrush(constants.LINECOLOR))
            font = QFont()
            font.setBold(True)
            font.setPointSize(int(font.pointSize() * 1.25)+1)
            self.frequency_marker[1].setFont(font)

        self.frequency_marker[0].setLine(x_pos, y1, x_pos, y2)
        scale_x, scale_y = util.calc_x_y_scale(self.sceneRect(), self.parent())
        self.frequency_marker[1].setTransform(QTransform.fromScale(scale_x, scale_y), False)
        self.frequency_marker[1].setText("Частота " + Formatter.big_value_with_suffix(frequency, decimals=3)+"Гц")
        font_metric = QFontMetrics(self.frequency_marker[1].font())
        text_width = font_metric.width("Частота") * scale_x
        text_width += (font_metric.width(" ") * scale_x) / 2
        self.frequency_marker[1].setPos(x_pos-text_width, 0.95*y1)

    def my_draw(self,x1,x2,frequency,color):
        if frequency is None:
            return

        self.ttick.append(self.addRect(x1,-4.5,x2-x1,6.5,QPen(color, 6.5)))
        if self.ttick.__len__() >=2:
            [self.removeItem(i) for i in self.ttick[:-1]]
            self.ttick = [self.ttick[-1]]

    def clear_frequency_marker(self):
        if self.frequency_marker is not None:
            self.removeItem(self.frequency_marker[0])
            self.removeItem(self.frequency_marker[1])
        self.frequency_marker = None

    def my_clear(self):
        if self.ttick.__len__() != 0 and self.my_marker.__len__() !=0:
            self.removeItem(self.ttick[0])
            self.ttick = []
            self.removeItem(self.my_marker[0])
            self.my_marker = []

    def get_freq_for_pos(self, x: int) ->  float:
        try:
            f = self.frequencies[x]

        except IndexError:
            return None

        return self.center_freq - f


    def clear(self):
        self.clear_frequency_marker()

        super().clear()

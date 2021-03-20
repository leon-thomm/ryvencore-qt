# import math

from PySide2.QtCore import QRectF, QPointF
from PySide2.QtGui import QPainter, QColor, QRadialGradient, QPainterPath, QPen, Qt
from PySide2.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from .tools import sqrt
from .tools import pythagoras


class ConnectionItem(QGraphicsItem):
    """The GUI representative for a connection. The classes ExecConnectionItem and DataConnectionItem will be ready
    for reimplementation later, so users can add GUI for the enhancements of DataConnection and ExecConnection,
    like input fields for weights."""

    def __init__(self, connection, session_design):
        super().__init__()

        self.connection = connection

        out = self.connection.out
        inp = self.connection.inp
        out_node = out.node
        inp_node = inp.node
        self.out_item = out_node.port_item(out)
        self.inp_item = inp_node.port_item(inp)

        # self.out = self.connection.out
        # self.out_item = self.connection.out.node.port_item()
        # self.inp = self.connection.inp

        # self.type_ = type_
        self.session_design = session_design
        self.changed = False
        self.path: QPainterPath = None
        self.gradient = None

        self.recompute()

    def boundingRect(self):
        op = self.out_pos()
        ip = self.inp_pos()
        rect = QRectF(
            0 if op.x() < ip.x() else (ip.x()-op.x()),
            0 if op.y() < ip.y() else (ip.y()-op.y()),
            abs(ip.x()-op.x()),
            abs(ip.y()-op.y())
        )
        return rect


    def recompute(self):
        """Updated scene position and recomputes the path"""

        self.setPos(self.out_pos())
        self.changed = True
        self.update()
    
    
    def out_pos(self) -> QPointF:
        """The current global scene position of the pin of the output port"""

        return self.out_item.pin.get_scene_center_pos()
    
    def inp_pos(self) -> QPointF:
        """The current global scene position of the pin of the input port"""

        return self.inp_item.pin.get_scene_center_pos()

    @staticmethod
    def dist(p1: QPointF, p2: QPointF) -> float:
        """Returns the diagonal distance between the points using pythagoras"""

        dx = p2.x()-p1.x()
        dy = p2.y()-p1.y()
        return sqrt((dx**2) + (dy**2))


    @staticmethod
    def connection_path(p1: QPointF, p2: QPointF) -> QPainterPath:
        """Returns the painter path for drawing the connection, using the usual cubic connection path by default"""

        return default_cubic_connection_path(p1, p2)



class ExecConnectionItem(ConnectionItem):


    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=...) -> None:

        theme = self.session_design.flow_theme

        pen = QPen(theme.exec_conn_color, theme.exec_conn_width)
        pen.setStyle(theme.exec_conn_pen_style)
        pen.setCapStyle(Qt.RoundCap)

        c = pen.color()

        # highlight hovered connections
        if self.out_item.pin.hovered or self.inp_item.pin.hovered:
            c = QColor('#c5c5c5')
            pen.setWidth(theme.exec_conn_width*2)

        if self.changed or not self.path:
            self.changed = False

            self.path = self.connection_path(
                QPointF(0, 0),
                self.inp_pos()-self.scenePos()
            )

            w = self.path.boundingRect().width()
            h = self.path.boundingRect().height()
            self.gradient = QRadialGradient(self.path.boundingRect().center(),
                                            pythagoras(w, h) / 2)

            c_r = c.red()
            c_g = c.green()
            c_b = c.blue()

            # this offset will be 1 if inp.x >> out.x and 0 if inp.x < out.x
            # hence, no fade for the gradient if the connection goes backwards
            offset_mult: float = max(
                0,
                min(
                    (self.inp_pos().x() - self.out_pos().x())/200,
                    1
                )
            )

            # and if the input is very far away from the output, decrease the gradient fade so the connection
            # doesn't fully disappear at the ends and stays visible
            if self.inp_pos().x() > self.out_pos().x():
                offset_mult = min(
                    offset_mult,
                    2000/(self.dist(self.inp_pos(), self.out_pos()))
                )
                # zucker.

            self.gradient.setColorAt(0.0, QColor(c_r, c_g, c_b, 255))
            self.gradient.setColorAt(0.75, QColor(c_r, c_g, c_b, 255 - round(55 * offset_mult)))
            self.gradient.setColorAt(0.95, QColor(c_r, c_g, c_b, 255 - round(255 * offset_mult)))

        pen.setBrush(self.gradient)
        painter.setPen(pen)

        painter.drawPath(self.path)


class DataConnectionItem(ConnectionItem):

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=...) -> None:

        theme = self.session_design.flow_theme

        pen = QPen(theme.data_conn_color, theme.data_conn_width)
        pen.setStyle(theme.data_conn_pen_style)
        pen.setCapStyle(Qt.RoundCap)

        c = pen.color()

        # highlight hovered connections
        if self.out_item.pin.hovered or self.inp_item.pin.hovered:
            c = QColor('#c5c5c5')
            pen.setWidth(theme.exec_conn_width*2)


        if self.changed or not self.path:
            self.changed = False

            self.path = self.connection_path(
                QPointF(0, 0),
                self.inp_pos() - self.scenePos()
            )

            w = self.path.boundingRect().width()
            h = self.path.boundingRect().height()
            self.gradient = QRadialGradient(self.path.boundingRect().center(),
                                            pythagoras(w, h) / 2)

            c_r = c.red()
            c_g = c.green()
            c_b = c.blue()

            # this offset will be 1 if inp.x >> out.x and 0 if inp.x < out.x
            # hence, no fade for the gradient if the connection goes backwards
            offset_mult: float = max(
                0,
                min(
                    (self.inp_pos().x() - self.out_pos().x())/200,
                    1
                )
            )

            # and if the input is very far away from the output, decrease the gradient fade so the connection
            # doesn't fully disappear at the ends and stays visible
            if self.inp_pos().x() > self.out_pos().x():
                offset_mult = min(
                    offset_mult,
                    2000/(self.dist(self.inp_pos(), self.out_pos()))
                )
                # zucker.

            self.gradient.setColorAt(0.0, QColor(c_r, c_g, c_b, 255))
            self.gradient.setColorAt(0.75, QColor(c_r, c_g, c_b, 255 - round(55 * offset_mult)))
            self.gradient.setColorAt(0.95, QColor(c_r, c_g, c_b, 255 - round(255 * offset_mult)))

        pen.setBrush(self.gradient)
        painter.setPen(pen)
        painter.drawPath(self.path)


def default_cubic_connection_path(p1: QPointF, p2: QPointF):
    """Returns the nice looking QPainterPath from p1 to p2"""

    path = QPainterPath()

    path.moveTo(p1)

    dx = p2.x() - p1.x()
    adx = abs(dx)
    dy = p2.y() - p1.y()
    ady = abs(dy)
    distance = sqrt((dx ** 2) + (dy ** 2))
    x1, y1 = p1.x(), p1.y()
    x2, y2 = p2.x(), p2.y()

    if ((x1 < x2 - 30) or distance < 100) and (x1 < x2):
        # STANDARD FORWARD
        path.cubicTo(x1 + ((x2 - x1) / 2), y1,
                     x1 + ((x2 - x1) / 2), y2,
                     x2, y2)
    elif x2 < x1 - 100 and adx > ady * 2:
        # STRONG BACKWARDS
        path.cubicTo(x1 + 100 + (x1 - x2) / 10, y1,
                     x1 + 100 + (x1 - x2) / 10, y1 + (dy / 2),
                     x1 + (dx / 2), y1 + (dy / 2))
        path.cubicTo(x2 - 100 - (x1 - x2) / 10, y2 - (dy / 2),
                     x2 - 100 - (x1 - x2) / 10, y2,
                     x2, y2)
    else:
        # STANDARD BACKWARDS
        path.cubicTo(x1 + 100 + (x1 - x2) / 3, y1,
                     x2 - 100 - (x1 - x2) / 3, y2,
                     x2, y2)
    
    return path

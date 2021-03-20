from PySide2.QtCore import QRectF, QPointF, QSizeF, Property
from PySide2.QtGui import QFont, QFontMetricsF, QColor
from PySide2.QtWidgets import QGraphicsWidget, QGraphicsLayoutItem, QGraphicsItem

from .tools import get_longest_line


class TitleLabel(QGraphicsWidget):

    # TODO: add NodeItem renaming on double click

    def __init__(self, node, node_item):
        super(TitleLabel, self).__init__(parent=node_item)

        self.setGraphicsItem(self)

        self.node = node
        self.node_item = node_item
        self.title_str = self.node.title
        font = QFont('Poppins', 15) if self.node.style == 'extended' else \
            QFont('K2D', 20, QFont.Bold, True)  # should be quite similar to every specific font chosen by the painter
        fm = QFontMetricsF(font)

        # approximately!
        self.width = fm.width(get_longest_line(self.title_str)+'___')
        self.height = fm.height() * 0.7 * (self.title_str.count('\n') + 1)

        self.color = QColor(30, 43, 48)
        self.pen_width = 1.5
        self.hovering = False  # whether the mouse is hovering over the parent NI (!)

        # # Design.flow_theme_changed.connect(self.theme_changed)
        # self.update_design()

    def boundingRect(self):
        return QRectF(QPointF(0, 0), self.geometry().size())

    def setGeometry(self, rect):
        self.prepareGeometryChange()
        QGraphicsLayoutItem.setGeometry(self, rect)
        self.setPos(rect.topLeft())

    def sizeHint(self, which, constraint=...):
        return QSizeF(self.width, self.height)

    def paint(self, painter, option, widget=None):

        self.node_item.session_design.flow_theme.paint_NI_title_label(
            self.node,
            painter, option, self.hovering,
            self.design_style(), self.title_str, self.node_item.color,
            self.boundingRect()
        )

    def design_style(self):
        return self.node.style

    def set_NI_hover_state(self, hovering: bool):
        self.hovering = hovering
        # self.update_design()
        self.update()

    # ANIMATION STUFF
    def get_color(self):
        return self.color

    def set_color(self, val):
        self.color = val
        QGraphicsItem.update(self)

    p_color = Property(QColor, get_color, set_color)
from qtpy.QtWidgets import QLineEdit, QWidget, QLabel, QGridLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QStyleOption, QStyle
from qtpy.QtGui import QFont, QPainter, QColor
from qtpy.QtCore import Signal


class NodeWidget(QWidget):

    chosen = Signal()
    custom_focused_from_inside = Signal()

    def __init__(self, parent, node):
        super(NodeWidget, self).__init__(parent)

        self.custom_focused = False
        self.node = node

        # UI
        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self_ = self
        class NameLabel(QLineEdit):
            def __init__(self, text):
                super().__init__(text)

                self.setReadOnly(True)
                self.setFont(QFont('Poppins', 10))
            def mouseMoveEvent(self, ev):
                self_.custom_focused_from_inside.emit()
                ev.ignore()
            def mousePressEvent(self, ev):
                ev.ignore()
            def mouseReleaseEvent(self, ev):
                ev.ignore()

        name_label = NameLabel(node.title)

        type_layout = QHBoxLayout()

        type_label = QLabel(node.type_)
        type_label.setFont(QFont('Segoe UI', 8, italic=True))
        # type_label.setStyleSheet('color: white;')

        main_layout.addWidget(name_label, 0, 0)
        main_layout.addWidget(type_label, 0, 1)

        self.setLayout(main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(250)

        self.setToolTip(node.__doc__)
        self.update_stylesheet()


    def mousePressEvent(self, event):
        self.custom_focused_from_inside.emit()

    def mouseReleaseEvent(self, event):
        if self.geometry().contains(self.mapToParent(event.pos())):
            self.chosen.emit()

    def set_custom_focus(self, new_focus):
        self.custom_focused = new_focus
        self.update_stylesheet()

    def update_stylesheet(self):
        bcol = QColor(self.node.color)
        new_style_sheet = f'''
NodeWidget {{
    border: 0px solid rgba({(
        f'{QColor(self.node.color).red()},{QColor(self.node.color).green()},{QColor(self.node.color).blue()},150'
    )});
    border-radius: 2px;
    {(
        f'background-color: rgba({bcol.red()},{bcol.green()},{bcol.blue()},40);'
    ) if self.custom_focused else ''}
}}   
QLabel {{
    background: transparent;
}}
QLineEdit {{
    color: {self.node.color};
    background: transparent;
    border: none;
}}
        '''

        self.setStyleSheet(new_style_sheet)

    def paintEvent(self, event):  # just to enable stylesheets
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)
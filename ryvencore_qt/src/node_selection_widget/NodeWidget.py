from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QStyleOption, QStyle
from qtpy.QtGui import QFont, QPainter, QColor
from qtpy.QtCore import Signal


class NodeWidget(QWidget):

    chosen = Signal()
    custom_focused_from_inside = Signal()

    def __init__(self, parent, node):
        super(NodeWidget, self).__init__(parent)

        self.custom_focused = False
        self.node = node
#         self.custom_focused_stylesheet = '''
# NodeWidget {
#     border: 2px solid #49aeed;
#     background-color: #246187;
# }
#         '''
#         self.custom_unfocused_stylesheet = '''
# NodeWidget {
#     border: 2px solid #3d3d3d;
# }
#         '''

        # UI
        main_layout = QGridLayout()

        name_label = QLabel(node.title)
        name_label.setFont(QFont('Poppins', 12))

        type_layout = QHBoxLayout()

        type_label = QLabel(node.type_)
        type_label.setFont(QFont('Arial', 8, italic=True))
        # type_label.setStyleSheet('color: white;')

        package_name_layout_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        type_layout.addItem(package_name_layout_spacer)
        type_layout.addWidget(type_label)

        main_layout.addWidget(name_label, 0, 0)
        main_layout.addLayout(type_layout, 1, 0)


        # # ------------------------------------------
        # img_label = QLabel()
        # img_label.setStyleSheet('padding: 20px;')
        # pix = QPixmap(self.node_image)
        # img_label.setPixmap(pix)
        # main_layout.addWidget(img_label, 2, 0)
        # # ------------------------------------------


        self.setLayout(main_layout)


        main_layout.setVerticalSpacing(0)
        main_layout.setSpacing(0)
        self.setContentsMargins(-6, -6, -6, -6)
        main_layout.setContentsMargins(-6, -6, -6, -6)
        self.setToolTip(node.doc)
        self.update_stylesheet()
        # self.setMinimumWidth(70)



    def mousePressEvent(self, event):
        self.custom_focused_from_inside.emit()

    # def mouseMoveEvent(self, event):
    #     self.set_custom_focus(True)

    def mouseReleaseEvent(self, event):
        if self.geometry().contains(self.mapToParent(event.pos())):
            self.chosen.emit()

    def set_custom_focus(self, new_focus):
        self.custom_focused = new_focus
        self.update_stylesheet()
        # if self.custom_focused:
        #     self.setFocus()

        # if new_focus:
        #     self.setStyleSheet(self.custom_focused_stylesheet + '\n' + self.contents_stylesheet)
        # else:
        #     self.setStyleSheet(self.custom_unfocused_stylesheet + '\n' + self.contents_stylesheet)

    def update_stylesheet(self):
        new_style_sheet = f'''
NodeWidget {{
    border: 2px solid rgba({(
        f'{QColor(self.node.color).red()},{QColor(self.node.color).green()},{QColor(self.node.color).blue()},150'
    )});
    border-radius: 4px;
    {(
        f'background-color: rgba({QColor(self.node.color).red()},{QColor(self.node.color).green()},{QColor(self.node.color).blue()},50);'
    ) if self.custom_focused else ''}
}}   
QLabel {{
    color: {self.node.color};
    background: transparent;
}}
        '''

        self.setStyleSheet(new_style_sheet)

    def paintEvent(self, event):  # just to enable stylesheets
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)
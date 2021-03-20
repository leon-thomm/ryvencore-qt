from PySide2.QtWidgets import QGraphicsGridLayout, QGraphicsWidget, \
    QGraphicsLayoutItem
from PySide2.QtCore import Qt, QRectF, QPointF, QSizeF
from PySide2.QtGui import QFontMetricsF, QFont

from .PortItemInputWidgets import RCIW_BUILTIN_SpinBox, RCIW_BUILTIN_LineEdit, RCIW_BUILTIN_LineEdit_small
from .ryvencore.tools import deserialize
from .tools import get_longest_line, shorten

from .FlowViewProxyWidget import FlowViewProxyWidget


class PortItem(QGraphicsWidget):
    """The GUI representative for ports of nodes, also handling mouse events for connections."""

    def __init__(self, node, node_item, port, flow_view):
        super(PortItem, self).__init__()
        self.setGraphicsItem(self)

        self.node = node
        self.node_item = node_item
        self.port = port
        self.flow_view = flow_view

        self.port.has_been_connected.connect(self.port_connected)
        self.port.has_been_disconnected.connect(self.port_disconnected)

        self.pin = PortItemPin(self.port, self, self.node, self.node_item)

        self.label = PortItemLabel(self.port, self, self.node, self.node_item)

        self._layout = QGraphicsGridLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    # --------------------------------------------
    def boundingRect(self):
        return QRectF(QPointF(0, 0), self.geometry().size())

    def setGeometry(self, rect):
        self.prepareGeometryChange()
        QGraphicsLayoutItem.setGeometry(self, rect)
        self.setPos(rect.topLeft())
    # --------------------------------------------

    def setup_ui(self):
        pass

    def port_connected(self):
        pass

    def port_disconnected(self):
        pass


class InputPortItem(PortItem):
    def __init__(self, node, node_item, port):
        super().__init__(node, node_item, port, node.flow)

        self.widget = None
        self.proxy: FlowViewProxyWidget = None

        if self.port.type_ == 'data':
            self.port.val_updated.connect(self._port_val_updated)

        if self.port.add_config and 'widget data' in self.port.add_config:
            self.create_widget()
            try:
                c_d = self.port.add_config['widget data']
                if type(c_d) == dict:  # backwards compatibility
                    self.widget.set_data(c_d)
                else:
                    self.widget.set_data(deserialize(c_d))
            except Exception as e:
                print('Exception while setting data in', self.node.title,
                      '\'s input widget:', e, ' (was this intended?)')
        else:
            self.create_widget()

        self.setup_ui()

    def setup_ui(self):
        l = self._layout

        # l.setSpacing(0)
        l.addItem(self.pin, 0, 0)
        l.setAlignment(self.pin, Qt.AlignVCenter | Qt.AlignLeft)
        l.addItem(self.label, 0, 1)
        l.setAlignment(self.label, Qt.AlignVCenter | Qt.AlignLeft)

        if self.widget is not None:
            if self.port.add_config['widget pos'] == 'besides':
                l.addItem(self.proxy, 0, 2)
            elif self.port.add_config['widget pos'] == 'below':
                l.addItem(self.proxy, 1, 0, 1, 2)
            l.setAlignment(self.proxy, Qt.AlignCenter)

    def create_widget(self, configuration=None):
        if (self.port.type_ and self.port.type_ == 'data') or (configuration and configuration['type'] == 'data'):

            if 'widget name' not in self.port.add_config:
                return  # no input widget

            wn = self.port.add_config['widget name']

            params = (self.port, self, self.node, self.node_item)

            # choose correct class for builtin line edit (the small version for small nodes)
            _RCIW_BUILTIN_LineEdit = RCIW_BUILTIN_LineEdit if self.node.style == 'extended' else \
                RCIW_BUILTIN_LineEdit_small

            if wn == 'std line edit s':
                self.widget = _RCIW_BUILTIN_LineEdit(params, size='small')
            elif wn == 'std line edit m' or wn == 'std line edit':
                self.widget = _RCIW_BUILTIN_LineEdit(params)
            elif wn == 'std line edit l':
                self.widget = _RCIW_BUILTIN_LineEdit(params, size='large')
            elif wn == 'std line edit s r':
                self.widget = _RCIW_BUILTIN_LineEdit(params, size='small', resize=True)
            elif wn == 'std line edit m r':
                self.widget = _RCIW_BUILTIN_LineEdit(params, resize=True)
            elif wn == 'std line edit l r':
                self.widget = _RCIW_BUILTIN_LineEdit(params, size='large', resize=True)
            elif wn == 'std spin box':
                self.widget = RCIW_BUILTIN_SpinBox(params)


            # backwards compatibility

            elif wn == 'std line edit s r nb':
                self.widget = _RCIW_BUILTIN_LineEdit(params, size='small', resize=True)
            elif wn == 'std line edit m r nb':
                self.widget = _RCIW_BUILTIN_LineEdit(params, resize=True)
            elif wn == 'std line edit l r nb':
                self.widget = _RCIW_BUILTIN_LineEdit(params, size='large', resize=True)


            # custom input widget

            else:
                self.widget = self.get_input_widget_class(wn)(params)


            self.proxy = FlowViewProxyWidget(self.flow_view, parent=self.node_item)
            self.proxy.setWidget(self.widget)

    def get_input_widget_class(self, widget_name):
        """Returns the CLASS of a defined custom input widget"""
        return self.node.input_widget_classes[widget_name]

    def port_connected(self):
        """Disables the widget"""
        if self.widget:
            self.widget.setEnabled(False)
        self._port_val_updated(self.port.val)

    def port_disconnected(self):
        """Enables the widget again"""
        if self.widget:
            self.widget.setEnabled(True)

    def _port_val_updated(self, val):
        """Called from output port"""
        if self.widget:
            self.widget.val_update_event(val)


class OutputPortItem(PortItem):
    def __init__(self, node, node_item, port):
        super().__init__(node, node_item, port, node.flow)
        # super(OutputPortItem, self).__init__(parent_node_instance, PortObjPos.OUTPUT, type_, label_str)

        self.setup_ui()

    def setup_ui(self):
        l = self._layout

        # l.setSpacing(5)
        l.addItem(self.label, 0, 0)
        l.setAlignment(self.label, Qt.AlignVCenter | Qt.AlignRight)
        l.addItem(self.pin, 0, 1)

        l.setAlignment(self.pin, Qt.AlignVCenter | Qt.AlignRight)


# CONTENTS -------------------------------------------------------------------------------------------------------------


class PortItemPin(QGraphicsWidget):
    def __init__(self, port, port_item, node, node_item):
        super(PortItemPin, self).__init__(node_item)

        self.port = port
        self.port_item = port_item
        self.node = node
        self.node_item = node_item
        self.flow_view = self.node_item.flow_view

        self.setGraphicsItem(self)
        self.setAcceptHoverEvents(True)
        self.hovered = False
        self.setCursor(Qt.CrossCursor)
        self.tool_tip_pos = None

        self.padding = 2
        self.painting_width = 15
        self.painting_height = 15
        self.width = self.painting_width+2*self.padding
        self.height = self.painting_height+2*self.padding
        self.port_local_pos = None

    def boundingRect(self):
        return QRectF(QPointF(0, 0), self.geometry().size())

    def setGeometry(self, rect):
        self.prepareGeometryChange()
        QGraphicsLayoutItem.setGeometry(self, rect)
        self.setPos(rect.topLeft())

    def sizeHint(self, which, constraint=...):
        return QSizeF(self.width, self.height)

    def paint(self, painter, option, widget=None):
        self.node_item.session_design.flow_theme.paint_PI(
            node=self.node,
            painter=painter,
            option=option,
            node_color=self.node_item.color,
            type_=self.port.type_,
            connected=len(self.port.connections) > 0,
            padding=self.padding,
            w=self.painting_width,
            h=self.painting_height
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # DRAG NEW CONNECTION
            self.flow_view.mouse_event_taken = True
            self.flow_view._selected_pin = self
            self.flow_view._dragging_connection = True
            event.accept()  # don't pass the ev ent to anything below
        else:
            return QGraphicsWidget.mousePressEvent(self, event)


    def hoverEnterEvent(self, event):
        if self.port.type_ == 'data':  # and self.parent_port_instance.io_pos == PortPos.OUTPUT:
            self.setToolTip(shorten(str(self.port.val), 1000, line_break=True))

        # update all connections
        for c in self.port.connections:
            conn_item = self.flow_view.connection_items[c]
            conn_item.update()

        self.hovered = True

        QGraphicsWidget.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):

        # turn connection highlighting off
        for c in self.port.connections:
            conn_item = self.flow_view.connection_items[c]
            conn_item.update()
        self.hovered = False

        QGraphicsWidget.hoverLeaveEvent(self, event)

    def get_scene_center_pos(self):
        if not self.node_item.collapsed:
            return QPointF(self.scenePos().x() + self.boundingRect().width()/2,
                           self.scenePos().y() + self.boundingRect().height()/2)
        else:
            if isinstance(self.port_item, InputPortItem):
                return self.node_item.get_left_body_header_vertex_scene_pos()
            else:
                return self.node_item.get_right_body_header_vertex_scene_pos()


class PortItemLabel(QGraphicsWidget):
    def __init__(self, port, port_item, node, node_item):
        super(PortItemLabel, self).__init__(node_item)
        self.setGraphicsItem(self)

        self.port = port
        self.port_item = port_item
        self.node = node
        self.node_item = node_item

        self.font = QFont("Source Code Pro", 10, QFont.Bold)
        font_metrics = QFontMetricsF(self.font)  # approximately! the designs can use different fonts
        self.width = font_metrics.width(get_longest_line(self.port.label_str))
        self.height = font_metrics.height() * (self.port.label_str.count('\n') + 1)
        self.port_local_pos = None

    def boundingRect(self):
        return QRectF(QPointF(0, 0), self.geometry().size())

    def setGeometry(self, rect):
        self.prepareGeometryChange()
        QGraphicsLayoutItem.setGeometry(self, rect)
        self.setPos(rect.topLeft())

    def sizeHint(self, which, constraint=...):
        return QSizeF(self.width, self.height)

    def paint(self, painter, option, widget=None):
        self.node_item.session_design.flow_theme.paint_PI_label(
            self.node,
            painter, option,
            self.port.type_,
            len(self.port.connections) > 0,
            self.port.label_str,
            self.node_item.color,
            self.boundingRect()
        )

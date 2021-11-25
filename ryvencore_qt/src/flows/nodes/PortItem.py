from qtpy.QtWidgets import QGraphicsGridLayout, QGraphicsWidget, \
    QGraphicsLayoutItem
from qtpy.QtCore import Qt, QRectF, QPointF, QSizeF
from qtpy.QtGui import QFontMetricsF, QFont

from ...GUIBase import GUIBase
from .PortItemInputWidgets import \
    Data_IW_S, Data_IW_M, Data_IW_L, Float_IW, Integer_IW, Choice_IW, Boolean_IW, String_IW_S, String_IW_M, String_IW_L
from ryvencore import dtypes, serialize
from ryvencore.utils import deserialize
from ...utils import get_longest_line, shorten

from ..FlowViewProxyWidget import FlowViewProxyWidget


class PortItem(GUIBase, QGraphicsWidget):
    """The GUI representative for ports of nodes, also handling mouse events for connections."""

    def __init__(self, node, node_item, port, flow_view):
        GUIBase.__init__(self, representing_component=port)
        QGraphicsWidget.__init__(self)

        self.setGraphicsItem(self)

        self.node = node
        self.node_item = node_item
        self.port = port
        self.flow_view = flow_view

        # self.port.has_been_connected.connect(self.port_connected)
        # self.port.has_been_disconnected.connect(self.port_disconnected)

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

        self.proxy = None  # widget proxy
        self.widget = self.create_widget()

        if self.widget:
            self.proxy = FlowViewProxyWidget(self.flow_view, parent=self.node_item)
            self.proxy.setWidget(self.widget)

        self.update_widget_value = self.widget is not None  # modified by FlowView when performance mode changes

        # catch up to missed connections
        if len(self.port.connections) > 0:
            self.port_connected()

        if self.port.add_data:

            if self.port.dtype:
                c_d = self.port.add_data['widget data']
                self.widget.set_state(deserialize(c_d))

            elif 'widget data' in self.port.add_data:
                try:
                    c_d = self.port.add_data['widget data']
                    if type(c_d) == dict:  # backwards compatibility
                        self.widget.set_state(c_d)
                    else:
                        self.widget.set_state(deserialize(c_d))
                except Exception as e:
                    print('Exception while setting data in', self.node.title,
                          '\'s input widget:', e, ' (was this intended?)')

        self.setup_ui()

    def setup_ui(self):
        l = self._layout

        # l.setSpacing(0)
        l.addItem(self.pin, 0, 0)
        l.setAlignment(self.pin, Qt.AlignVCenter | Qt.AlignLeft)
        l.addItem(self.label, 0, 1)
        l.setAlignment(self.label, Qt.AlignVCenter | Qt.AlignLeft)
        if self.widget:
            if self.port.add_data and self.port.add_data.get('widget pos') == 'below':
                l.addItem(self.proxy, 1, 0, 1, 2)
            else:
                l.addItem(self.proxy, 0, 2)  # besides

            l.setAlignment(self.proxy, Qt.AlignCenter)

    def create_widget(self):

        params = (self.port, self, self.node, self.node_item)

        if self.port.dtype:

            dtype = self.port.dtype

            if isinstance(dtype, dtypes.Data):
                if dtype.size == 's':
                    return Data_IW_S(params)
                elif dtype.size == 'm':
                    return Data_IW_M(params)
                elif dtype.size == 'l':
                    return Data_IW_L(params)

            elif isinstance(dtype, dtypes.String):
                if dtype.size == 's':
                    return String_IW_S(params)
                elif dtype.size == 'm':
                    return String_IW_M(params)
                elif dtype.size == 'l':
                    return String_IW_L(params)

            elif isinstance(dtype, dtypes.Integer):
                return Integer_IW(params)

            elif isinstance(dtype, dtypes.Float):
                return Float_IW(params)

            elif isinstance(dtype, dtypes.Boolean):
                return Boolean_IW(params)

            elif isinstance(dtype, dtypes.Choice):
                return Choice_IW(params)

        elif self.port.type_ == 'data' and self.port.add_data and 'widget name' in self.port.add_data:

            # custom input widget
            return self.get_input_widget_class(self.port.add_data['widget name'])(params)

        else:
            return None


    def get_input_widget_class(self, widget_name):
        """Returns the CLASS of a defined custom input widget"""
        return self.node.input_widget_classes[widget_name]

    def port_connected(self):
        """Disables the widget"""
        if self.widget:
            self.widget.setEnabled(False)

        if self.port.type_ == 'data':
            self.port.connections[0].activated.connect(self._port_val_updated)

        self._port_val_updated(self.port.val)

    def port_disconnected(self):
        """Enables the widget again"""
        if self.widget:
            self.widget.setEnabled(True)

    def _port_val_updated(self, val):
        """Called from output port"""

        if self.update_widget_value:  # this might be quite slow
            self.widget.val_update_event(val)

    def complete_data(self, data: dict) -> dict:
        if self.port.type_ == 'data':
            if self.widget:
                data['has widget'] = True
                if not self.port.dtype:
                    # this stuff is statically stored in port.add_data
                    data['widget name'] = self.port.add_data['widget name']
                    data['widget pos'] = self.port.add_data['widget pos']

                data['widget data'] = serialize(self.widget.get_state())
            else:
                data['has widget'] = False

        return data


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
        # self.painting_width = 17
        # self.painting_height = 17
        # self.width = self.painting_width+2*self.padding
        # self.height = self.painting_height+2*self.padding
        self.width = 17
        self.height = 17
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
            rect=QRectF(self.padding, self.padding, self.width-2*self.padding, self.height-2*self.padding)
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # DRAG NEW CONNECTION
            self.flow_view.mouse_event_taken = True
            self.flow_view._selected_pin = self
            self.flow_view._dragging_connection = True
            event.accept()  # don't pass the ev ent to anything below
        else:
            return QGraphicsWidget.mousePressEvent(self, event)


    def moveEvent(self, event):
        super().moveEvent(event)

        # update connections
        conn_items = self.flow_view.connection_items
        for c in self.port.connections:
            i = conn_items[c]

            # if the items are grouped (which means they move together), don't recompute
            if i.out.group() is None or i.out.group() != i.inp.group():  # not entirely sure if this is working
                i.recompute()


    def hoverEnterEvent(self, event):
        if self.port.type_ == 'data':  # and self.parent_port_instance.io_pos == PortPos.OUTPUT:
            self.setToolTip(shorten(str(self.port.val), 1000, line_break=True))

        # highlight connections
        items = self.flow_view.connection_items
        for c in self.port.connections:
            items[c].set_highlighted(True)

        self.hovered = True

        QGraphicsWidget.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):

        # un-highlight connections
        items = self.flow_view.connection_items
        for c in self.port.connections:
            items[c].set_highlighted(False)

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

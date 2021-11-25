from qtpy.QtWidgets import QGraphicsItem, QGraphicsObject, QMenu, QGraphicsDropShadowEffect
from qtpy.QtCore import Qt, QRectF, QObject, QPointF
from qtpy.QtGui import QColor

from ...GUIBase import GUIBase
from ryvencore.NodePort import NodeInput, NodeOutput
from .NodeItemAction import NodeItemAction
from .NodeItemAnimator import NodeItemAnimator
from .NodeItemWidget import NodeItemWidget
from .PortItem import InputPortItem, OutputPortItem
from ...utils import serialize, deserialize
from ...utils import MovementEnum


class NodeItem(GUIBase, QGraphicsObject):  # QGraphicsItem, QObject):
    """The GUI representative for nodes. Unlike the Node class, this class is not subclassed individually and works
    the same for every node."""

    def __init__(self, node, params):
        # QGraphicsItem.__init__(self)
        # QObject.__init__(self)
        GUIBase.__init__(self, representing_component=node)
        QGraphicsObject.__init__(self)

        self.node = node
        flow_view, design, load_data = params
        self.flow_view = flow_view
        self.session_design = design
        self.movement_state = None
        self.movement_pos_from = None
        self.painted_once = False
        self.inputs = []
        self.outputs = []
        self.color = QColor(self.node.color)  # manipulated by self.animator

        self.collapsed = False
        self.hovered = False
        self.hiding_unconnected_ports = False

        self.personal_logs = []

        # 'initializing' will be set to False below. It's needed for the ports setup, to prevent shape updating stuff
        self.initializing = True

        # self.temp_state_data = None
        self.init_data = load_data

        # CONNECT TO NODE
        self.node.updated.connect(self.node_updated)
        self.node.update_shape_triggered.connect(self.update_shape)
        self.node.hide_unconnected_ports_triggered.connect(self.hide_unconnected_ports_triggered)
        self.node.show_unconnected_ports_triggered.connect(self.show_unconnected_ports_triggered)
        self.node.input_added.connect(self.add_new_input)
        self.node.output_added.connect(self.add_new_output)
        self.node.input_removed.connect(self.remove_input)
        self.node.output_removed.connect(self.remove_output)

        # FLAGS
        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemSendsScenePositionChanges
        )
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # UI
        self.shadow_effect = None
        self.main_widget = None
        if self.node.main_widget_class is not None:
            self.main_widget = self.node.main_widget_class((self.node, self))
        self.widget = NodeItemWidget(self.node, self)  # QGraphicsWidget(self)
        self.animator = NodeItemAnimator(self)  # needs self.title_label

        # TOOLTIP
        if self.node.description_html:
            self.setToolTip(self.node.description_html)
        elif self.node.__doc__:
            self.setToolTip('<html><head/><body><p>' + self.node.__doc__ + '</p></body></html>')
        self.setCursor(Qt.SizeAllCursor)

        # DESIGN THEME
        self.session_design.flow_theme_changed.connect(self.update_design)
        self.session_design.performance_mode_changed.connect(self.update_design)

    def initialize(self):
        """All ports and the main widget get finally created here."""

        # LOADING DATA
        if self.init_data is not None:
            if self.main_widget:
                try:
                    self.main_widget.set_state(deserialize(self.init_data['main widget data']))
                except Exception as e:
                    print('Exception while setting data in', self.node.title, 'Node\'s main widget:', e,
                          ' (was this intended?)')

        # catch up on ports
        for i in self.node.inputs:
            self.add_new_input(i)

        for o in self.node.outputs:
            self.add_new_output(o)

        if self.init_data is not None:
            if self.init_data.get('unconnected ports hidden'):
                self.hide_unconnected_ports_triggered()
            if self.init_data.get('collapsed'):
                self.collapse()

        self.initializing = False

        # No self.update_shape() here because for some reason, the bounding rect hasn't been initialized yet, so
        # self.update_shape() gets called when the item is being drawn the first time (see paint event in NI painter)
        # https://forum.qt.io/topic/117179/force-qgraphicsitem-to-update-immediately-wait-for-update-event

        self.update_design()  # load current design, update QGraphicsItem

        self.update()  # ... not sure if I need that

    # --------------------------------------------------------------------------------------
    # UI STUFF ----------------------------------------

    def node_updated(self):
        if self.session_design.animations_enabled:
            if not self.animator.running():
                self.animator.start()
            elif self.animator.fading_out():
                self.animator.set_animation_max()

        self.update()

    def add_new_input(self, inp: NodeInput, insert: int = None):

        # create item
        # inp.item = InputPortItem(inp.node, self, inp)
        item = InputPortItem(inp.node, self, inp)

        if insert is not None:
            self.inputs.insert(insert, item)
            self.widget.insert_input_into_layout(insert, item)
        else:
            self.inputs.append(item)
            self.widget.add_input_to_layout(item)

        if not self.initializing:
            self.update_shape()
            self.update()

    def remove_input(self, inp: NodeInput):
        item = None
        for inp_item in self.inputs:
            if inp_item.port == inp:
                item = inp_item
                break

        # index = self.node.inputs.index(inp)
        # item = self.inputs[index]

        # for some reason, I have to remove all widget items manually from the scene too. setting the items to
        # ownedByLayout(True) does not work, I don't know why.
        self.scene().removeItem(item.pin)
        self.scene().removeItem(item.label)
        if item.proxy is not None:
            self.scene().removeItem(item.proxy)

        self.inputs.remove(item)
        self.widget.remove_input_from_layout(item)

        if not self.initializing:
            self.update_shape()
            self.update()

    def add_new_output(self, out: NodeOutput, insert: int = None):

        # create item
        # out.item = OutputPortItem(out.node, self, out)
        item = OutputPortItem(out.node, self, out)

        if insert is not None:
            self.outputs.insert(insert, item)
            self.widget.insert_output_into_layout(insert, item)
        else:
            self.outputs.append(item)
            self.widget.add_output_to_layout(item)

        if not self.initializing:
            self.update_shape()
            self.update()

    def remove_output(self, out: NodeOutput):
        item = None
        for out_item in self.outputs:
            if out_item.port == out:
                item = out_item
                break

        # index = self.node.outputs.index(out)
        # item = self.outputs[index]

        # see remove_input() for info!
        self.scene().removeItem(item.pin)
        self.scene().removeItem(item.label)

        self.outputs.remove(item)
        self.widget.remove_output_from_layout(item)

        if not self.initializing:
            self.update_shape()
            self.update()

    def update_shape(self):
        self.widget.update_shape()
        self.update_conn_pos()
        self.flow_view.viewport().update()

    def update_design(self):
        """Loads the shadow effect option and causes redraw with active theme."""

        if self.session_design.node_item_shadows_enabled:
            self.shadow_effect = QGraphicsDropShadowEffect()
            self.shadow_effect.setXOffset(12)
            self.shadow_effect.setYOffset(12)
            self.shadow_effect.setBlurRadius(20)
            self.shadow_effect.setColor(self.session_design.flow_theme.node_item_shadow_color)
            self.setGraphicsEffect(self.shadow_effect)
        else:
            self.setGraphicsEffect(None)

        self.widget.update_shape()
        self.animator.reload_values()

        QGraphicsItem.update(self)

    def boundingRect(self):
        # remember: (0, 0) shall be the NI's center!
        rect = QRectF()
        w = self.widget.layout().geometry().width()
        h = self.widget.layout().geometry().height()
        rect.setLeft(-w / 2)
        rect.setTop(-h / 2)
        rect.setWidth(w)
        rect.setHeight(h)
        return rect

    def get_left_body_header_vertex_scene_pos(self):
        return self.mapToScene(
            QPointF(
                -self.boundingRect().width() / 2,
                -self.boundingRect().height() / 2 + self.widget.header_widget.rect().height()
            )
        )

    def get_right_body_header_vertex_scene_pos(self):
        return self.mapToScene(
            QPointF(
                +self.boundingRect().width() / 2,
                -self.boundingRect().height() / 2 + self.widget.header_widget.rect().height()
            )
        )

    def hide_unconnected_ports_triggered(self):
        self.widget.hide_unconnected_ports()
        self.hiding_unconnected_ports = True
        self.update_shape()

    def show_unconnected_ports_triggered(self):
        self.widget.show_unconnected_ports()
        self.hiding_unconnected_ports = False
        self.update_shape()

    def expand(self):
        self.collapsed = False
        self.widget.expand()
        self.update_shape()

    def collapse(self):
        self.collapsed = True
        self.widget.collapse()
        self.update_shape()

    #   PAINTING

    def paint(self, painter, option, widget=None):
        """All painting is done by NodeItemPainter"""

        # in order to access a meaningful geometry of GraphicsWidget contents in update_shape(), the paint event
        # has to be called once. See here:
        # https://forum.qt.io/topic/117179/force-qgraphicsitem-to-update-immediately-wait-for-update-event/4
        if not self.painted_once:
            # ok, quick notice. Since I am using a NodeItemWidget, calling self.update_design() here (again)
            # leads to a QT crash without error, which is really strange. Calling update_design multiple times
            # principally isn't a problem, but, for some reason, here it leads to a crash in QT. It's not necessary
            # anymore, so I removed it.
            # self.update_design()

            self.update_shape()
            self.update_conn_pos()

        self.session_design.flow_theme.paint_NI(
            node=self.node,
            selected=self.isSelected(),
            hovered=self.hovered,
            node_style=self.node.style,
            painter=painter,
            option=option,
            color=self.color,
            w=self.boundingRect().width(),
            h=self.boundingRect().height(),
            bounding_rect=self.boundingRect(),
            title_rect=self.widget.header_widget.boundingRect()
            if self.widget.header_widget
            else self.widget.title_label.boundingRect()
        )

        # useful for widget development:

        # painter.setBrush(Qt.NoBrush)
        # painter.setPen(QPen(QColor('black')))
        #
        # painter.drawRect(
        #         self.boundingRect()
        # )
        #
        # header_rect = QRectF(
        #         -self.boundingRect().width()/2, -self.boundingRect().height()/2,
        #         self.widget.header_widget.geometry().width(), self.widget.header_widget.geometry().height()
        #     )
        # painter.drawRect(header_rect)
        #
        # # note that the widget's layout has spacing 0
        # body_rect = QRectF(
        #     -self.boundingRect().width()/2, -self.boundingRect().height()/2 + header_rect.height(),
        #     self.widget.body_widget.geometry().width(), self.widget.body_widget.geometry().height()
        # )
        # painter.drawRect(body_rect)

        self.painted_once = True

    # MOUSE INTERACTION

    def get_context_menu(self):
        menu = QMenu(self.flow_view)

        for a in self.get_actions(self.node.get_extended_default_actions(), menu):  # menu needed for 'parent'
            if type(a) == NodeItemAction:
                menu.addAction(a)
            elif type(a) == QMenu:
                menu.addMenu(a)

        menu.addSeparator()

        actions = self.get_actions(self.node.actions, menu)
        for a in actions:  # menu needed for 'parent'
            if type(a) == NodeItemAction:
                menu.addAction(a)
            elif type(a) == QMenu:
                menu.addMenu(a)

        return menu

    def itemChange(self, change, value):
        """Ensures that all connections, selection borders etc. that get drawn in the FlowView get
        constantly redrawn during a drag of the item"""

        if change == QGraphicsItem.ItemPositionChange:
            if self.session_design.performance_mode == 'pretty':
                self.flow_view.viewport().update()
            if self.movement_state == MovementEnum.mouse_clicked:
                self.movement_state = MovementEnum.position_changed

        self.update_conn_pos()

        return QGraphicsItem.itemChange(self, change, value)

    def update_conn_pos(self):
        """Updates the scene positions of connections"""

        for o in self.node.outputs:
            for c in o.connections:
                # c.item.recompute()

                if c not in self.flow_view.connection_items:
                    # it can happen that the connection item hasn't been
                    # created yet
                    continue

                item = self.flow_view.connection_items[c]
                item.recompute()
        for i in self.node.inputs:
            for c in i.connections:
                # c.item.recompute()

                if c not in self.flow_view.connection_items:
                    # it can happen that the connection item hasn't been
                    # created yet
                    continue

                item = self.flow_view.connection_items[c]
                item.recompute()

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.widget.title_label.set_NI_hover_state(hovering=True)
        QGraphicsItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.widget.title_label.set_NI_hover_state(hovering=False)
        QGraphicsItem.hoverLeaveEvent(self, event)

    def mousePressEvent(self, event):
        """Used for Moving-Commands in FlowView - may be replaced later by a nicer determination of a moving action."""

        self.flow_view.mouse_event_taken = True

        if event.button() == Qt.LeftButton:
            self.movement_state = MovementEnum.mouse_clicked
            self.movement_pos_from = self.pos()
        return QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Used for Moving-Commands in FlowView - may be replaced later by a nicer determination of a moving action."""

        self.flow_view.mouse_event_taken = True

        if self.movement_state == MovementEnum.position_changed:
            self.flow_view.selected_components_moved(self.pos() - self.movement_pos_from)
        self.movement_state = None
        return QGraphicsItem.mouseReleaseEvent(self, event)

    # ACTIONS

    def get_actions(self, actions_dict, menu):
        actions = []

        for k in actions_dict:
            v_dict = actions_dict[k]
            try:
                method = v_dict['method']
                data = None
                try:
                    data = v_dict['data']
                except KeyError:
                    pass
                action = NodeItemAction(node=self.node, text=k, method=method, menu=menu, data=data)
                action.triggered_with_data.connect(self.flow_view.thread_interface.trigger_node_action)
                action.triggered_without_data.connect(self.flow_view.thread_interface.trigger_node_action)

                actions.append(action)
            except KeyError:
                action_menu = QMenu(k, menu)
                sub_actions = self.get_actions(v_dict, action_menu)
                for a in sub_actions:
                    action_menu.addAction(a)
                actions.append(action_menu)

        return actions

    # DATA

    def complete_data(self, data: dict) -> dict:
        """completes the node's data by adding all frontend info"""

        data['pos x'] = self.pos().x()
        data['pos y'] = self.pos().y()
        if self.main_widget:
            data['main widget data'] = serialize(self.main_widget.get_state())

        data['unconnected ports hidden'] = self.hiding_unconnected_ports
        data['collapsed'] = self.collapsed

        return data

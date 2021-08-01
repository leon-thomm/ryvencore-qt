"""
This file contains the implementations of the possible undoable actions for FlowView.

Why not in Flow?
-> Because there are actions that only regard the GUI and are therefore unnoticed by the Flow but still undoable, like
adding a DrawingObject.

The main characteristic of these implementations is that they communicate with the Flow only using signals and slots,
which complicates the process of making changes but enables threading, as in case of the abstract
components being managed in a separate thread, no direct communication between the FlowCommands from the main thread
and the Flow are allowed. Usually to make changes to the flow, they emit signals that are temporarily connected
the the Flow which then causes the FlowView to update accordingly.

These implementations might have quite some potential for improvement.
"""


from qtpy.QtCore import Signal, QObject, QPointF
from qtpy.QtWidgets import QUndoCommand

from .DrawingObject import DrawingObject
from .ryvencore.Node import Node
from .ryvencore.Connection import Connection
from .NodeItem import NodeItem
from .ryvencore.NodePort import NodePort


class FlowUndoCommand(QObject, QUndoCommand):
    """
    The main difference to normal QUndoCommands is the activation feature. This allows the flow widget to add the
    undo command to the undo stack before redo() is called. This is important since some of these commands can cause
    other commands to be added while they are performing redo(), so to prevent those commands to be added to the
    undo stack before the parent command, it is here blocked at first.
    """

    def __init__(self, flow_view):

        self.flow_view = flow_view
        self.flow = flow_view.flow
        self._activated = False

        QObject.__init__(self)
        QUndoCommand.__init__(self)

    def activate(self):
        self._activated = True
        self.redo()

    def redo(self) -> None:
        if not self._activated:
            return
        else:
            self.redo_()

    def undo(self) -> None:
        self.undo_()

    def redo_(self):
        """subclassed"""
        pass

    def undo_(self):
        """subclassed"""
        pass


class MoveComponents_Command(FlowUndoCommand):
    def __init__(self, flow_view, items_list, p_from, p_to):
        super(MoveComponents_Command, self).__init__(flow_view)

        self.items_list = items_list
        self.p_from = p_from
        self.p_to = p_to
        self.last_item_group_pos = p_to

    def undo_(self):
        items_group = self.items_group()
        items_group.setPos(self.p_from)
        self.last_item_group_pos = items_group.pos()
        self.destroy_items_group(items_group)

    def redo_(self):
        items_group = self.items_group()
        items_group.setPos(self.p_to - self.last_item_group_pos)
        self.destroy_items_group(items_group)


    def items_group(self):
        return self.flow_view.scene().createItemGroup(self.items_list)

    def destroy_items_group(self, items_group):
        self.flow_view.scene().destroyItemGroup(items_group)


class PlaceNode_Command(FlowUndoCommand):

    create_node_request = Signal(object)
    add_node_request = Signal(Node)
    remove_node_request = Signal(Node)

    def __init__(self, flow_view, node_class, pos):
        super().__init__(flow_view)

        self.node_class = node_class
        self.node = None
        self.item_pos = pos

        self.create_node_request.connect(self.flow.create_node)
        self.add_node_request.connect(self.flow.add_node)
        self.remove_node_request.connect(self.flow.remove_node)

        self.flow_view.node_placed.connect(self.node_placed_in_flow)

    def undo_(self):
        self.remove_node_request.emit(self.node)

    def redo_(self):
        if self.node:
            self.add_node_request.emit(self.node)
        else:
            self.flow_view.node_placed.connect(self.node_placed_in_flow)
            self.create_node_request.emit(self.node_class)

        # --> node_placed_in_flow()

    def node_placed_in_flow(self, node):
        self.flow_view.node_placed.disconnect(self.node_placed_in_flow)
        self.node = node


class PlaceDrawing_Command(FlowUndoCommand):
    def __init__(self, flow_view, posF, drawing):
        super().__init__(flow_view)

        self.drawing = drawing
        self.drawing_obj_place_pos = posF
        self.drawing_obj_pos = self.drawing_obj_place_pos

    def undo_(self):
        # The drawing_obj_pos is not anymore the drawing_obj_place_pos because after the
        # drawing object was completed, its actual position got recalculated according to all points and differs from
        # the initial pen press pos (=drawing_obj_place_pos). See DrawingObject.finished().

        self.drawing_obj_pos = self.drawing.pos()

        self.flow_view.remove_component(self.drawing)

    def redo_(self):
        self.flow_view.add_drawing(self.drawing, self.drawing_obj_pos)


class RemoveComponents_Command(FlowUndoCommand):

    add_node_request = Signal(Node)
    remove_node_request = Signal(Node)

    add_connection_request = Signal(Connection)
    remove_connection_request = Signal(Connection)

    def __init__(self, flow_view, items):
        super().__init__(flow_view)

        self.items = items
        self.broken_connections = []  # the connections that go beyond the removed nodes and need to be restored in undo
        self.internal_connections = set()

        # static connections
        self.add_node_request.connect(self.flow.add_node)
        self.remove_node_request.connect(self.flow.remove_node)
        self.add_connection_request.connect(self.flow.add_connection)
        self.remove_connection_request.connect(self.flow.remove_connection)

        self.node_items = []
        self.nodes = []
        self.drawings = []
        for i in self.items:
            if isinstance(i, NodeItem):
                self.node_items.append(i)
                self.nodes.append(i.node)
            elif isinstance(i, DrawingObject):
                self.drawings.append(i)

        for n in self.nodes:
            for i in n.inputs:
                for c in i.connections:
                    cp = c.out
                    cn = cp.node
                    if cn not in self.nodes:
                        self.broken_connections.append(c)
                    else:
                        self.internal_connections.add(c)
            for o in n.outputs:
                for c in o.connections:
                    cp = c.inp
                    cn = cp.node
                    if cn not in self.nodes:
                        self.broken_connections.append(c)
                    else:
                        self.internal_connections.add(c)

    def undo_(self):
        # add connections
        self.restore_broken_connections()
        self.restore_internal_connections()

        # add nodes
        for n in self.nodes:
            self.add_node_request.emit(n)

        # add drawings
        for d in self.drawings:
            self.flow_view.add_drawing(d)

    def redo_(self):

        # remove connections
        self.remove_broken_connections()
        self.remove_internal_connections()

        # remove nodes
        for n in self.nodes:
            self.remove_node_request.emit(n)

        # remove drawings
        for d in self.drawings:
            self.flow_view.remove_drawing(d)

    def restore_internal_connections(self):
        for c in self.internal_connections:
            self.add_connection_request.emit(c)

    def remove_internal_connections(self):
        for c in self.internal_connections:
            self.remove_connection_request.emit(c)

    def restore_broken_connections(self):
        for c in self.broken_connections:
            self.add_connection_request.emit(c)

    def remove_broken_connections(self):
        for c in self.broken_connections:
            self.remove_connection_request.emit(c)


class ConnectPorts_Command(FlowUndoCommand):

    connect_request = Signal(NodePort, NodePort)
    add_connection_request = Signal(Connection)
    remove_connection_request = Signal(Connection)

    def __init__(self, flow_view, out, inp):
        super().__init__(flow_view)

        # CAN ALSO LEAD TO DISCONNECT INSTEAD OF CONNECT!!

        self.out = out
        self.inp = inp
        self.connection = None
        self.connecting = True

        # static connections
        self.connect_request.connect(self.flow.connect_nodes)
        self.add_connection_request.connect(self.flow.add_connection)
        self.remove_connection_request.connect(self.flow.remove_connection)

        for c in self.out.connections:
            if c.inp == self.inp:
                self.connection = c
                self.connecting = False


    def undo_(self):
        if self.connecting:
            # remove connection
            self.remove_connection_request.emit(self.connection)
        else:
            # recreate former connection
            self.add_connection_request.emit(self.connection)

    def redo_(self):
        if self.connecting:
            if self.connection:
                self.add_connection_request.emit(self.connection)
            else:
                # connection hasn't been created yet
                self.flow.connection_added.connect(self.connection_created)
                self.connect_request.emit(self.out, self.inp)
        else:
            # remove existing connection
            self.remove_connection_request.emit(self.connection)

    def connection_created(self, c):
        self.flow.connection_added.disconnect(self.connection_created)
        self.connection = c




class Paste_Command(FlowUndoCommand):

    create_nodes_request = Signal(list)
    create_connections_request = Signal(list, list)

    add_node_request = Signal(Node)
    remove_node_request = Signal(Node)

    add_connection_request = Signal(Connection)
    remove_connection_request = Signal(Connection)


    def __init__(self, flow_view, data, offset_for_middle_pos):
        super().__init__(flow_view)

        self.data = data
        self.modify_data_positions(offset_for_middle_pos)
        self.pasted_components = None

        # static connections
        self.add_node_request.connect(self.flow.add_node)
        self.remove_node_request.connect(self.flow.remove_node)
        self.add_connection_request.connect(self.flow.add_connection)
        self.remove_connection_request.connect(self.flow.remove_connection)


    def modify_data_positions(self, offset):
        """adds the offset to the components' positions in data"""

        for node in self.data['nodes']:
            node['pos x'] = node['pos x'] + offset.x()
            node['pos y'] = node['pos y'] + offset.y()
        for drawing in self.data['drawings']:
            drawing['pos x'] = drawing['pos x'] + offset.x()
            drawing['pos y'] = drawing['pos y'] + offset.y()


    def connect_to_flow(self):
        """creates temporary connections to retrieve the created components once"""
        self.flow.nodes_created_from_data.connect(self.nodes_created)
        self.flow.connections_created_from_data.connect(self.connections_created)
        self.create_nodes_request.connect(self.flow.create_nodes_from_data)
        self.create_connections_request.connect(self.flow.connect_nodes_from_data)

    def disconnect_from_flow(self):
        self.flow.nodes_created_from_data.disconnect(self.nodes_created)
        self.flow.connections_created_from_data.disconnect(self.connections_created)
        self.create_nodes_request.disconnect(self.flow.create_nodes_from_data)
        self.create_connections_request.disconnect(self.flow.connect_nodes_from_data)


    def redo_(self):
        if self.pasted_components is None:
            self.pasted_components = {}

            # create components
            self.create_drawings()
            self.connect_to_flow()
            self.create_nodes_request.emit(self.data['nodes'])
            # --> nodes_created()
        else:
            self.add_existing_components()

    def undo_(self):
        # remove components and their items from flow
        for n in self.pasted_components['nodes']:
            self.remove_node_request.emit(n)
        for c in self.pasted_components['connections']:
            self.remove_connection_request.emit(c)
        for d in self.pasted_components['drawings']:
            self.flow_view.remove_drawing(d)

    def add_existing_components(self):
        # add existing components and items to flow
        for n in self.pasted_components['nodes']:
            self.add_node_request.emit(n)
        for c in self.pasted_components['connections']:
            self.add_connection_request.emit(c)
        for d in self.pasted_components['drawings']:
            self.flow_view.add_drawing(d)

        self.select_new_components_in_view()

    def select_new_components_in_view(self):
        self.flow_view.clear_selection()
        for d in self.pasted_components['drawings']:
            d: DrawingObject
            d.setSelected(True)
        for n in self.pasted_components['nodes']:
            n: NodeItem
            ni: NodeItem = self.flow_view.node_items[n]
            ni.setSelected(True)




    def nodes_created(self, nodes):
        self.pasted_components['nodes'] = nodes
        self.create_connections_request.emit(nodes, self.data['connections'])
        # --> connections_created()

    def connections_created(self, connections):
        self.disconnect_from_flow()
        self.pasted_components['connections'] = connections

        # self.create_drawings()
        self.select_new_components_in_view()

    def create_drawings(self):
        drawings = []
        for d in self.data['drawings']:
            new_drawing = self.flow_view.create_drawing(d)
            self.flow_view.add_drawing(new_drawing, posF=QPointF(d['pos x'], d['pos y']))
            drawings.append(new_drawing)
        self.pasted_components['drawings'] = drawings

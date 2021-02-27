from PySide2.QtCore import QObject, Signal

from .RC import PortObjPos, FlowAlg
from .tools import serialize
from .InfoMsgs import InfoMsgs


class NodeObjPort(QObject):
    """The base class for inputs and outputs of nodes with basic functionality."""

    has_been_connected = Signal()
    has_been_disconnected = Signal()

    def __init__(self, node, io_pos, type_, label_str):
        super().__init__()

        self.val = None
        self.node = node
        self.io_pos = io_pos
        self.type_ = type_
        self.label_str = label_str
        self.connections = []
        self.item = None


    def get_val(self):
        pass

    def connected(self):
        self.has_been_connected.emit()

    def disconnected(self):
        self.has_been_disconnected.emit()

    def config_data(self):
        data_dict = {'type': self.type_,
                     'label': self.label_str}

        return data_dict


class NodeObjInput(NodeObjPort):
    def __init__(self, node, type_, label_str='', widget_name=None, widget_pos='besides', config_data=None):
        super().__init__(node, PortObjPos.INPUT, type_, label_str)

        self.widget_name = widget_name
        self.widget_pos = widget_pos
        self.widget_config_data = config_data

        self.item = None  # InputPortItem


    def connected(self):
        super().connected()
        if self.type_ == 'data':
            self.node.update(self.node.inputs.index(self))

    def get_val(self):
        if self.item is None:
            raise Exception(
                'The node item has not been initialized yet.'
            )

        InfoMsgs.write('getting value of input', self.node.inputs.index(self), 'of', self.node.title, 'node')

        if len(self.connections) == 0:
            if self.item.widget:
                return self.item.widget.get_val()
            else:
                return None
        else:
            if self.node.flow.alg_mode == FlowAlg.DATA and self.val is not None:
                return self.val
            else:
                return self.connections[0].get_val()

    def update(self, data=None):
        """called from another node or from connected()"""
        if self.type_ == 'data':
            self.val = data  # self.get_val()
            InfoMsgs.write('Data in input set to', data)
            if self.item:
                self.item.updated_val()

        if (self.node.is_active() and self.type_ == 'exec') or \
           not self.node.is_active():
            self.node.update(self.node.inputs.index(self))

    def config_data(self, include_val=False):
        data = super().config_data()
        if include_val:
            data['val'] = serialize(self.get_val())
        return data



class NodeObjOutput(NodeObjPort):
    def __init__(self, node, type_, label_str=''):
        super().__init__(node, PortObjPos.OUTPUT, type_, label_str)

        self.item = None  # OutputPortItem(node, self)

    def exec(self):
        for c in self.connections:
            c.activate()

    def get_val(self):
        InfoMsgs.write('getting value in output', self.node.outputs.index(self), 'of', self.node.title, 'node')

        if self.node.flow.alg_mode == FlowAlg.EXEC:
            self.node.update()
        return self.val

    def set_val(self, val):

        # note that val COULD be of complex type and therefore already changed because the original object might have
        self.val = val

        # if algorithm mode is exec flow, all data will be 'required' at outputs instead of actively forward propagated
        if self.node.flow.alg_mode == FlowAlg.DATA:
            for c in self.connections:
                c.activate(data=val)

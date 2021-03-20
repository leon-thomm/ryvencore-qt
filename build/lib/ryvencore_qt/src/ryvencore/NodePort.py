from .Base import Base, Signal

from .RC import PortObjPos, FlowAlg
from .tools import serialize
from .InfoMsgs import InfoMsgs


class NodePort(Base):
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


    def get_val(self):
        pass

    def connected(self):
        self.has_been_connected.emit()

    def disconnected(self):
        self.has_been_disconnected.emit()

    def config_data(self):
        data_dict = {
            'type': self.type_,
            'label': self.label_str
        }

        return data_dict


class NodeInput(NodePort):

    val_updated = Signal(object)

    def __init__(self, node, type_, label_str='', add_config=None):
        super().__init__(node, PortObjPos.INPUT, type_, label_str)

        # add_config can be used to store additional config data for enhanced input ports
        self.add_config = add_config

    def disconnected(self):
        super().disconnected()
        if self.type_ == 'data' and self.node.flow.alg_mode == FlowAlg.DATA:
            self.node.update(self.node.inputs.index(self))

    def get_val(self):
        InfoMsgs.write('getting value of node input')

        if self.node.flow.alg_mode == FlowAlg.DATA and self.val is not None:  # TODO: change this
            return self.val
        else:
            return self.connections[0].get_val()

    def update(self, data=None):
        """called from another node or from connected()"""
        if self.type_ == 'data':
            self.val = data  # self.get_val()
            InfoMsgs.write('Data in input set to', data)

            self.val_updated.emit(self.val)

        self.node.update(input_called=self.node.inputs.index(self))

    def config_data(self, include_val=False):
        data = super().config_data()
        if include_val:
            data['val'] = serialize(self.get_val())
        return data



class NodeOutput(NodePort):
    def __init__(self, node, type_, label_str=''):
        super().__init__(node, PortObjPos.OUTPUT, type_, label_str)

    def exec(self):
        for c in self.connections:
            c.activate()

    def get_val(self):
        InfoMsgs.write('getting value in node output')

        if self.node.flow.alg_mode == FlowAlg.EXEC:
            self.node.update()
        return self.val

    def set_val(self, val):

        # in case val isn't of complex type
        self.val = val

        if self.node.flow.alg_mode == FlowAlg.DATA:
            for c in self.connections:
                c.activate(data=val)

    def connected(self):
        super().connected()
        if self.type_ == 'data' and self.node.flow.alg_mode == FlowAlg.DATA:
            self.set_val(self.val)  # update output

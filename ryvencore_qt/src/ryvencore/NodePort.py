from .Base import Base

from .RC import PortObjPos, FlowAlg
from .dtypes import DType
from .tools import serialize
from .InfoMsgs import InfoMsgs


class NodePort(Base):
    """The base class for inputs and outputs of nodes with basic functionality."""

    def __init__(self, node, io_pos, type_, label_str):
        Base.__init__(self)

        self.val = None
        self.node = node
        self.io_pos = io_pos
        self.type_ = type_
        self.label_str = label_str
        self.connections = []


    def get_val(self):
        pass

    def connected(self):
        pass

    def disconnected(self):
        pass

    def flow_alg_data_mode(self):
        return self.node.flow.alg_mode in (FlowAlg.DATA, FlowAlg.DATA_OPT)

    def data(self) -> dict:
        data_dict = {
            'type': self.type_,
            'label': self.label_str
        }

        return data_dict


class NodeInput(NodePort):

    def __init__(self, node, type_, label_str='', add_data=None, dtype: DType = None):
        super().__init__(node, PortObjPos.INPUT, type_, label_str)

        # data can be used to store additional data for enhanced data input ports
        self.add_data = add_data

        # optional dtype
        self.dtype: DType = dtype

    def connected(self):
        super().connected()
        self.val = self.connections[0].get_val()
        if self.type_ == 'data' and self.flow_alg_data_mode():
            self.node.update(self.node.inputs.index(self))

    def disconnected(self):
        super().disconnected()
        if self.type_ == 'data' and self.flow_alg_data_mode():
            self.node.update(self.node.inputs.index(self))

    def get_val(self):
        InfoMsgs.write('getting value of node input')

        if self.flow_alg_data_mode() or len(self.connections) == 0:
            return self.val
        else:  # len(self.connections) > 0:
            return self.connections[0].get_val()

    def update(self, data=None):
        """called from another node or from connected()"""
        if self.type_ == 'data':
            self.val = data  # self.get_val()
            InfoMsgs.write('Data in input set to', data)

        self.node.update(inp=self.node.inputs.index(self))

    def data(self) -> dict:
        data = super().data()

        if len(self.connections) == 0:
            data['val'] = serialize(self.get_val())

        if self.dtype:
            data['dtype'] = str(self.dtype)
            data['dtype state'] = serialize(self.dtype.get_state())

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
        InfoMsgs.write('setting value in node output')

        self.val = val

        if self.flow_alg_data_mode():
            for c in self.connections:
                c.activate(data=val)

    # def connected(self):
    #     super().connected()
    #     if self.type_ == 'data' and self.node.flow.alg_mode == FlowAlg.DATA:
    #         self.set_val(self.val)  # update output

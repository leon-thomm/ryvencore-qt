from .dtypes import DType


class NodePortBP:
    """
    The NodePorts (NodeInputs and NodeOutputs) are only placeholders for the static init_input and init_outputs of
    custom Node classes.
    An instantiated Node's actual inputs and outputs will be of type NodeObjPort (NodeObjInput, NodeObjOutput).
    """

    def __init__(self,
                 type_: str = 'data',
                 label: str = ''):
        """
        :type_: 'data' or 'exec'
        """

        self.type_: str = type_
        self.label: str = label


class NodeInputBP(NodePortBP):
    def __init__(self,
                 type_: str = 'data',
                 label: str = '',
                 dtype: DType = None,
                 add_config={}):

        super().__init__(type_, label)

        self.dtype = dtype
        self.add_config = add_config


class NodeOutputBP(NodePortBP):
    def __init__(self,
                 type_: str = 'data',
                 label: str = ''):
        super().__init__(type_, label)

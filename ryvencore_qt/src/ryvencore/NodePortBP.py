from .dtypes import DType

# TODO: make this a dataclass
class NodePortBP:
    """
    The NodePortBPs (NodeInputs and NodeOutputs) are only placeholders (BluePrints) for the static init_input and
    init_outputs of custom Node classes.
    An instantiated Node's actual inputs and outputs will be of type NodeObjPort (NodeObjInput, NodeObjOutput).
    """

    def __init__(self, label: str = '', type_: str = 'data'):

        self.type_: str = type_
        self.label: str = label


class NodeInputBP(NodePortBP):
    def __init__(self, label: str = '', type_: str = 'data', dtype: DType = None, add_data={}):
        super().__init__(label, type_)

        self.dtype = dtype
        self.add_data = add_data


class NodeOutputBP(NodePortBP):
    def __init__(self, label: str = '', type_: str = 'data'):
        super().__init__(label, type_)

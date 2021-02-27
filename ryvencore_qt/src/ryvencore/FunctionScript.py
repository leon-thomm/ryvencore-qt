from .Script import Script
from .FunctionNodeTypes import FunctionInputNode, FunctionOutputNode, FunctionScriptNode


class FunctionScript(Script):
    """Besides all the properties of a Script, a FunctionScript automatically create an input node and an output node
    in the Flow, and locally defines a new Node class and registers it in the session."""

    def __init__(self, session, title: str = None, config_data: dict = None, flow_view_size: list = None,
                 create_default_logs=True):

        super().__init__(session, title, config_data, flow_view_size, create_default_logs,
                         False)  # initialization blocked here!


        _self = self

        class CustomFunctionScriptNode(FunctionScriptNode):

            identifier = 'FUNCTION_NODE_'+_self.title
            # notice that script titles have to be unique!
            # and the script's title has already been set in Script.__init__

            title = _self.title

            # it is important that these two static attributes are defined here ant NOT in FunctionScriptNode
            # otherwise they would result in the same for ALL FunctionScriptNodes
            function_script = _self
            instances = []

        self.function_node_class = CustomFunctionScriptNode
        self.session.register_node(self.function_node_class)

        self.input_node, self.output_node = None, None
        self.parameters: [dict] = []
        self.returns: [dict] = []
        self.caller_stack: [FunctionScriptNode] = []  # used by input, output and function nodes


    def initialize(self):
        if self.init_config:
            self.parameters = self.init_config['parameters']
            self.returns = self.init_config['returns']

        super().initialize()

        if self.init_config:
            # find input and output node that have already been created by the flow
            for node in self.flow.nodes:
                if node.identifier == FunctionInputNode.identifier:
                    self.input_node = node
                elif node.identifier == FunctionOutputNode.identifier:
                    self.output_node = node
        else:
            self.input_node = self.flow.create_node(FunctionInputNode)
            self.output_node = self.flow.create_node(FunctionOutputNode)


    def add_parameter(self, type_, label):
        self.parameters.append({'type': type_, 'label': label})

        for fn in self.function_node_class.instances:
            fn: FunctionScriptNode
            fn.create_input(type_, label)

    def remove_parameter(self, index):
        self.parameters.remove(self.parameters[index])

        for fn in self.function_node_class.instances:
            fn: FunctionScriptNode
            fn.delete_input(index)

    def add_return(self, type_, label):
        self.returns.append({'type': type_, 'label': label})

        for fn in self.function_node_class.instances:
            fn: FunctionScriptNode
            fn.create_output(type_, label)

    def remove_return(self, index):
        self.returns.remove(self.returns[index])

        for fn in self.function_node_class.instances:
            fn: FunctionScriptNode
            fn.delete_output(index)

    def serialize(self) -> dict:
        script_dict = super().serialize()

        script_dict['parameters'] = self.parameters
        script_dict['returns'] = self.returns

        return script_dict

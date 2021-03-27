from .Script import Script
from .RC import CLASSES
from .FunctionNodeTypes import build_function_classes


class FunctionScript(Script):
    """Besides all the properties of a Script, a FunctionScript automatically create an input node and an output node
    in the Flow, and locally defines a new Node class and registers it in the session."""

    ID_ctr = 0  # ensures I don't need to change the func node class's identifier when script name is changed
    # the ID gets stored when serializing and is reloaded in a way that the ID_ctr will afterwards still be larger than
    # any ID used, even if there were func scripts deleted which created holes in the id assignments

    FunctionInputNode, FunctionOutputNode, FunctionScriptNode = None, None, None

    @staticmethod
    def build_node_classes():
        FunctionScript.FunctionInputNode, FunctionScript.FunctionOutputNode, FunctionScript.FunctionScriptNode = \
            build_function_classes(BaseClass=CLASSES['node base'])


    def __init__(self, session, title: str = None, config_data: dict = None, create_default_logs=True):

        self.input_node, self.output_node = None, None
        self.parameters: [dict] = []
        self.returns: [dict] = []
        self.caller_stack = []  # : [FunctionScriptNode]; used by input, output and function nodes

        if config_data and 'ID' in config_data:
            self.ID = max(config_data['ID'], self.ID_ctr)
        else:
            self.ID = self.ID_ctr
        self.ID_ctr = self.ID + 1

        super().__init__(session, title, config_data, create_default_logs)

        _self = self

        class CustomFunctionScriptNode(_self.FunctionScriptNode):

            identifier = _self.func_node_identifier()

            title = _self.title

            # it is important that these two static attributes are defined here ant NOT in FunctionScriptNode
            # otherwise they would result in the same for ALL FunctionScriptNodes
            function_script = _self
            instances = []

        self.function_node_class = CustomFunctionScriptNode
        self.session.register_node(self.function_node_class)

        if self.init_config:
            self.parameters = self.init_config['parameters']
            self.returns = self.init_config['returns']


    def func_node_identifier(self):
        # not using the script title here anymore, because although it's unique, it can change
        return f'FUNCTION_NODE_{self.ID}'


    def load_flow(self):
        super().load_flow()

        if self.init_config:
            # find input and output node that have already been created by the flow
            for node in self.flow.nodes:
                if node.identifier == self.FunctionInputNode.identifier:
                    self.input_node = node
                elif node.identifier == self.FunctionOutputNode.identifier:
                    self.output_node = node
        else:
            self.input_node = self.flow.create_node(self.FunctionInputNode)
            self.output_node = self.flow.create_node(self.FunctionOutputNode)


    def add_parameter(self, type_, label):
        self.parameters.append({'type': type_, 'label': label})

        for fn in self.function_node_class.instances:
            fn.create_input(type_, label)

    def remove_parameter(self, index):
        self.parameters.remove(self.parameters[index])

        for fn in self.function_node_class.instances:
            fn.delete_input(index)

    def add_return(self, type_, label):
        self.returns.append({'type': type_, 'label': label})

        for fn in self.function_node_class.instances:
            fn.create_output(type_, label)

    def remove_return(self, index):
        self.returns.remove(self.returns[index])

        for fn in self.function_node_class.instances:
            fn.delete_output(index)

    def serialize(self) -> dict:
        script_dict = super().serialize()

        script_dict['parameters'] = self.parameters
        script_dict['returns'] = self.returns
        script_dict['ID'] = self.ID

        return script_dict

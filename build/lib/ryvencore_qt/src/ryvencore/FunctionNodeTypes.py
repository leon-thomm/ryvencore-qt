"""The implementations for the special nodes of functions."""
from .RC import FlowAlg
from .InfoMsgs import InfoMsgs


def build_function_classes(BaseClass):

    class FunctionInputNode(BaseClass):
        """The input node of a function script"""

        identifier = 'BUILTIN_FunctionInputNode'
        title = 'input'
        type_ = 'BUILT-IN func input node'

        def __init__(self, params):
            super().__init__(params)

            self.special_actions = {
                'add parameter': {
                    'data': {'method': self.add_function_param, 'data': 'data'},
                    'exec': {'method': self.add_function_param, 'data': 'exec'}
                },
                'remove parameter': {

                }
            }

        def add_function_param(self, type_):
            self.create_output(type_, '')

            self.special_actions['remove parameter'][str(len(self.outputs))] = {
                'method': self.remove_function_param,
                'data': len(self.outputs)-1
            }

            self.script.add_parameter(type_, '')

        def remove_function_param(self, index):
            self.delete_output(index)
            self.rebuild_remove_actions()
            self.script.remove_parameter(index)

        def rebuild_remove_actions(self):
            del self.special_actions['remove parameter']
            self.special_actions['remove parameter'] = {
                str(o+1): {'method': self.remove_function_param, 'data': o} for o in range(len(self.outputs))
            }

        # def update_event(self, input_called=-1):
        #     InfoMsgs.write('update in function input node with output values:', [o.val for o in self.outputs])
        #
        #     if len(self.script.caller_stack) == 0:
        #         return
        #
        #     if input_called == -1:  # for exec flows
        #         caller = self.script.caller_stack[-1]
        #         for i in range(len(caller.inputs)):
        #             self.set_output_val(i, caller.input(i))

        def propagate_output_values(self, values):
            self.script.output_node.hold_values()

            affected_inputs = set()

            for o in range(len(self.outputs)):
                out = self.outputs[o]
                if out.type_ == 'data':
                    for c in out.connections:
                        if c.inp.val != values[o]:
                            # affected
                            affected_inputs.add(c.inp)
                    self.outputs[o].val = values[o]

            for inp in affected_inputs:
                inp.update(inp.val)

            self.script.output_node.release_values()

        def get_data(self) -> dict:
            return {

            }

        def set_data(self, data: dict):
            pass


    class FunctionOutputNode(BaseClass):
        """The output node of a function script"""

        identifier = 'BUILTIN_FunctionOutputNode'
        title = 'output'
        type_ = 'BUILT-IN func output node'

        def __init__(self, params):
            super().__init__(params)

            self.special_actions = {
                'add return': {
                    'data': {'method': self.add_function_return, 'data': 'data'},
                    'exec': {'method': self.add_function_return, 'data': 'exec'}
                },
                'remove return': {

                }
            }

            self.held_values = {}
            self.holding_values = False

        def add_function_return(self, type_):
            self.create_input(type_)

            self.special_actions['remove return'][str(len(self.inputs))] = {
                'method': self.remove_function_return,
                'data': len(self.inputs)-1
            }

            self.script.add_return(type_, '')

        def remove_function_return(self, index):
            self.delete_input(index)
            self.rebuild_remove_actions()
            self.script.remove_return(index)

        def rebuild_remove_actions(self):
            del self.special_actions['remove return']
            self.special_actions['remove return'] = {
                str(i+1): {'method': self.remove_function_return, 'data': i} for i in range(len(self.inputs))
            }

        def update_event(self, input_called=-1):
            if len(self.script.caller_stack) == 0:
                return

            caller = self.script.caller_stack[-1]

            if input_called == -1:
                for i in range(len(self.inputs)):
                    caller.set_output_val(i, self.input(i))

            else:
                if self.inputs[input_called].type_ == 'data':
                    if self.holding_values:
                        self.held_values[self.inputs[input_called]] = self.input(input_called)
                    # else:
                    #     caller.set_output_val(input_called, self.input(input_called))
                else:
                    caller.exec_output(input_called)

        def hold_values(self):
            self.held_values = {inp : None for inp in self.inputs}
            self.holding_values = True

        def release_values(self):
            caller = self.script.caller_stack[-1]
            for i in range(len(self.inputs)):
                inp = self.inputs[i]
                if inp.type_ == 'data':
                    caller.set_output_val(i, inp.val)


    class FunctionScriptNode(BaseClass):
        """The function node of a function script"""

        type_ = 'BUILT-IN func node'

        def __init__(self, params):
            super().__init__(params)

            self.instances.append(self)

            if not self.init_config:
                # catch up on params and returns
                for p in self.function_script.parameters:
                    self.create_input(p['type'], p['label'])
                for r in self.function_script.returns:
                    self.create_output(r['type'], r['label'])

        def update_event(self, input_called=-1):
            if input_called != -1:

                self.function_script.caller_stack.append(self)

                if self.flow.alg_mode == FlowAlg.DATA:
                    values = [self.input(i) for i in range(len(self.inputs))]
                    InfoMsgs.write('sending propagation values to input node', values)
                    self.function_script.input_node.propagate_output_values(values)

                    # if somebody wants to use exec inputs in a data flow for some reason
                    if self.inputs[input_called].type_ == 'exec':
                        self.function_script.input_node.exec_output(input_called)
                else:
                    # manually set output values of input node
                    for i in range(len(self.inputs)):
                        if self.inputs[i].type_ == 'data':
                            self.function_script.input_node.outputs[i].val = self.input(i)
                    self.function_script.input_node.exec_output(input_called)

                self.function_script.caller_stack.pop()

            else:
                self.function_script.caller_stack.append(self)
                self.function_script.output_node.update()
                self.function_script.caller_stack.pop()

        def get_data(self):
            data = {'title': self.function_script.title}
            return data

        def set_data(self, data: dict):
            # find parent function script by unique title
            for fs in self.session.function_scripts:
                if fs.title == data['title']:
                    self.function_script = fs
                    break


    return FunctionInputNode, FunctionOutputNode, FunctionScriptNode

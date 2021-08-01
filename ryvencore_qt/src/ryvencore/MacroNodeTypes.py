"""The implementations for the special nodes of macros."""
from .RC import FlowAlg
from .InfoMsgs import InfoMsgs


def build_macro_classes(BaseClass):

    class MacroInputNode(BaseClass):
        """The input node of a macro script"""

        identifier = 'BUILTIN_MacroInputNode'
        title = 'input'
        type_ = 'BUILT-IN macro input node'

        def __init__(self, params):
            super().__init__(params)

            self.actions = {
                'add parameter': {
                    'data': {'method': self.add_macro_param, 'data': 'data'},
                    'exec': {'method': self.add_macro_param, 'data': 'exec'}
                },
                'remove parameter': {

                }
            }

        def add_macro_param(self, type_):
            self.create_output(type_=type_, label='')

            i = len(self.outputs)-1
            self.actions['remove parameter'][str(i)] = {
                'method': self.remove_macro_param,
                'data': i
            }

            self.script.add_parameter(type_, '')

        def remove_macro_param(self, index):
            self.delete_output(index)
            # self.rebuild_remove_actions()
            del self.actions['remove parameter'][str(index)]
            self.script.remove_parameter(index)

        # def rebuild_remove_actions(self):
        #     del self.actions['remove parameter']
        #     self.actions['remove parameter'] = {
        #         str(o+1): {'method': self.remove_macro_param, 'data': o} for o in range(len(self.outputs))
        #     }

        def propagate_output_values(self, values):
            self.script.output_node.hold_values()

            affected_connections = {}

            for o in range(len(self.outputs)):
                out = self.outputs[o]
                if out.type_ == 'data':
                    for c in out.connections:
                        if c.inp.val != values[o]:
                            # affected
                            affected_connections[c] = values[o]
                    self.outputs[o].val = values[o]

            for c, v in affected_connections.items():
                c.activate(v)

            self.script.output_node.release_values()


    class MacroOutputNode(BaseClass):
        """The output node of a macro script"""

        identifier = 'BUILTIN_MacroOutputNode'
        title = 'output'
        type_ = 'BUILT-IN macro output node'

        def __init__(self, params):
            super().__init__(params)

            self.actions = {
                'add return': {
                    'data': {'method': self.add_macro_return, 'data': 'data'},
                    'exec': {'method': self.add_macro_return, 'data': 'exec'}
                },
                'remove return': {

                }
            }

            self.held_values = {}
            self.holding_values = False
            # Basically a barrier.
            # Holding values means data input updates are not propagated
            # to the caller macro node until release_values() is called.
            # This is a nice feature for macros which allows the user
            # to split connections inside a macro (and therefore producing
            # multiple execution branches) but join all the updates again
            # in the end.
            # It is coordinated by the input node above.

        def add_macro_return(self, type_):
            self.create_input(type_=type_, label='')

            i = len(self.inputs)-1
            self.actions['remove return'][str(i)] = {
                'method': self.remove_macro_return,
                'data': i
            }

            self.script.add_return(type_, '')

        def remove_macro_return(self, index):
            self.delete_input(index)
            # self.rebuild_remove_actions()
            del self.actions['remove return'][str(index)]
            self.script.remove_return(index)

        # def rebuild_remove_actions(self):
        #     del self.actions['remove return']
        #     self.actions['remove return'] = {
        #         str(i+1): {'method': self.remove_macro_return, 'data': i} for i in range(len(self.inputs))
        #     }

        def update_event(self, inp=-1):
            # if len(self.script.caller_stack) == 0:
            #     return

            # caller = self.script.caller_stack[-1]

            if not self.script.caller:
                return

            caller = self.script.caller

            if inp == -1:  # requested data in exec flow
                for i in range(len(self.inputs)):
                    v = self.input(i)
                    if v != caller.outputs[i].val:  # only update if value is new
                        caller.set_output_val(i, v)

            else:   # data propagation in data flow or exec signal in exec flow
                if self.inputs[inp].type_ == 'data':
                    if self.holding_values:
                        self.held_values[self.inputs[inp]] = self.input(inp)
                else:
                    caller.exec_output(inp)

        def hold_values(self):
            self.held_values = {inp: None for inp in self.inputs}
            self.holding_values = True

        def release_values(self):
            # caller = self.script.caller_stack[-1]
            caller = self.script.caller
            for i in range(len(self.inputs)):
                inp = self.inputs[i]
                if inp.type_ == 'data':
                    v = inp.val
                    if v != caller.outputs[i].val:  # only update if value is new
                        caller.set_output_val(i, inp.val)


    class MacroScriptNode(BaseClass):
        """The macro node of a macro script"""

        type_ = 'BUILT-IN macro node'

        def __init__(self, params):
            super().__init__(params)

            self.instances.append(self)  # defined statically in the custom macro node class

            if not self.init_data:
                # catch up on params and returns
                for p in self.macro_script.parameters:
                    self.create_input(type_=p['type'], label=p['label'])
                for r in self.macro_script.returns:
                    self.create_output(type_=r['type'], label=r['label'])

        def update_event(self, inp=-1):

            self.macro_script.caller = self

            if inp != -1:

                # self.macro_script.caller_stack.append(self)

                if self.flow.alg_mode == FlowAlg.DATA:
                    values = [inp.val for inp in self.inputs]
                    InfoMsgs.write('sending propagation values to input node', values)
                    self.macro_script.input_node.propagate_output_values(values)

                    # if somebody wants to use exec inputs in a data flow for some reason
                    if self.inputs[inp].type_ == 'exec':
                        self.macro_script.input_node.exec_output(inp)
                else:
                    # manually set output values of input node
                    for i in range(len(self.inputs)):
                        if self.inputs[i].type_ == 'data':
                            self.macro_script.input_node.outputs[i].val = self.inputs[i].val
                    self.macro_script.input_node.exec_output(inp)

                # self.macro_script.caller_stack.pop()

            else:
                # self.macro_script.caller_stack.append(self)
                self.macro_script.output_node.update()
                # self.macro_script.caller_stack.pop()

            self.macro_script.caller = None

        def get_state(self):
            data = {'title': self.macro_script.title}  # script title are unique
            return data

        def set_state(self, data: dict):
            # find parent macro script by unique title
            for ms in self.session.macro_scripts:
                if ms.title == data['title']:
                    self.macro_script = ms
                    break


    return MacroInputNode, MacroOutputNode, MacroScriptNode

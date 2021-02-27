from PySide2.QtCore import QObject, Signal

from .NodeObjPort import NodeObjInput, NodeObjOutput
from .NodePort import NodeInput, NodeOutput
from .logging.Log import Log
from .retain import M
from .InfoMsgs import InfoMsgs
from .tools import serialize, deserialize


class Node(QObject):
    """Base class for all node blueprints. Such a blueprint is defined by its class, which is registered
    in the session, and actual node objects are instances of it. The static properties are stored using
    static attributes, which works really well in Python.
    All the main API for programming nodes, i.e. creating subclasses of this class, is defined here."""

    # SIGNALS
    updated = Signal()
    update_shape_triggered = Signal()
    hide_unused_ports_triggered = Signal()
    show_unused_ports_triggered = Signal()
    input_added = Signal(NodeObjInput, int)
    output_added = Signal(NodeObjOutput, int)
    input_removed = Signal(NodeObjInput)
    output_removed = Signal(NodeObjOutput)

    # STATIC FIELDS
    title = ''
    # display_title = ''  TODO: Node display_title
    type_ = ''
    init_inputs: [NodeInput] = []
    init_outputs: [NodeOutput] = []
    identifier: str = None  # set by Session if None
    description: str = ''
    description_html: str = None
    main_widget_class: list = None
    main_widget_pos: str = 'below ports'
    input_widget_classes: dict = {}
    style: str = 'extended'
    color: str = '#c69a15'
    icon: str = None

    class SIGNALS(QObject):
        """A class for defining QT signals to communicate with GUI components safely in threaded environments.
        I wanted to do it this way to enable Qt independent source code generation in the future."""
        pass

    def __init__(self, params):
        super().__init__()

        self.flow, design, config = params
        self.script = self.flow.script
        self.session = self.script.session
        self.inputs: [NodeInput] = []
        self.outputs: [NodeOutput] = []
        self.default_actions = self.init_default_actions()
        self.special_actions = {}
        self.logs = []
        self.signals = self.SIGNALS()
        # self.display_title = self.title

        self.init_config = config
        self.initialized = False

        self.item = None  # set by the flow view

    def finish_initialization(self):
        """Loads the initial config if it was provided, set up all inputs and outputs, enables the logs and calls
        self._initialized() for subclasses"""

        if self.init_config:
            self.setup_ports(self.init_config['inputs'], self.init_config['outputs'])

            self.special_actions = self.set_special_actions_data(self.init_config['special actions'])

        else:
            self.setup_ports()

        self.enable_logs()

        self._initialized()

        self.initialized = True

        # self.update()

    def load_config_data(self):
        """Loads the component-specific config data that was returned by get_data() previously; prints an exception
        if it fails but doesn't crash, as this always happens when developing nodes"""

        if self.init_config:
            try:
                if type(self.init_config['state data']) == dict:  # backwards compatibility
                    self.set_data(self.init_config['state data'])
                else:
                    self.set_data(deserialize(self.init_config['state data']))
            except Exception as e:
                print('Exception while setting data in', self.title, 'Node:', e,
                      ' (was this intended?)')

    def init_default_actions(self) -> dict:
        return {
            'update shape': {'method': self.update_shape},
            'hide unused ports': {'method': self.hide_unused_ports}
        }

    def setup_ports(self, inputs_config=None, outputs_config=None):

        if not inputs_config and not outputs_config:
            for i in range(len(self.init_inputs)):
                inp = self.init_inputs[i]
                self.create_input(
                    inp.type_, inp.label,
                    widget_name=self.init_inputs[i].widget_name,
                    widget_pos =self.init_inputs[i].widget_pos
                )

            for o in range(len(self.init_outputs)):
                out = self.init_outputs[o]
                self.create_output(out.type_, out.label)

        else:  # when loading saved Nodes, the init_inputs and init_outputs are irrelevant
            for inp in inputs_config:
                has_widget = inp['has widget'] if inp['type'] == 'data' else False

                self.create_input(
                    type_=inp['type'], label=inp['label'],
                    widget_name=inp['widget name'] if has_widget else None,
                    widget_pos =inp['widget position'] if has_widget else None,
                    config=inp['widget data'] if has_widget else None
                )

            for out in outputs_config:
                self.create_output(out['type'], out['label'])

    def main_widget(self):
        return self.item.main_widget




    #                        __                             _    __     __
    #              ____ _   / /  ____ _   ____     _____   (_)  / /_   / /_     ____ ___
    #             / __ `/  / /  / __ `/  / __ \   / ___/  / /  / __/  / __ \   / __ `__ \
    #            / /_/ /  / /  / /_/ /  / /_/ /  / /     / /  / /_   / / / /  / / / / / /
    #            \__,_/  /_/   \__, /   \____/  /_/     /_/   \__/  /_/ /_/  /_/ /_/ /_/
    #                         /____/


    def update(self, input_called=-1, output_called=-1):
        """'Activates' the node, causing an update_event(); prints an exception if something crashed, but prevents
        the application from crashing in such a case"""

        InfoMsgs.write('update in', self.title, 'on input', input_called)

        try:
            self.update_event(input_called)
            self.updated.emit()
        except Exception as e:
            InfoMsgs.write_err('EXCEPTION IN', self.title, 'NI:', e)

    def update_event(self, input_called=-1):
        """Gets called when an input received a signal or some node requested data of an output in exec mode"""

        pass

    def input(self, index: int):
        """Returns the value of a data input.
        If the input is connected, the value of the connected output is used:
        If not, the value of the widget is used."""

        InfoMsgs.write('input called in', self.title, 'Node:', index)
        return self.inputs[index].get_val()

    def input_widget(self, index: int):
        """Returns a reference to the widget of the corresponding input"""

        return self.inputs[index].item.widget

    def exec_output(self, index: int):
        """Executes an exec output, causing activation of all connections"""

        self.outputs[index].exec()

    def set_output_val(self, index, val):
        """Sets the value of a data output causing activation of all connections in data mode"""

        self.outputs[index].set_val(val)

    def place_event(self):
        """Called once the GUI item for the node has been created and placed in the scene and therefore all
        widgets have been created"""

        pass

    def remove_event(self):
        """Called when the node is removed from the flow, useful for stopping threads and timers, etc."""

        pass

    #                                 _
    #              ____ _   ____     (_)
    #             / __ `/  / __ \   / /
    #            / /_/ /  / /_/ /  / /
    #            \__,_/  / .___/  /_/
    #                   /_/


    def _initialized(self):
        """Called after the node has been initialized and the GUI item has been created."""

        pass


    # LOGGING


    def new_log(self, title) -> Log:
        """Requesting a new custom Log"""

        # new_log = self.script.logger.new_log(self, title)
        new_log = self.script.logger.new_log(title)
        self.logs.append(new_log)
        return new_log

    def disable_logs(self):
        """Disables custom Logs"""

        for log in self.logs:
            log.disable()

    def enable_logs(self):
        """Enables custom logs"""

        for log in self.logs:
            log.enable()

    def log_message(self, msg: str, target: str):
        """Writes a message string to a default script log with title target"""

        self.script.logger.log_message(msg, target)


    # SHAPE


    def update_shape(self):
        """Causes recompilation of the whole shape of the GUI item."""

        # self.item.update_shape()
        self.update_shape_triggered.emit()

    def hide_unused_ports(self):
        """Causes the GUI item to hide all unconnected ports"""

        del self.default_actions['hide unused ports']
        self.default_actions['show unused ports'] = {'method': self.show_unused_ports}
        self.hide_unused_ports_triggered.emit()

    def show_unused_ports(self):
        """Causes the GUI item to show all unconnected ports that have been hidden previously"""

        del self.default_actions['show unused ports']
        self.default_actions['hide unused ports'] = {'method': self.hide_unused_ports}
        self.show_unused_ports_triggered.emit()


    # PORTS


    def create_input(self, type_: str = 'data', label: str = '', widget_name=None,
                     widget_pos='besides', pos=-1, config=None):
        """
        Creates and adds a new input, possible positions for widgets are 'besides' and 'below
        """
        InfoMsgs.write('create_new_input called')

        # backwards compatibility
        widget_pos = widget_pos if widget_pos != 'under' else 'below'

        inp = NodeObjInput(
            node=self,
            type_=type_,
            label_str=label,
            widget_name=widget_name,
            widget_pos=widget_pos,
            config_data=config
        )

        if pos < -1:
            pos += len(self.inputs)
        if pos == -1:
            self.inputs.append(inp)
        else:
            self.inputs.insert(pos, inp)

        # self.item.add_new_input(inp, pos)
        self.input_added.emit(inp, pos)


    def delete_input(self, i):
        """Disconnects and removes input"""

        inp: NodeObjInput = None
        if type(i) == int:
            inp = self.inputs[i]
        elif type(i) == NodeObjInput:
            inp = i

        # break all connections
        for c in inp.connections:
            self.flow.connect_nodes(c.out, inp)

        self.inputs.remove(inp)
        # self.item.remove_input(inp)
        self.input_removed.emit(inp)


    def create_output(self, type_: str = 'data', label: str = '', pos=-1):
        """Creates and adds a new output"""

        out = NodeObjOutput(
              node=self,
              type_=type_,
              label_str=label
        )

        # pi = OutputPortInstance(self, type_, label)
        if pos < -1:
            pos += len(self.outputs)
        if pos == -1:
            self.outputs.append(out)
        else:
            self.outputs.insert(pos, out)

        # self.item.add_new_output(out, pos)
        self.output_added.emit(out, pos)

        # if self.session.threaded:
        #     out.moveToThread(self.flow.worker_thread)

    def delete_output(self, o):
        """Disconnects and removes output"""

        out: NodeObjOutput = None
        if type(o) == int:
            out = self.outputs[o]
        elif type(o) == NodeObjOutput:
            out = o

        # break all connections
        for c in out.connections:
            self.flow.connect_nodes(out, c.inp)

        self.outputs.remove(out)
        # self.item.remove_output(out)
        self.output_removed.emit(out)


    # GET, SET DATA


    def get_data(self) -> dict:
        """
        Used to store node-specific custom data that needs to be reloaded when loading a project or pasting copied
        components. All values will be serialized by pickle and base64. The corresponding method for the opposite
        operation is set_data().
        """
        return {}

    def set_data(self, data: dict):
        """
        Used for reloading node-specific custom data which has been previously returned by get_data()
        """
        pass

    def session_stylesheet(self) -> str:
        """Returns the registered stylesheet of the session"""

        return self.session.design.global_stylesheet


    # VARIABLES


    def get_vars_manager(self):
        """Returns a ref to the script's variables manager"""

        return self.script.vars_manager

    def get_var_val(self, name: str):
        """Gets the value of a script variable"""

        return self.get_vars_manager().get_var_val(name)

    def set_var_val(self, name: str, val):
        """Sets the value of a script variable"""

        return self.get_vars_manager().set_var(name, val)

    def register_var_receiver(self, name: str, method):
        """Registers the node with given method as vars receiver in the script's variables manager to catch
        value changes of any variable with the given name"""

        self.get_vars_manager().register_receiver(self, name, method)

    def unregister_var_receiver(self, name: str):
        """Unregisters previously registered node as receiver for value changes of script variables with given name"""

        self.get_vars_manager().unregister_receiver(self, name)







    def set_special_actions_data(self, actions_data):
        actions = {}
        for key in actions_data:
            if type(actions_data[key]) != dict:
                if key == 'method':
                    try:
                        actions['method'] = M(getattr(self, actions_data[key]))
                    except AttributeError:  # outdated method referenced
                        pass
                elif key == 'data':
                    actions['data'] = actions_data[key]
            else:
                actions[key] = self.set_special_actions_data(actions_data[key])
        return actions


    def get_special_actions_data(self, actions):
        cleaned_actions = actions.copy()
        for key in cleaned_actions:
            v = cleaned_actions[key]
            if type(v) == M:  # callable(v):
                cleaned_actions[key] = v.method_name
            elif callable(v):
                cleaned_actions[key] = v.__name__
            elif type(v) == dict:
                cleaned_actions[key] = self.get_special_actions_data(v)
            else:
                cleaned_actions[key] = v
        return cleaned_actions

    def get_extended_default_actions(self):
        actions_dict = self.default_actions.copy()
        for index in range(len(self.inputs)):
            inp = self.inputs[index]
            if inp.type_ == 'exec':
                actions_dict['exec input '+str(index)] = {'method': self.action_exec_input,
                                                          'data': {'input index': index}}
        return actions_dict

    def action_exec_input(self, data):
        self.update(data['input index'])

    # def action_remove(self):
    #     self.flow.remove_node_item(self.item)

    def prepare_removal(self):
        """Called from Flow when the NI gets removed from the scene
        to stop all running threads and disable personal logs."""

        if self.main_widget():
            self.main_widget().remove_event()
        self.remove_event()

        self.disable_logs()

    def is_active(self):
        for i in self.inputs:
            if i.type_ == 'exec':
                return True
        for o in self.outputs:
            if o.type_ == 'exec':
                return True
        return False

    def has_main_widget(self):
        """Might be used later in CodePreview_Widget to enable not only showing the NI's class but also it's
        main_widget's class."""
        return self.main_widget() is not None


    def config_data(self, include_data_inp_values=False) -> dict:
        """Returns all metadata of the NI including position, package etc. in a JSON-able dict format.
        Used to rebuild the Flow when loading a project.
        include_data_inp_values is only used for code generation."""

        # general attributes
        node_dict = {
            'identifier': self.identifier,  # self.__class__.__name__,
            'state data': serialize(self.get_data()),
            'special actions': self.get_special_actions_data(self.special_actions)
        }

        # inputs
        inputs = []
        for i in self.inputs:
            input_dict = i.config_data(include_data_inp_values)
            inputs.append(input_dict)
        node_dict['inputs'] = inputs

        # outputs
        outputs = []
        for o in self.outputs:
            output_dict = o.config_data()
            outputs.append(output_dict)
        node_dict['outputs'] = outputs

        return node_dict

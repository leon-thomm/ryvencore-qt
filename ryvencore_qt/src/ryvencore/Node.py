
from .Base import Base

from .NodePort import NodeInput, NodeOutput
from .NodePortBP import NodeInputBP, NodeOutputBP
from .dtypes import DType
from .logging.Log import Log
from .InfoMsgs import InfoMsgs
from .tools import serialize, deserialize


class Node(Base):
    """Base class for all node blueprints. Such a blueprint is defined by its class, which is registered
    in the session, and actual node objects are instances of it. The static properties are stored using
    static attributes, which works really well in Python.
    All the main API for programming nodes, i.e. creating subclasses of this class, is defined here."""

    title = ''
    type_ = ''
    init_inputs: [NodeInputBP] = []
    init_outputs: [NodeOutputBP] = []
    identifier: str = None  # set by Session if None
    identifier_prefix: str = None
    doc: str = ''


    @classmethod
    def build_identifier(cls):

        full_prefix = (cls.identifier_prefix + '.') if cls.identifier_prefix is not None else ''

        if cls.identifier is None:
            cls.identifier = cls.__name__

        cls.identifier = full_prefix + cls.identifier


    def __init__(self, params):
        Base.__init__(self)

        self.flow, self.session, self.init_config = params
        self.script = self.flow.script
        self.inputs: [NodeInputBP] = []
        self.outputs: [NodeOutputBP] = []
        self.logs = []

        self.initialized = False

        self.block_init_updates = False
        self.block_updates = False

    def finish_initialization(self):
        """
        Loads all default properties from initial config if it was provided;
        sets up inputs and outputs, enables the logs, loads custom (std) config
        and calls self._initialized()
        """

        if self.init_config:
            self.setup_ports(self.init_config['inputs'], self.init_config['outputs'])

            self.load_custom_config(self.init_config)

        else:
            self.setup_ports()

        self.enable_logs()
        self._initialized()
        self.initialized = True

        # self.update()

    def load_user_config(self):
        """Loads the component-specific config data that was returned by get_state() previously; prints an exception
        if it fails but doesn't crash because that usually happens when developing nodes"""

        if self.init_config:
            try:
                if type(self.init_config['state data']) == dict:  # backwards compatibility
                    self.set_state(self.init_config['state data'])
                else:
                    self.set_state(deserialize(self.init_config['state data']))
            except Exception as e:
                InfoMsgs.write_err(
                    'Exception while setting data in', self.title, 'node:', e, ' (was this intended?)')


    def setup_ports(self, inputs_config=None, outputs_config=None):

        if not inputs_config and not outputs_config:
            for i in range(len(self.init_inputs)):
                inp = self.init_inputs[i]

                if inp.dtype:
                    self.create_input_dt(dtype=inp.dtype, label=inp.label, add_config=inp.add_config)

                else:
                    self.create_input(inp.type_, inp.label, add_config=self.init_inputs[i].add_config)

            for o in range(len(self.init_outputs)):
                out = self.init_outputs[o]
                self.create_output(out.type_, out.label)

        else:  # when loading saved nodes, the init_inputs and init_outputs are irrelevant
            for inp in inputs_config:
                if 'dtype' in inp:
                    self.create_input_dt(
                        dtype=DType.from_str(inp['dtype'])(_load_state=deserialize(inp['dtype state'])),
                        label=inp['label'], add_config=inp)
                else:
                    self.create_input(type_=inp['type'], label=inp['label'], add_config=inp)

                if 'val' in inp:
                    # this means the input is 'data' and did not have any connections,
                    # so we saved its value which was probably represented by some widget
                    # in the front end which has probably overridden the Node.input() method
                    self.inputs[-1].val = deserialize(inp['val'])

            for out in outputs_config:
                self.create_output(out['type'], out['label'])

    # -----------------------------------------------------------------------------------------------------------------

    def update(self, input_called=-1):  # , output_called=-1):
        """'Activates' the node, causing an update_event(); prints an exception if something crashed, but prevents
        the application from crashing in such a case"""

        if self.block_updates:
            InfoMsgs.write('update blocked in', self.title, 'node')
            return

        InfoMsgs.write('update in', self.title, 'node on input', input_called)

        try:
            self.update_event(input_called)
        except Exception as e:
            InfoMsgs.write_err('EXCEPTION in', self.title, 'Node:', e)

    # OVERRIDE
    def update_event(self, input_called=-1):
        """Gets called when an input received a signal or some node requested data of an output in exec mode"""

        pass

    def input(self, index: int):
        """Returns the value of a data input.
        If the input is connected, the value of the connected output is used:
        If not, the value of the widget is used."""

        InfoMsgs.write('input called in', self.title, 'Node:', index)
        return self.inputs[index].get_val()

    def exec_output(self, index: int):
        """Executes an exec output, causing activation of all connections"""

        self.outputs[index].exec()

    def set_output_val(self, index, val):
        """Sets the value of a data output causing activation of all connections in data mode"""

        self.outputs[index].set_val(val)

    # OVERRIDE
    def place_event(self):
        """
        place_event() is called once the node object has been fully initialized and placed in the Flow.
        When loading content, place_event() is executed *before* the connections are built,
        which is important for nodes that need to update once and, during this process set output data values,
        to prevent other (later connected) nodes from receiving updates because of that.
        Notice that this method gets executed *every time* the node is added to the flow, which can happen
        multiple times, due to undo/redo operations for example.
        Also note that GUI content is generally not accessible yet from here, for that use view_place_event().
        """

        pass

    # OVERRIDE
    def view_place_event(self):
        """
        view_place_event() is called once all GUI for the node has been created by the frontend.
        Any initial communication to widgets is supposed to happen here, and this method is not called
        when running without gui.
        """

        pass

    # OVERRIDE
    def remove_event(self):
        """Called when the node is removed from the flow; useful for stopping threads and timers etc."""

        pass

    # OVERRIDE
    def _initialized(self):
        """Called once all the node's components (including inputs, outputs) have been initialized"""

        pass

    # OVERRIDE
    def custom_config_data(self) -> dict:
        """Convenience method for saving some std config for all nodes in an editor.
        get_state()/set_state() then stays clean for all specific node subclasses"""

        return {}

    # OVERRIDE
    def load_custom_config(self, data: dict):
        """For loading the data returned by custom_config_data()"""
        pass

    # OVERRIDE
    def get_state(self) -> dict:
        """
        Used to store node-specific custom data that needs to be reloaded when loading a project or pasting copied
        components. All values will be serialized by pickle and base64. The corresponding method for the opposite
        operation is set_state().
        """
        return {}

    # OVERRIDE
    def set_state(self, data: dict):
        """
        Used for reloading node-specific custom data which has been previously returned by get_state()
        """
        pass

    # -----------------------------------------------------------------------------------------------------------------

    # API


    #   LOGGING


    def new_log(self, title) -> Log:
        """Requesting a new custom Log"""

        new_log = self.script.logger.new_log(title)
        self.logs.append(new_log)
        return new_log

    def disable_logs(self):
        """Disables custom logs"""

        for log in self.logs:
            log.disable()

    def enable_logs(self):
        """Enables custom logs"""

        for log in self.logs:
            log.enable()

    def log_message(self, msg: str, target: str):
        """Writes a message string to a default script log with title target"""

        self.script.logger.log_message(msg, target)


    #   PORTS


    def create_input(self, type_: str = 'data', label: str = '', add_config={}, insert: int = None):
        """Creates and adds a new input at index pos"""
        # InfoMsgs.write('create_input called')

        inp = NodeInput(
            node=self,
            type_=type_,
            label_str=label,
            add_config=add_config,
        )

        if insert is not None:
            self.inputs.insert(insert, inp)
        else:
            self.inputs.append(inp)


    def create_input_dt(self, dtype: DType, label: str = '', add_config={}, insert: int = None):
        """Creates and adds a new data input with a DType"""
        # InfoMsgs.write('create_input called')

        inp = NodeInput(
            node=self,
            type_='data',
            label_str=label,
            dtype=dtype,
            add_config=add_config,
        )

        if insert is not None:
            self.inputs.insert(insert, inp)
        else:
            self.inputs.append(inp)


    def delete_input(self, index):
        """Disconnects and removes input"""

        inp: NodeInput = self.inputs[index]

        # break all connections
        for c in inp.connections:
            self.flow.connect_nodes(c.out, inp)

        self.inputs.remove(inp)


    def create_output(self, type_: str = 'data', label: str = '', insert: int = None):
        """Creates and adds a new output"""

        out = NodeOutput(
              node=self,
              type_=type_,
              label_str=label
        )

        if insert is not None:
            self.outputs.insert(insert, out)
        else:
            self.outputs.append(out)


    def delete_output(self, index):
        """Disconnects and removes output"""

        out: NodeOutput = self.outputs[index]

        # break all connections
        for c in out.connections:
            self.flow.connect_nodes(out, c.inp)

        self.outputs.remove(out)


    #   VARIABLES


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


    # -----------------------------------------------------------------------------------------------------------------



    def prepare_removal(self):
        """Called from Flow when the node gets removed"""

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


    def config_data(self) -> dict:
        """
        Returns all metadata of the node in JSON-compatible dict.
        Used to rebuild the Flow when loading a project or pasting components.
        """

        # general attributes
        node_dict = {
            'identifier': self.identifier,
            'state data': serialize(self.get_state()),
            **self.custom_config_data()
        }

        # inputs
        inputs = []
        for i in self.inputs:
            input_dict = i.config_data()
            inputs.append(input_dict)
        node_dict['inputs'] = inputs

        # outputs
        outputs = []
        for o in self.outputs:
            output_dict = o.config_data()
            outputs.append(output_dict)
        node_dict['outputs'] = outputs

        return node_dict

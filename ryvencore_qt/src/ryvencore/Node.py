import logging
import traceback

from . import FlowAlg
from .Base import Base

from .NodePort import NodeInput, NodeOutput
from .NodePortBP import NodeInputBP, NodeOutputBP
from .dtypes import DType
from .InfoMsgs import InfoMsgs
from .logging.Logger import Logger
from .tools import serialize, deserialize


class Node(Base):
    """Base class for all node blueprints. Such a blueprint is defined by its class, which is registered
    in the session, and actual node objects are instances of it. The static properties are stored using
    static attributes, which works really well in Python.
    All the main API for programming nodes, i.e. creating subclasses of this class, is defined here."""

    title = ''
    type_ = ''
    # keywords = []  TODO: add this with intelligent search in NodeSelectionWidget
    init_inputs: [NodeInputBP] = []
    init_outputs: [NodeOutputBP] = []
    identifier: str = None  # set by Session if None
    identifier_comp: [str] = []  # identifier compatibility, useful when node class name changes

    identifier_prefix: str = None  # becomes part of identifier if set

    # INITIALIZATION ---------------------------------------------------------------------------------------------------

    @classmethod
    def build_identifier(cls):

        full_prefix = (cls.identifier_prefix + '.') if cls.identifier_prefix is not None else ''

        if cls.identifier is None:
            cls.identifier = cls.__name__

        cls.identifier = full_prefix + cls.identifier

        for ic in cls.identifier_comp:
            cls.identifier_comp.remove(ic)
            cls.identifier_comp.append(full_prefix + ic)

    def __init__(self, params):
        Base.__init__(self)

        self.flow, self.session, self.init_data = params
        self.script = self.flow.script
        self.inputs: [NodeInput] = []
        self.outputs: [NodeOutput] = []
        self.loggers = []
        # self.global_logger, self.errors_logger = self.script.logs_manager.default_loggers.values()

        self.initialized = False

        self.block_init_updates = False
        self.block_updates = False

    def finish_initialization(self):
        """
        Loads all default properties from initial data if it was provided;
        sets up inputs and outputs, enables the logs, loads custom (std) data
        and calls self._initialized()
        """

        if self.init_data:
            self.setup_ports(self.init_data['inputs'], self.init_data['outputs'])

            self.load_custom_data(self.init_data)

        else:
            self.setup_ports()

        self.enable_loggers()
        self._initialized()
        self.initialized = True

        # self.update()

    def load_user_data(self):
        """Loads the component-specific data that was returned by get_state() previously; prints an exception
        if it fails but doesn't crash because that usually happens when developing nodes"""

        if self.init_data:
            try:
                if type(self.init_data['state data']) == dict:  # backwards compatibility
                    self.set_state(self.init_data['state data'])
                else:
                    self.set_state(deserialize(self.init_data['state data']))
            except Exception as e:
                InfoMsgs.write_err(
                    'Exception while setting data in', self.title, 'node:', e, ' (was this intended?)')

    def setup_ports(self, inputs_data=None, outputs_data=None):

        if not inputs_data and not outputs_data:
            for i in range(len(self.init_inputs)):
                inp = self.init_inputs[i]

                if inp.dtype:
                    self.create_input_dt(dtype=inp.dtype, label=inp.label, add_data=inp.add_data)

                else:
                    self.create_input(inp.label, inp.type_, add_data=self.init_inputs[i].add_data)

            for o in range(len(self.init_outputs)):
                out = self.init_outputs[o]
                self.create_output(out.label, out.type_)

        else:  # when loading saved nodes, the init_inputs and init_outputs are irrelevant
            for inp in inputs_data:
                if 'dtype' in inp:
                    self.create_input_dt(dtype=DType.from_str(inp['dtype'])(
                        _load_state=deserialize(inp['dtype state'])), label=inp['label'], add_data=inp)
                else:
                    self.create_input(label=inp['label'], type_=inp['type'], add_data=inp)

                if 'val' in inp:
                    # this means the input is 'data' and did not have any connections,
                    # so we saved its value which was probably represented by some widget
                    # in the front end which has probably overridden the Node.input() method
                    self.inputs[-1].val = deserialize(inp['val'])

            for out in outputs_data:
                self.create_output(out['label'], out['type'])

    def prepare_placement(self):
        """Called from Flow when the nodes gets added"""

        self.enable_loggers()
        self.place_event()

    def prepare_removal(self):
        """Called from Flow when the node gets removed"""

        self.remove_event()
        self.disable_loggers()

    # ALGORITHM --------------------------------------------------------------------------------------------------------

    # notice that all the below methods check whether the flow currently 'runs with an executor', which means
    # the flow is running in a special execution mode, in which case all the algorithm-related methods below are
    # handled by the according executor

    def update(self, inp=-1):  # , output_called=-1):
        """'Activates' the node, causing an update_event(); prints an exception if something crashed, but prevents
        the application from crashing in such a case"""

        if self.block_updates:
            InfoMsgs.write('update blocked in', self.title, 'node')
            return

        InfoMsgs.write('update in', self.title, 'node on input', inp)

        # invoke update_event
        if self.flow.running_with_executor:
            self.flow.executor.update_node(self, inp)
        else:
            try:
                self.update_event(inp)
            except Exception as e:
                InfoMsgs.write_err('EXCEPTION in', self.title, '\n', traceback.format_exc())

    def input(self, index: int):
        """Returns the value of a data input.
        If the input is connected, the value of the connected output is used:
        If not, the value of the widget is used."""

        InfoMsgs.write('input called in', self.title, 'Node:', index)

        if self.flow.running_with_executor:
            return self.flow.executor.input(self, index)
        else:
            return self.inputs[index].get_val()

    def exec_output(self, index: int):
        """Executes an exec output, causing activation of all connections"""
        if self.flow.running_with_executor:
            self.flow.executor.exec_output(self, index)
        else:
            self.outputs[index].exec()

    def set_output_val(self, index, val):
        """Sets the value of a data output causing activation of all connections in data mode"""
        if self.flow.running_with_executor:
            self.flow.executor.set_output_val(self, index, val)
        else:
            self.outputs[index].set_val(val)

    # EVENTS -----------------------------------------------------------------------------------------------------------
    # these methods get implemented by node implementations

    def update_event(self, inp=-1):
        """Gets called when an input received a signal or some node requested data of an output in exec mode"""

        pass

    def place_event(self):
        """
        place_event() is called once the node object has been fully initialized and placed in the flow.
        When loading content, place_event() is executed *before* the connections are built,
        which is important for nodes that need to update once and, during this process, set output data values,
        to prevent other (later connected) nodes from receiving updates because of that.
        Notice that this method gets executed *every time* the node is added to the flow, which can happen
        multiple times, due to undo/redo operations for example.
        Also note that GUI content is generally not accessible yet from here, for that use view_place_event().
        """

        pass

    def view_place_event(self):
        """
        view_place_event() is called once all GUI for the node has been created by the frontend.
        Any initial communication to widgets is supposed to happen here, and this method is not called
        when running without gui.
        """

        pass

    def remove_event(self):
        """Called when the node is removed from the flow; useful for stopping threads and timers etc."""

        pass

    def _initialized(self):  # not used currently

        """Called once all the node's components (including inputs, outputs) have been initialized"""

        pass

    def additional_data(self) -> dict:
        """Convenience method for wrappers for saving some std data for all nodes in an editor.
        get_state()/set_state() then stays clean for all specific node subclasses"""

        return {}

    def load_custom_data(self, data: dict):
        """For loading the data returned by custom_data()"""
        pass

    def get_state(self) -> dict:
        """
        Used to store node-specific custom data that needs to be reloaded when loading a project or pasting copied
        components. All values will be serialized by pickle and base64. The corresponding method for the opposite
        operation is set_state().
        """
        return {}

    def set_state(self, data: dict):
        """
        Used for reloading node-specific custom data which has been previously returned by get_state()
        """
        pass

    # API --------------------------------------------------------------------------------------------------------------

    #   LOGGING

    def new_logger(self, title) -> Logger:
        """Requesting a new custom Log"""

        logger = self.script.logs_manager.new_logger(title)
        self.loggers.append(logger)
        return logger

    def disable_loggers(self):
        """Disables custom logs"""

        for logger in self.loggers:
            logger.disable()
            # logger.disabled = True

    def enable_loggers(self):
        """Enables custom logs"""

        for logger in self.loggers:
            logger.enable()
            # logger.enabled = True

    #   PORTS

    def create_input(self, label: str = '', type_: str = 'data', add_data={}, insert: int = None):
        """Creates and adds a new input at index pos"""
        # InfoMsgs.write('create_input called')

        inp = NodeInput(
            node=self,
            type_=type_,
            label_str=label,
            add_data=add_data,
        )

        if insert is not None:
            self.inputs.insert(insert, inp)
        else:
            self.inputs.append(inp)

    def create_input_dt(self, dtype: DType, label: str = '', add_data={}, insert: int = None):
        """Creates and adds a new data input with a DType"""
        # InfoMsgs.write('create_input called')

        inp = NodeInput(
            node=self,
            type_='data',
            label_str=label,
            dtype=dtype,
            add_data=add_data,
        )

        if insert is not None:
            self.inputs.insert(insert, inp)
        else:
            self.inputs.append(inp)

    def rename_input(self, index: int, label: str):
        self.inputs[index].label_str = label

    def delete_input(self, index: int):
        """Disconnects and removes input"""

        inp: NodeInput = self.inputs[index]

        # break all connections
        for c in inp.connections:
            self.flow.connect_nodes(c.out, inp)

        self.inputs.remove(inp)

    def create_output(self, label: str = '', type_: str = 'data', insert: int = None):
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

    def rename_output(self, index: int, label: str):
        self.outputs[index].label_str = label

    def delete_output(self, index: int):
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

    def unregister_var_receiver(self, name: str, method):
        """Unregisters previously registered node as receiver for value changes of script variables with given name"""

        self.get_vars_manager().unregister_receiver(self, name, method)

    # -----------------------------------------------------------------------------------------------------------------

    def is_active(self):
        for i in self.inputs:
            if i.type_ == 'exec':
                return True
        for o in self.outputs:
            if o.type_ == 'exec':
                return True
        return False

    def flow_in_data_opt_mode(self):
        return self.flow.alg_mode == FlowAlg.DATA_OPT

    def data(self) -> dict:
        """
        Returns all metadata of the node in JSON-compatible dict.
        Used to rebuild the Flow when loading a project or pasting components.
        """

        return {
            'identifier': self.identifier,
            'state data': serialize(self.get_state()),
            'inputs': [i.data() for i in self.inputs],
            'outputs': [o.data() for o in self.outputs],

            **self.additional_data(),

            'GID': self.GLOBAL_ID,
        }

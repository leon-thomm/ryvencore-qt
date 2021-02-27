import time

from PySide2.QtCore import QObject, Signal

from .Flow import Flow
from ..FlowView import FlowView  # TODO [!DEPENDENCY!]
from .logging.Logger import Logger
from .script_variables.VarsManager import VarsManager


class Script(QObject):
    """A Script consists of a Flow, the corresponding FlowView, a variables manager and a logger."""

    create_flow_view_request = Signal(object, tuple)
    generate_flow_view_config_request = Signal(dict)

    def __init__(self, session, title: str = None, config_data: dict = None, flow_view_size: list = None,
                 create_default_logs=True, _initialize=True):
        super(Script, self).__init__(parent=session)

        self.session = session
        self.logger = None
        self._create_default_logs = create_default_logs
        self.vars_manager = None
        self.title = title if not config_data else config_data['name']
        self.flow = None

        # all reference to any flow_view should get removed when abstracting away ryvencore
        self.flow_view = None
        self.init_flow_view_size = flow_view_size
        self.init_flow_view_gui_parent = self.session.gui_parent
        self.tmp_data = None  # used to synchronize threads

        self.init_config = config_data
        self.init_flow_config = None
        self.init_flow_view_config = None
        self.init_vars_manager_config = None

        # saving config data
        if config_data:
            self.init_flow_config = config_data['flow'] if config_data else None

            if 'flow widget config' not in config_data:  # backwards compatibility
                self.init_flow_view_config = config_data['flow']
            else:
                self.init_flow_view_config = \
                    config_data['flow widget config'] if config_data else None

            self.init_vars_manager_config = config_data['variables']

        if _initialize:
            self.initialize()


    def initialize(self):
        """
        Creates flow, flow view, vars manager and logger.
        For normal scripts, this is basically part of the constructor. But for FunctionScripts the Script might not be
        supposed to create content just yet, so the initialization will proceed later, see FunctionScript class.
        """

        self.logger = Logger(self, self._create_default_logs)
        self.flow = Flow(self.session, self, self)

        if self.session.threaded:
            self.create_flow_view_request.connect(
                self.session.threading_bridge.script_request__create_flow_view
            )

            if self.session.gui_parent is None:
                raise Exception(
                    "When using threading, you must provide a gui_parent."
                )

        # VARS MANAGER
        if self.init_config:
            self.vars_manager = VarsManager(self, self.init_vars_manager_config)
        else:
            self.vars_manager = VarsManager(self)

        # INIT FLOW VIEW
        flow_view_params = (
            self.session,
            self,
            self.flow,
            self.init_flow_view_config,
            self.init_flow_view_size,
            self.session.gui_parent
        )
        if self.session.threaded:
            self.create_flow_view_request.emit(self, flow_view_params)

            # wait until flow_view initialized
            while self.tmp_data is None:
                time.sleep(0.001)
            self.flow_view = self.tmp_data

        else:
            self.flow_view = FlowView(*flow_view_params)

        # CONNECT TO FLOW VIEW
        self.generate_flow_view_config_request.connect(self.flow_view.generate_config_data)

        # LOAD FLOW
        if self.init_flow_config is not None:
            self.flow.load(config=self.init_flow_config)


    def serialize(self) -> dict:
        """Returns the config data of the script, including variables and flow content"""

        abstract_flow_data = self.flow.generate_config_data()
        self.generate_flow_view_config_request.emit(abstract_flow_data)

        while self.flow_view._temp_config_data is None:
            time.sleep(0.001)  # 'join' threads
        flow_config, flow_view_config = self.flow_view._temp_config_data

        script_dict = {
            'name': self.title,
            'variables': self.vars_manager.config_data(),
            'flow': flow_config,
            'flow widget config': flow_view_config
        }

        return script_dict

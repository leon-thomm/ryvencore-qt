from .Base import Base, Signal

from .Flow import Flow
from .logging.Logger import Logger
from .script_variables.VarsManager import VarsManager


class Script(Base):
    """A Script consists of a Flow, the corresponding FlowView, a variables manager and a logger."""

    def __init__(self, session, title: str = None, config_data: dict = None, create_default_logs=True):
        super(Script, self).__init__(parent=session)

        self.session = session
        self.logger = None
        self._create_default_logs = create_default_logs
        self.vars_manager = None
        self.title = title if not config_data else config_data['name']
        self.flow = None

        self.init_config = config_data
        self.init_flow_config = None
        self.init_vars_manager_config = None

        # saving config data
        if config_data:
            self.init_flow_config = config_data['flow'] if config_data else None
            self.init_vars_manager_config = config_data['variables']

        self.logger = Logger(self, self._create_default_logs)
        self.flow = Flow(self.session, self, self)

        # VARS MANAGER
        if self.init_config:
            self.vars_manager = VarsManager(self, self.init_vars_manager_config)
        else:
            self.vars_manager = VarsManager(self)


    def load_flow(self):
        if self.init_flow_config:
            self.flow.load(self.init_flow_config)


    def serialize(self) -> dict:
        """Returns the config data of the script, including variables and flow content"""

        flow_data = self.flow.generate_config_data()
        # self.generate_flow_view_config_request.emit(flow_data)
        #
        # while self.flow_view._temp_config_data is None:
        #     time.sleep(0.001)  # 'join' threads
        # flow_config, flow_view_config = self.flow_view._temp_config_data

        script_dict = {
            'name': self.title,
            'variables': self.vars_manager.config_data(),
            'flow': flow_data,
            # 'flow widget config': flow_view_config,
        }

        return script_dict

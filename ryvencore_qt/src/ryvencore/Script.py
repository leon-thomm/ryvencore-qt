from .Base import Base

from .RC import CLASSES


class Script(Base):
    """A Script consists of a Flow, the corresponding FlowView, a variables manager and a logger."""

    def __init__(self, session, title: str = None, config_data: dict = None, create_default_logs=True):
        Base.__init__(self)

        self.session = session
        self.logs_manager = None
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

        # logging
        self.logs_manager = CLASSES['logs manager'](self, self._create_default_logs)

        # vars manager
        self.vars_manager = CLASSES['vars manager'](self, self.init_vars_manager_config)

        # flow
        self.flow = CLASSES['flow'](self.session, self)

    def load_flow(self):
        if self.init_flow_config:
            self.flow.load(self.init_flow_config)


    def serialize(self) -> dict:
        """Returns the config data of the script, including variables and flow content"""

        flow_data = self.flow.generate_config_data()

        script_dict = {
            'name': self.title,
            'variables': self.vars_manager.config_data(),
            'flow': flow_data,
            # 'flow widget config': flow_view_config,
        }

        return script_dict

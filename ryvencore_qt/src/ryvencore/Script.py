from .Base import Base

from .RC import CLASSES


class Script(Base):
    """A Script consists of a Flow, the corresponding FlowView, a variables manager and a logger."""

    def __init__(self, session, title: str = None, load_data: dict = None, create_default_logs=True):
        Base.__init__(self)

        self.session = session
        self.logs_manager = None
        self._create_default_logs = create_default_logs
        self.vars_manager = None
        self.title = title if not load_data else (load_data['title'] if 'title' in load_data else load_data['name'])
        self.flow = None

        self.init_data = load_data
        self.init_flow_data = None
        self.init_vars_manager_data = None

        # saving data
        if load_data:
            self.init_flow_data = load_data['flow'] if load_data else None
            self.init_vars_manager_data = load_data['variables']

        # logging
        self.logs_manager = CLASSES['logs manager'](self, self._create_default_logs)

        # vars manager
        self.vars_manager = CLASSES['vars manager'](self, self.init_vars_manager_data)

        # flow
        self.flow = CLASSES['flow'](self.session, self)

    def load_flow(self):
        if self.init_flow_data:
            self.flow.load(self.init_flow_data)


    def data(self) -> dict:
        return {
            'title': self.title,
            'variables': self.vars_manager.data(),
            'flow': self.flow.data(),
            'GID': self.GLOBAL_ID,
        }

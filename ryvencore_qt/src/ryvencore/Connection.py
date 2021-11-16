from .Base import Base, Event

from .InfoMsgs import InfoMsgs


class Connection(Base):
    """
    The base class for both types of connections. All data is transmitted through a connection from an output
    port to some connected input port.
    """

    activated = Event()

    def __init__(self, params):
        Base.__init__(self)

        self.out, self.inp, self.flow = params

    def activate(self):
        """Causes forward propagation of information"""

        self.activated.emit()


class ExecConnection(Connection):

    def activate(self):
        """Causes an update in the input port"""
        InfoMsgs.write('exec connection activated')
        super().activate()

        self.inp.update()


class DataConnection(Connection):

    def __init__(self, params):
        super().__init__(params)

        self.data = None

    def get_val(self):
        """Gets the value of the output port -- only used in exec mode flows"""
        InfoMsgs.write('data connection getting value')

        # request data backwards
        self.data = self.out.get_val()

        return self.data

    def activate(self, data=None):
        """Passes data to the input port and causes update"""
        InfoMsgs.write('data connection activated')
        super().activate()

        # store data
        self.data = data

        # propagate data forward
        self.inp.update(data)

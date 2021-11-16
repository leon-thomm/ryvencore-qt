from logging import Logger as PyLogger
from ..Base import Base, Event


class Logger(Base, PyLogger):
    """
    A small wrapper template for the python loggers to add functionality on node events.
    Reimplemented as wrapper by the frontend with according implementations of the below methods.
    """

    sig_enabled = Event()
    sig_disabled = Event()


    def enable(self):
        self.sig_enabled.emit()

    def disable(self):
        self.sig_disabled.emit()

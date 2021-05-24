from logging import Logger as PyLogger


class Logger(PyLogger):
    """
    A small wrapper template for the python Loggers to add
    functionality on node events.
    Reimplemented as wrapper by the frontend with
    according implementations of the below methods.
    """

    def enable(self):
        pass

    def disable(self):
        pass

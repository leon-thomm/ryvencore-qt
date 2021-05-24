from ..Base import Base

from ..RC import CLASSES

# from logging import Logger
from .Logger import Logger


class LogsManager(Base):
    """Manages all logs/loggers that belong to the script."""

    def __init__(self, script, create_default_logs=True):
        Base.__init__(self)

        self.script = script
        self.loggers: [Logger] = []
        self.default_loggers = {
            'global': None,
            'errors': None,
        }

        if create_default_logs:
            self.create_default_loggers()

    def create_default_loggers(self):
        for name in self.default_loggers.keys():
            self.default_loggers[name] = self.new_logger(title=name.title())

    def new_logger(self, title: str) -> Logger:
        logger = CLASSES['logger'](name=title)
        self.loggers.append(logger)
        return logger

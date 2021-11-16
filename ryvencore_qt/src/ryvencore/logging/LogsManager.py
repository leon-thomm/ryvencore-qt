from ..Base import Base, Event
from .Logger import Logger


class LogsManager(Base):
    """Manages all logs/loggers that belong to the script."""

    new_logger_created = Event(Logger)

    def __init__(self, script, create_default_logs=True):
        Base.__init__(self)

        self.script = script
        self.session = self.script.session
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
        logger = self.session.CLASSES['logger'](name=title)
        self.loggers.append(logger)
        self.new_logger_created.emit(logger)
        return logger

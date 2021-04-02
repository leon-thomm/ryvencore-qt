from ..Base import Base

from .Log import Log
from ..RC import CLASSES


class Logger(Base):
    """Manages all logs that belong to the script."""

    def __init__(self, script, create_default_logs=True):
        Base.__init__(self)

        self.script = script
        self.logs: [Log] = []

        if create_default_logs:
            self.create_default_logs()

    def create_default_logs(self):
        self.new_log(title='Global')
        self.new_log(title='Errors')

    def log_message(self, msg: str, target: str = ''):
        for log in self.logs:
            if log.title == target:
                log.write(msg)

    def new_log(self, title: str) -> Log:

        log = CLASSES['log'](title=title)
        self.logs.append(log)
        return log

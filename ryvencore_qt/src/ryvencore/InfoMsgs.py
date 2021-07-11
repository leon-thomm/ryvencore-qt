import sys
import traceback


class InfoMsgs:
    """A few handy static methods for writing different kinds of messages to the output console only if info msgs are
    enabled."""

    enabled = False
    enabled_errors = False
    traceback_enabled = False

    @staticmethod
    def enable(traceback=False):
        InfoMsgs.enabled = True
        InfoMsgs.traceback_enabled = traceback

    @staticmethod
    def enable_errors(traceback=True):
        InfoMsgs.enabled_errors = True
        InfoMsgs.traceback_enabled = traceback

    @staticmethod
    def disable():
        InfoMsgs.enabled = False

    @staticmethod
    def write(*args):
        if not InfoMsgs.enabled:
            return

        s = ''
        for arg in args:
            s += ' '+str(arg)
        print('--> INFO: '+s)

    @staticmethod
    def write_err(*args):
        if not (InfoMsgs.enabled or InfoMsgs.enabled_errors):
            return

        s = ''
        for arg in args:
            s += ' '+str(arg)

        sys.stderr.write(s)

        if InfoMsgs.traceback_enabled:
            sys.stderr.write(traceback.format_exc())



class MSG_COLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

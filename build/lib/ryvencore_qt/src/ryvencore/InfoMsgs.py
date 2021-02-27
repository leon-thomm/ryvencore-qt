import sys


class InfoMsgs:
    """A few handy static methods for writing different kinds of messages to the output console only if they are
    enabled."""

    enabled = False

    @staticmethod
    def enable():
        InfoMsgs.enabled = True

    @staticmethod
    def disable():
        InfoMsgs.enabled = False

    def write(*args):
        if not InfoMsgs.enabled:
            return

        s = ''
        for arg in args:
            s += ' '+str(arg)
        print('--> INFO: '+s)

    def write_err(*args):
        if not InfoMsgs.enabled:
            return

        s = ''
        for arg in args:
            s += ' '+str(arg)

        sys.stderr.write(s)



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

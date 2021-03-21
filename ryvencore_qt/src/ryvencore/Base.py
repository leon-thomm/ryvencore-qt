Base = None
Signal = None

def build_base_class(mode: str):
    """
    Builds the Base class for all abstract components.
    If mode is 'gui' the Base is just QObject.
    If mode is 'no gui' the Base is instead empty and Signal is replaced by a dummy class,
    so there is no Qt functionality/dependency anymore when running in this mode.
    """

    global Base
    global Signal

    if mode == 'no gui':

        # no GUI -> use dummy classes

        class AbstractBase:
            pass

        class AbstractSignal:
            def __init__(self, *args):
                pass

            def connect(self, method):
                pass

            def emit(self, *args):
                pass

        Base = AbstractBase
        Signal = AbstractSignal

    else:

        # GUI -> use Qt classes

        from qtpy.QtCore import QObject, Signal as QtSignal

        class GUIBase(QObject):
            pass

        Base = GUIBase
        Signal = QtSignal

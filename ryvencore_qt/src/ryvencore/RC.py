"""Namespace for enum types etc."""

from enum import IntEnum


class FlowAlg(IntEnum):
    """Used for performance"""

    DATA = 1
    EXEC = 2
    DATA_OPT = 3

    @staticmethod
    def str(mode):
        # not using __str__ here because FlowAlg only serves as an enum,
        # so there won't be any objects instantiated
        if mode == FlowAlg.DATA:
            return 'data'
        elif mode == FlowAlg.EXEC:
            return 'exec'
        elif mode == FlowAlg.DATA_OPT:
            return 'data opt'

        return None

    @staticmethod
    def from_str(mode):
        if mode == 'data':
            return FlowAlg.DATA
        elif mode == 'exec':
            return FlowAlg.EXEC
        elif mode == 'data opt':
            return FlowAlg.DATA_OPT

        return None


class PortObjPos(IntEnum):
    """Used for performance"""

    INPUT = 1
    OUTPUT = 2


# registry for customizable classes
CLASSES = {
    'node base':    None,
    'data conn':    None,
    'exec conn':    None,
    'logs manager': None,
    'logger':       None,
    'vars manager': None,
    'flow':         None,
}

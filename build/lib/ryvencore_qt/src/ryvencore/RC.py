"""Namespace for enum types"""

from enum import IntEnum


class FlowAlg(IntEnum):
    """Used for performance"""

    DATA = 1
    EXEC = 2

    @staticmethod
    def stringify(mode):
        if mode == FlowAlg.DATA:
            return 'data'
        elif mode == FlowAlg.EXEC:
            return 'exec'


class FlowVPUpdateMode(IntEnum):
    """Used for performance"""

    SYNC = 1
    ASYNC = 2

    @staticmethod
    def stringify(mode):
        if mode == FlowVPUpdateMode.SYNC:
            return 'sync'
        elif mode == FlowVPUpdateMode.ASYNC:
            return 'async'


# alternative solution, maybe use this later:
# class Flows:
#     class Alg(IntEnum):
#         DATA = 1
#         EXEC = 2
#
#     class VPUpdateMode(IntEnum):
#         SYNC = 1
#         ASYNC = 2


class PortObjPos(IntEnum):
    """Used for performance"""

    INPUT = 1
    OUTPUT = 2


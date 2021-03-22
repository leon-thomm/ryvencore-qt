"""Namespace for enum types and stuff"""

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


class PortObjPos(IntEnum):
    """Used for performance"""

    INPUT = 1
    OUTPUT = 2


# registry for customizable classes
CLASSES = {
    'node base': None,
    'data conn': None,
    'exec conn': None,
}


# class FlowVPUpdateMode(IntEnum):
#     """Used for performance"""
#
#     SYNC = 1
#     ASYNC = 2
#
#     @staticmethod
#     def stringify(mode):
#         if mode == FlowVPUpdateMode.SYNC:
#             return 'sync'
#         elif mode == FlowVPUpdateMode.ASYNC:
#             return 'async'

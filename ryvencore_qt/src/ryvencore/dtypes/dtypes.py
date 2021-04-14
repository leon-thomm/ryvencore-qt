"""
This module contains definitions of declarative types which can be conveniently used for data inputs.
For each of the exposed types, the frontend can define some prebuilt widgets, which makes nodes
from other frontends that use those types to determine input widgets automatically compatible in
other environments.
This list may grow significantly over time.
"""


class DType:
    def __init__(self, default, bounded: bool = False, bounds: tuple = None, doc: str = ""):
        self.default = default
        self.doc = doc
        self.bounded = bounded
        if self.bounded:
            self.bounds = bounds

    def __str__(self):
        return 'DType.'+self.__class__.__name__

    @staticmethod
    def from_str(s):
        for DTypeClass in exposed_types:
            if s == 'DType.'+DTypeClass.__name__:
                return DTypeClass

        return None


class Data(DType):
    """Any kind of data represented by some evaluated text input"""
    def __init__(self, default=None, size: str = 'm', doc=None):
        """
        size: 's' / 'm' / 'l'
        """
        super().__init__(default=default, doc=doc)
        self.size = size


class Integer(DType):
    def __init__(self, default: int = 0, bounds: tuple = None, doc: str = ""):
        super().__init__(default, True, bounds, doc)


class Float(DType):
    def __init__(self, default: float = 0.0, bounds: tuple = None, decimals: int = 10, doc: str = ""):
        super().__init__(default, True, bounds, doc)
        self.decimals = decimals


class Boolean(DType):
    def __init__(self, default: bool = False, doc: str = ""):
        super().__init__(default=default, doc=doc)


class Char(DType):
    def __init__(self, default: chr = '', doc: str = ""):
        super().__init__(default, doc=doc)


class String(DType):
    def __init__(self, default: str = "", size: str = 'm', doc: str = ""):
        """
        size: 's' / 'm' / 'l'
        """
        super().__init__(default=default, doc=doc)
        self.size = size


class Choice(DType):
    def __init__(self, default, items: list, doc: str = ""):
        super().__init__(default=default, doc=doc)
        self.items = items


class List(DType):
    def __init__(self, default: list = [], doc: str = ""):
        super().__init__(default=default, doc=doc)


class Date(DType):
    ...


class Time(DType):
    ...


class Color(DType):
    ...


class Range(DType):
    ...

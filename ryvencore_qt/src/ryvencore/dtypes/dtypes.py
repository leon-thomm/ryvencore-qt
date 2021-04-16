"""
This module contains definitions of declarative types which can be conveniently used for data inputs.
For each of the exposed types, the frontend can define some prebuilt widgets, which makes nodes
from other frontends that use those types to determine input widgets automatically compatible in
other environments.
This list may grow significantly over time.
"""


class DType:
    def __init__(self, default, bounds: tuple = None, doc: str = "", _load_state=None):
        if _load_state:
            self.set_state(_load_state)
        else:
            self.default = default
            self.doc = doc
            self.bounds = bounds

        self._data = ['default', 'doc', 'bounds']

    def __str__(self):
        return 'DType.'+self.__class__.__name__

    @staticmethod
    def from_str(s):
        for DTypeClass in dtypes:
            if s == 'DType.'+DTypeClass.__name__:
                return DTypeClass

        return None

    def add_data(self, *attr_names):
        self._data += list(attr_names)

    def get_state(self) -> dict:
        return {
            name: getattr(self, name)
            for name in self._data
        }

    def set_state(self, data: dict):
        for name, val in data.items():
            setattr(self, name, val)


class Data(DType):
    """Any kind of data represented by some evaluated text input"""
    def __init__(self, default=None, size: str = 'm', doc: str = "", _load_state=None):
        """
        size: 's' / 'm' / 'l'
        """
        self.size = size
        super().__init__(default=default, doc=doc, _load_state=_load_state)
        self.add_data('size')


class Integer(DType):
    def __init__(self, default: int = 0, bounds: tuple = None, doc: str = "", _load_state=None):
        super().__init__(default=default, bounds=bounds, doc=doc, _load_state=_load_state)


class Float(DType):
    def __init__(self, default: float = 0.0, bounds: tuple = None, decimals: int = 10, doc: str = "", _load_state=None):
        self.decimals = decimals
        super().__init__(default=default, bounds=bounds, doc=doc, _load_state=_load_state)
        self.add_data('decimals')


class Boolean(DType):
    def __init__(self, default: bool = False, doc: str = "", _load_state=None):
        super().__init__(default=default, doc=doc, _load_state=_load_state)


class Char(DType):
    def __init__(self, default: chr = '', doc: str = "", _load_state=None):
        super().__init__(default=default, doc=doc, _load_state=_load_state)


class String(DType):
    def __init__(self, default: str = "", size: str = 'm', doc: str = "", _load_state=None):
        """
        size: 's' / 'm' / 'l'
        """
        self.size = size
        super().__init__(default=default, doc=doc, _load_state=_load_state)
        self.add_data('size')


class Choice(DType):
    def __init__(self, default, items: list, doc: str = "", _load_state=None):
        self.items = items
        super().__init__(default=default, doc=doc, _load_state=_load_state)
        self.add_data('items')


class List(DType):
    def __init__(self, default: list = [], doc: str = "", _load_state=None):
        super().__init__(default=default, doc=doc, _load_state=_load_state)


class Date(DType):
    ...


class Time(DType):
    ...


class Color(DType):
    ...


class Range(DType):
    ...

dtypes = [Data, Integer, Float, Boolean, Char, String, Choice, List]

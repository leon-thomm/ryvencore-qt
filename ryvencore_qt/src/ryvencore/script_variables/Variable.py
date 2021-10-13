from ..utils import serialize, deserialize


class Variable:
    """Implementation of script variables"""

    def __init__(self, name='', val=None):
        self.name = name
        self.val = None

        if val and 'serialized' in val.keys():
            self.val = deserialize(val['serialized'])

    def serialize(self):
        return serialize(self.val)

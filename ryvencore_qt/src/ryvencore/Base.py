def complete_data(data: dict) -> dict:
    """Default implementation for completing data with frontend properties.
    When running with a frontend that needs to store additional information about
    components (e.g. current position and color of a node), this frontend then
    overrode this exact function to add whatever is necessary for adding this data."""
    return data


class Base:
    """
    Base class for all abstract components. Provides functionality for ID counting.
    Assigns a global ID to every object and provides an optional custom ID counter for additional custom counting.
    """

    class IDCtr:
        def __init__(self):
            self.ctr = -1

        def count(self):
            """increases the counter and returns the new count. first time is 0"""
            self.ctr += 1
            return self.ctr

        def set_count(self, cnt):
            if cnt < self.ctr:
                raise Exception("Decreasing ID counters is illegal")
            else:
                self.ctr = cnt

    # all abstract components have a global ID
    global_id_ctr = IDCtr()

    # optional custom ID counter
    id_ctr = None
    # notice that the attribute is static, but a subclass changing it will not change it for Base
    # and hence not for other Base subclasses, only for itself

    def __init__(self):
        self.GLOBAL_ID = self.global_id_ctr.count()

        # ignore custom ID if it has already been set
        if self.id_ctr is not None and not (hasattr(self, 'ID') and self.ID is not None):
            self.ID = self.id_ctr.count()

    def data(self) -> dict:
        """Converts the object to a JSON compatible dict for serialization"""
        return None

    def complete_data(self, data: dict) -> data:
        return complete_data(data)

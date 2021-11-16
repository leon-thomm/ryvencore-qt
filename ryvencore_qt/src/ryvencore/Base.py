def complete_data(data: dict) -> dict:
    """Default implementation for completing data with frontend properties.
    When running with a frontend that needs to store additional information about
    components (e.g. current position and color of a node), this frontend then
    overrode this exact function to add whatever is necessary for adding this data."""
    return data


class Event:
    def __init__(self, *args):
        self.args = args
        self._slots = []

    def connect(self, callback):
        self._slots.append(callback)

    def disconnect(self, callback):
        self._slots.remove(callback)

    def emit(self, *args):
        for cb in self._slots:
            cb(args)


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

    # events
    events = {}
    # format: {event_name : tuple_of_arguments}
    # the arguments tuple only serves documentation purposes

    def __init__(self):
        self.GLOBAL_ID = self.global_id_ctr.count()

        # ignore custom ID if it has already been set
        if self.id_ctr is not None and not (hasattr(self, 'ID') and self.ID is not None):
            self.ID = self.id_ctr.count()

        self._slots = {
            ev: []
            for ev in self.events
        }

    # CUSTOM DATA ------------------------------------

    # this can be set to another function by the frontend to implement adding frontend information to the data dict
    complete_data_function = lambda data: data

    def data(self) -> dict:
        """converts the object to a JSON compatible dict for serialization"""
        return None

    def complete_data(self, data: dict) -> data:
        return Base.complete_data_function(data)

    # EVENTS ------------------------------------

    def on(self, ev: Event, callback):
        # self._slots[ev].append(callback)
        ev.connect(callback)

    def off(self, ev: Event, callback):
        # self._slots[ev].remove(callback)
        ev.disconnect(callback)

    # def _emit(self, ev: str, *args, **kwargs):
    #     for s in self._slots[ev]:
    #         s(args, kwargs)

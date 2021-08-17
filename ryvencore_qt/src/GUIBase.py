

class GUIBase:
    """Base class for GUI items that represent specific backend components"""

    # component frontend representatives
    COMP_FE_REPS = {}  # global id : GUI object
    # every frontend GUI object that represents some specific component from the backend
    # is stored there under the the global id of the represented component.
    # used for completing data (serialization)

    def complete_data(self, data: dict) -> dict:
        """Completes the data dict of the represented backend component by all frontend information
        that needs to be stored in the data dict too."""
        return data


def _complete_data(data: dict) -> dict:
    return _comp_data_analyze(data)


def _comp_data_analyze(obj):
    """Searches recursively through obj and calls complete_data(obj) on associated
    frontend components(instances of GUIBase)"""

    # TODO: make this thread-safe, this should run in the GUI thread!

    if isinstance(obj, dict):
        if GID := obj.get('GID'):
            # find representative
            if comp := GUIBase.COMP_FE_REPS.get(GID):
                obj = comp.complete_data(obj)  # complete data by frontend information

        # look for child objects
        for key, value in obj.items():
            obj[key] = _complete_data(value)

    elif isinstance(obj, list):
        for i in range(len(obj)):
            item = obj[i]
            item = _comp_data_analyze(item)
            obj[i] = item

    return obj


# overwrite the core's complete_data function
# to add frontend information to the data dicts of in the
# frontend represented components (like nodes)
import ryvencore.Base as Base
Base.complete_data = _complete_data

from PySide2.QtCore import QObject

from .FlowView import FlowView


class SessionThreadingBridge(QObject):
    """
    A SessionThreadingBridge instance is a session's interface to the main thread to create the GUI, i.e. FlowViews,
    in the main thread in threaded applications.
    """

    # @staticmethod
    def script_request__create_flow_view(self, script, params):
        view = FlowView(*params)
        script.tmp_data = view

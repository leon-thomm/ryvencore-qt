from PySide2.QtCore import QObject, Signal


class FlowSessionThreadInterface(QObject):
    """This class is used to automize communication from GUI components from FlowView to their abstract components,
    currently only implementing the execution of node actions after a right click operation.
    If threading is enabled, the FlowView's instance of this class runs in the abstract thread."""


    def trigger_node_action(self, method, data=None):
        if data is not None:
            method(data)
        else:
            method()

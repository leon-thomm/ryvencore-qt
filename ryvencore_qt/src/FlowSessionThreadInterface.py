from qtpy.QtCore import QObject, Signal


class FlowSessionThreadInterface(QObject):
    """This class is used to automize communication from GUI components from FlowView to their abstract components,
    currently only implementing the execution of node actions after a right click operation.
    If threading is enabled, the FlowView's instance of this class runs in the abstract thread."""


    def trigger_node_action(self, method, data=None):
        if data is not None:
            method(data)
        else:
            method()



    def __init__(self):
        super().__init__()
        self.callback_method = None

    callback_signal = Signal(object)

    def run(self, target_method, args: tuple, callback):
        """Runs some method in this thread and calls triggers callback via signal"""

        if self.callback_method is not None:
            # this prevents recursion issues when this method is called again
            # inside the callback method, in this case I need to disconnect
            # the previous connection before calling the new callback
            self.callback_signal.disconnect(self.callback_method)

        self.callback_method = callback

        print(args)
        ret = target_method(*args)
        print(ret)
        if callback:
            self.callback_signal.connect(self.callback_method)
            self.callback_signal.emit(ret)

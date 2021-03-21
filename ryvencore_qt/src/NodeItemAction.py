from qtpy.QtCore import Signal
from qtpy.QtWidgets import QAction


class NodeItemAction(QAction):
    """A custom implementation of QAction that additionally stores transmitted 'data' which can be intuitively used
    in subclasses f.ex. to determine the exact source of the action triggered. For more info see GitHub docs.
    It shall not be a must to use the data parameter though. For that reason, there are two different signals,
    one that triggers with transmitted data, one without.
    So, if a special action does not have 'data', the connected method does not need to have a data parameter.
    Both signals get connected to the target method but only if data isn't None, the signal with the data parameter
    is used."""

    triggered_with_data = Signal(object, object)
    triggered_without_data = Signal(object)

    def __init__(self, node, text, method, menu, data=None):
        super(NodeItemAction, self).__init__(text=text, parent=menu)

        self.node = node
        self.data = data
        self.method = method
        self.triggered.connect(self.triggered_)  # yeah, I think that's ugly but I didn't find a nicer way; it works

    def triggered_(self):
        if self.data is not None:
            self.triggered_with_data.emit(self.grab_method(), self.data)
        else:
            self.triggered_without_data.emit(self.grab_method())

    def grab_method(self):
        """
        Replacement for the retain mechanism. Because some editors (like Ryven) might add source code editing features,
        before calling a method here
        :return:
        """
        updated_method = getattr(self.node, self.method.__name__)
        return updated_method

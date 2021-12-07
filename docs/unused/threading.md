# Threading

## Overview

One of the biggest internal changes in `ryvencore-qt`/`ryvencore` compared to Ryven 2, is the threading compatibility. `ryvencore` provides abstract components and `ryvencore-qt` provides the Qt GUI for the flows (plus some convenience widgets). Therefore, in order to run a session instance in a thread different from the GUI thread, the internal communication between `ryvencore` and `ryvencore-qt` must be set up in a thread save way. To achieve this, `ryvencore-qt` provides custom *WRAPPER* classes for all `ryvencore` components that the frontend needs to communicate with directly. Those wrappers do almost nothing but adding Qt signals to all the API methods, so every time an API method of the backend has been executed, a Qt signal is sent which the frontend components who need to get notified of this API method execution (like creation of a new node must notify the `FlowView`) listen for.

> [!WARNING]
> `Session.serialize()` shouldn't be called in concurrently as the the serialization of the `FlowView` is currently joined with the session's thread by setting an attribute (see implementation). This may change.

## Programming Nodes

A `Node` object lives in the same thread as the `Session` object. Their GUI items, however, including all **custom widgets**, live in the GUI thread. Therefore, you need to make sure that the communication between your nodes and their custom widgets is thread save, which usually means: implemented using Qt's signals and slots.

### Communication from Nodes to Widgets

Use the `Node.view_place_event()` to manage initial connections between the node and its widgets which will exist at this point.

Example:
```python
import ryvencore_qt as rc


class MyNode(rc.Node):
    # ...

    def __init__(self, params):
        super().__init__(params)

        if self.session.gui:
            from PySide2.QtCore import QObject, Signal

            class SIGNALS(QObject):
                notify_gui = Signal(object)

            self.signals = SIGNALS

    def view_place_event(self):
        # remember, the view_place_event will only be called when there is frontend
        self.signals.notify_gui.connect(self.main_widget().some_method)
        self.main_widget().some_input_signal.connect(self.process_input)

    def update_event(self, inp=-1):
        # ...
        self.signals.notify_gui.emit(something)
        # ...
```

### Communication from Widgets to Nodes

For custom widgets, since QWidgets are QObjects, you can directly add all your signals as static attributes to your custom widget class.

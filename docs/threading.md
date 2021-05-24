# Threading

<!-- First, I want to mention that the system often receives  changes, and especially the exact way in which nodes communicate with their widgets using signals and slots as described below might change drastically in the future to enable more scalable deployment. The instructions described here only apply on threaded applications. -->

## Overview

One of the biggest internal changes in `ryvencore-qt`/`ryvencore` compared to Ryven 2, is the threading compatibility. `ryvencore` provides abstract components and `ryvencore-qt` provides the Qt GUI for the flows (plus some convenience widgets). Therefore, in order to run a session instance in a thread different from the GUI thread, the internal communication between `ryvencore` and `ryvencore-qt` must be set up in a thread save way. To achieve this, `ryvencore-qt` provides custom *WRAPPER* classes for all `ryvencore` components that the frontend needs to communicate with directly. Those wrappers do almost nothing but adding Qt signals to all the API methods, so every time an API method of the backend has been executed, a Qt signal is sent which the frontend components who need to get notified of this API method execution (like creation of a new node must notify the `FlowView`) listen for.

> [!WARNING]
> Do not call `Session.serialize()` from different threads in an unsynchronized way, as the serialization of the `FlowView` is currently "joined" with the session's thread by setting an attribute (see `Session.serialize()` implementation). This may change at some point.

<!-- ## Characteristics

You should be careful with accessing session contents from multiple different threads simultaneously. There are API methods that trigger procedures in the GUI components (like initialization) and wait wait for them to complete. To ensure that these procedures complete *during* the execution of the according API method, the calling abstract component (like `Script`) uses a temp attribute which it sets to `None` before triggering the intended procedure in the GUI thread via a signal, and then waits for this attribute to be set to something else by the component executing the procedure in the main/GUI thread. -->

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

    def update_event(self, input_called=-1):
        # ...
        self.signals.notify_gui.emit(something)
        # ...
```

### Communication from Widgets to Nodes

For custom widgets, since QWidgets are QObjects, you can directly add all your signals as static attributes to your custom widget class.

<!-- ## Further Thoughts

I want to mention that ryvencore could probably be modified easily to run without any GUI. Furthermore, all abstract components, such as `Session`, `Script`, `Flow` etc. only have dependency to Qt's signals right now. Depending on in which environments ryvencore should run in the future, there might be mayor changes to the communication system in the future, to make it more scalable. If you want to contribute to this, you can try to modify ryvencore such that it can easily run without GUI. The advantage of using something else than Qt's signals and slots could be that in case running ryvencore without GUI is a frequent use case, this could be done without any Qt dependencies at all. For thoughts and showcases on this, feel free to open issues and discussions. -->

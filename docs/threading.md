# Threading

First, I want to mention that the system is often subject to frequent changes, and especially the exact way in which nodes communicate with their widgets using signals and slots as described below might change drastically in the future to enable more scalable deployment. The instructions described here only apply on threaded applications.

## Overview

One of the biggest internal changes in ryvencore, compared to Ryven 2, is threading compatibility. ryvencore provides abstract components *and* the GUI for the flows, so in order to run a session instance inside a threaded application, the internal communication between those components must be set up in a thread save way. In ryvencore this is currently done using Qt's standard signals and slots system.

## Characteristics

You should be careful with accessing session contents from multiple different threads simultaneously. There are API methods that trigger procedures in the GUI components (like initialization) and wait wait for them to complete. To ensure that these procedures complete *during* the execution of the according API method, the calling abstract component (like `Script`) uses a temp attribute which it sets to `None` before triggering the intended procedure in the GUI thread via a signal, and then waits for this attribute to be set to something else by the component executing the procedure in the main/GUI thread.

## Programming Nodes

A `Node` object lives in the same thread as the `Session`. Their GUI items, however, including all **custom widgets**, live in the GUI thread. Therefore, you need to make sure that the communication between your nodes and their custom widgets is thread save, which usually means implemented using Qt's signals and slots. 

### Communication from Nodes to Widgets

If your node needs to send signals to the widgets, there currently is a `SIGNALS` class part of `Node`, which you can reimplement, which will be instantiated during initialization and can be accessed through the attribute `Node.signals`. Connections from the node to the widgets are supposed to be built in the `Node`'s `place_event()`.

!!! note
    The `Node`'s `place_event()` method is called once the node has been initialized and all GUI has too, so I suggest using it only for connecting to the GUI.
    
Concretely, it works like this:

```python
import ryvencore_qt as rc
from PySide2.QtCore import QObject, Signal


class MyNode(rc.Node):

    title = '...'
    description = '...'
    # ...

    class SIGNALS(QObject):
        my_signal = Signal(object)

    def place_event(self):
        self.signals.my_signal.connect(self.main_widget().some_method)

    def update_event(self, input_called=-1):
        # ...
        self.signals.my_signal.emit(something)
        # ...
```

### Communication from Widgets to Nodes

For custom widgets, since QWidgets are QObjects, you can directly add all your signals as static attributes to your custom widget class.

## Further Thoughts

I want to mention that ryvencore could probably be modified easily to run without any GUI. Furthermore, all abstract components, such as `Session`, `Script`, `Flow` etc. only have dependency to Qt's signals right now. Depending on in which environments ryvencore should run in the future, there might be mayor changes to the communication system in the future, to make it more scalable. If you want to contribute to this, you can try to modify ryvencore such that it can easily run without GUI. The advantage of using something else than Qt's signals and slots could be that in case running ryvencore without GUI is a frequent use case, this could be done without any Qt dependencies at all. For thoughts and showcases on this, feel free to open issues and discussions.

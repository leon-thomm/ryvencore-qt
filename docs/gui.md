# GUI

Adding intuitive GUI to your nodes is of mayor importance to create a nice interface. Therefore, in ryvencore you can register your very own widget classes and are not restricted to some fixed set of available standard widgets. However, there are also a few convenience widgets which make your life a lot easier.

## Convenience GUI Classes

All those classes only use ryvencore's public API and you could implement them all yourself. The list should grow over time. All these are classes come from Ryven.

### Script List Widget

A simple list widget for creating, renaming and deleting scripts and function-scripts. To catch the according events (i.e. `script_created`, `script_renamed` etc), use the signals of the `Session` class.

### Variables List Widget

A synchronous widget to the script list widget for script variables. You can create, rename, delete script variables and change their values which results in all registered receivers to update.

### Log Widget

A very basic widget for outputting data of a log. Use the `Script.logger.new_log_created()` signal to catch instantiation of new logs. If you want to implement your own, you will need the `Log`'s signals `enabled`, `disabled`, `cleared`, `wrote`.

### Input Widgets

- `std line edit ` aka `std line edit m`, `std line edit s`, `std line edit l`
- `std spin box`

For styling those, refer to thir classes `RCIW_BUILTIN_LineEdit`, `RCIW_BUILTIN_SpinBox`.

I really would like to add many more widgets to this list in the future.

## Writing your own GUI

All custom widgets must be QWidgets and subclass one of ryvencore's widget base classes. Both classes have similar functionality for serialization and loading as `Node`. They have methods `get_state() -> dict` and `set_state(data: dict)` (and also a `remove_event()` right now) to subclass.

### Main Widget

A main widget must additionally subclass ryvencore's `MWB` (MainWidgetBase) class. Example:

```python
import ryvencore_qt as rc
from PySide2.QtWidgets import QPushButton


class MyMainWidget(rc.MWB, QPushButton):
    def __init__(self, params):
        rc.MWB.__init__(self, params)
        QPushButton.__init__(self)
        
        # then do your stuff like
        self.setEnabled(False)
        self.clicked.connect(self.node.update)
```

After `rc.MWB.__init__(self, params)`, you have access to the node object via `self.node`. A custom main widget class must be referenced in the node's class definition

```python
class MyNode(rc.Node):
    
    title = '...'
    # ...
    main_widget_class = MyMainWidget
    # ...

    def __init__(self, params):
        super().__init__(params)
    
    # ...
```

### Input Widget

An input widget must additionally subclass ryvencore's `IWB` (InputWidgetBase) class. The initialization process is exactly the same as with `MWB` shown in the example above. After the `IWB` constructor the refs `self.node` to the node object and `self.input` for the node's input port object which contains the widget are available. Custom input widget classes, together with the names that should be used to refer to them node internally, must be referenced in the node's class definition

```python
class MyNode(rc.Node):
    
    title = '...'
    # ...
    input_widget_classes = {'some input widget': MyInputWidget}
    # ...

    def __init__(self, params):
        super().__init__(params)
    
    # ...
```
# API Reference

This page provides descriptions of the API methods of `ryvencore` **and** `ryvencore-qt` (which just adds a few GUI related methods and Qt signals to the `ryvencore` API). If you plan to deploy your nodes without frontend, then keep in mind to use `ryvencore-qt` API strictly only in places where existence of a frontend is guaranteed (you can usually use the `self.session.gui: boolean` in the `Node` class). Assume all methods are `ryvencore` API, `ryvencore-qt` methods or sections are marked with *`RC-QT`*.

Also, please use argument names (like `session.create_script(title='something')`) as some parameter orderings will change.

## [class] `Session`

A session is the top-most interface to your components. Usually you will want to create one session per application instance.

### Qt Signals *[`RC-QT`]*

The following signals are useful if you use custom widgets for listing the scripts. You can connect these signals to the corresponding GUI classes to make your GUI adapt.

| Name                              | Parameters                                | Emitted when...                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `new_script_created`              | `Script`                                  | a new script is created.     |
| `flow_view_created`               | `Script, Flow`                            | the `FlowView` (the widget) for a scripts's flow has been created.   |
| `script_renamed`                  | `Script`                                  | a script has been renamed.   |
| `script_deleted`                  | `Script`                                  | a script has been deleted.   |

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `nodes`                           | A list of all registered nodes (the *classes*).           |
| `scripts: [Script]`               | A list of all scripts (including macros).           |
| `design: Design`                  | *[`RC-QT`]* The session's `Design` reference.         |
| `flow_views: dict`                | *[`RC-QT`]* The flow views (widgets) identified by the script owning the flow.         |

### Methods

`Session(gui_parent: QWidget = None, custom_classes: dict = None)`

*don't use other arguments*

| Parameter                         | Description                               |
| --------------------------------- | ----------------------------------------- |
| `gui_parent`                      | The parent (i.e. MainWindow) for the GUI, only important for threaded applications. |
| `custom_classes`                  | You can provide custom implementations of classes. |

`register_node(node)`

Registers a Node which then can be accessed in all scripts,

> [!NOTE]
> You can register and un-register nodes at any time! Un-registering a node does not affect existent instances (so you can also re-register nodes).

`register_nodes(node_classes: list)`

Convenience class for registering a list of nodes at once.

`unregister_node(node_class)`

Un-register a node which will then be removed from the internal list. Existing instances won't be affected.

`create_script(title: str, create_default_logs=True, flow_view_size: list = None) -> Script`

| Parameter                         | Description                               |
| --------------------------------- | ----------------------------------------- |
| `title`                           | The title of the new script. **Script titles are identifiers, they have to be unique.** |
| `flow_view_size`                  | The pixel size of the flow in format `[x, y]`. |
| `create_default_logs`             | Whether the script's default logs (*Global* and *Errors*) should get created. You can also do them later via `Script.logs_manager.create_default_logs()`. |

Creates and returns a script which triggers the `Session.new_script_created()` signal. By the time the script is returned, all abstract as well as the GUI components have been created.

`rename_script(script: Script, title: str) -> bool`

Renames an existing script which triggers the `Session.script_renamed` signal and returns `True` if `title` is valid (unique), otherwise it just returns `False`.

`script_title_valid(title: str) -> bool`

Checks whether a considered title for a new script is valid (i.e. unique). Done automatically when using `Session.rename_script()`.

`delete_script(script: Script)`

Deletes a script and triggers the `Session.script_deleted` signal. If the script is a macro, it also un-registers the macro node (existing instances are unaffected).

`load(project: dict) -> [Script]`

Loads a project, i.e. creates all scripts saved in the provided project dict and builds all their contents including the flows.

`serialize() -> dict`

Returns the project as dict to be saved and loaded again using load().

`info_messenger()`

Returns a reference to the `InfoMsgs` class for printing only if info messages are enabled.

`all_node_objects() -> list`

Returns a list of all Node **instances** (objects) from all flows of the session's scripts.

## [class] `InfoMsgs`

The `InfoMsgs` class just provides a simple way to print such that the additional info is disabled by default but can be enabled for troubleshooting.

### Methods

`enable()`

Enables the printing.

`disable()`

Disables the printing.

`write(*args)`

Writes a list of arguments stringified using `str()` in the same format `print()` does.

`write_err(*args)`

Same as `write(*args)` but for (usually highlighted) errors.

## [class] `Script`

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `title`                           | the script's current tile                 |
| `session`                         | a ref to the session                      |
| `flow`                            | the script's flow                         |
| `logs_manager`                    | the script's logs manager                 |
| `vars_manager`                    | the script's variables manager            |

## [class] `LogsManager`

Manages all the logs of a script.

### Qt Signals *[`RC-QT`]*

| Name                              | Parameters                                | Emitted when...                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `new_logger_created`              | `Logger`                                  | a new logger has been created, either through `new_logger()` or automatically (default logs). |

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `script: Script`                  | A ref to the script.                       |
| `loggers: [Logger]`               | A list of all loggers registered in the script. |

### Methods

`create_default_loggers()`

Creates the default script's logs *Global* and *Errors*. This is done automatically if you didn't disable default logs when creating the the script.

> [!NOTE]
> I might remove default logs from `ryvencore` soon since their specifications depend on the use case and they can easily be added manually with exact same behavior.

`new_logger(title: str) -> Logger`

Creates an individual new logger which you can use for anything. Emits the `new_log_created` signal.

## [class] `Logger(logging.Logger)`

The `Logger` class inherits python's `logging.Logger`.

### Qt Signals *[`RC-QT`]*

The following signals are useful if you implement your own logs GUI.

| Name                              | Parameters                                | Emitted when...                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `sig_enabled`                     | `-`                                       | the log has been enabled. Can happen automatically for instance when a node which requested the logger was removed from the flow and has been restored through an undo command, the loggers get re-enabled. |
| `sig_disabled`                    | `-`                                       | the log has been disabled. Can also happen automatically as in the above example. |

`enable()` 

Enables the logger and emits `enabled`.

`disable()`

Disables the logger and emits `disabled`.

## [class] `VarsManager`

### Qt Signals *[`RC-QT`]*

The following signals are useful if you implement your own script variables list GUI.

| Name                              | Parameters                                | Emitted when...                           |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `new_var_created`                 | `Variable`                                | a new script variable has been created.   |
| `var_deleted`                     | `Variable`                                | a script variable has been deleted.       |
| `var_val_changed`                 | `Variable, object`                        | a script variable's value changed.        |

#### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `variables: [Variable]`           | A list of all the managed script variables.    |

### Methods

`var_name_valid(name: str) -> bool`

Checks whether `name` is a valid name for a new script variable.

`create_new_var(name: str, val=None) -> Variable`

Checks `var_name_valid()`, creates and returns a new script variable with given name and initial value and emits `new_var_created` in case of success, and returns `None` otherwise.

`get_var(name) -> Variable`

Returns script variable with given name or `None` if it couldn't be found.

`get_var_val(name)`

Returns the value of a script variable with given name or `None` if it couldn't be found.

`set_var(name, val) -> bool`

Sets the value of an existing script variable. Returns `False` if the variable couldn't be found.

`delete_var(var: Variable)`

Deletes a script variable and emits `var_deleted`.

`register_receiver(receiver, var_name: str, method)`

Registers a variable receiver method. A registered receiver method gets triggered every time the value of a variable with the given name changes (also when it gets created).

`unregister_receiver(receiver, var_name: str, method) -> bool`

Un-registers a variable receiver method. Returns `False` if the receiver wasn't registered.

## [class] `Flow`

The `Flow` class represents the abstract graph and stores all the node objects and connections between them. You can access a script's flow via `Script.flow`.

### Qt Signals *[`RC-QT`]*

| Name                              | Parameters                                | Emitted when...                         |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `node_added`                      | `Node`                                    | a node has been added to the flow (also happens when a removed node is restored through an undo). |
| `node_removed`                    | `Node`                                    | a node has been removed from the flow. |
| `connection_added`                | `Connection`                              | a connection has been added. |
| `connection_removed`              | `Connection`                              | a connection has been removed. |
| `algorithm_mode_changed`          | `str`                                     | the flow's algorithm mode changed, see `Flow.set_algorithm_mode()`. |

#### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `session: Session`                | A ref to the owning session. |
| `script: Script`                  | A ref to the owning script. |
| `nodes: [Node]`                   | A list of all current nodes. |
| `connections: [Connection]`       | A list of all current connections. |

### Methods

`create_node(node_class, config=None)`

Creates, adds and returns a new node object. Emits `node_added`, see `add_node()`.

`add_node(node: Node)`

Adds an existing node object to the flow. Emits `node_added`.

`remove_node(node: Node)`

Removes a node and all incident connections from the flow. Emits `node_removed`.

`connect_nodes(p1: NodePort, p2: NodePort) -> Connection`

To connect or disconnect nodes. If the connection is valid and doesn't exist, it connects two node ports and returns the new connection.

Returns `None` if

1. the connection request is invalid (f.ex. when `p1` and `p2` are both inputs)
2. the connection exists, which means it gets removed

`add_connection(c: Connection)`

Adds an existing connection object to the flow and registers the connection in the connection's output node port and input node port.

`remove_connection(c: Connection)`

Removes a connection from the flow and un-registers the connection in the connection's output node port and input node port.

`algorithm_mode() -> str`

Returns the flow's current algorithms mode (`'data'` for *data flow* or `'exec'` for *execution flow*). By default, flows run in data flow mode.

`set_algorithm_mode(mode: str)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `mode`                | `'data'` or `'exec'`                      |

## [class] FlowView *[`RC-QT`]*

The `FlowView` is the GUI representative for the `Flow`, i.e. the widget, and is accessible via `session.flow_views[script]`.

`get_viewport_img() -> QImage`

Returns a cleared image of the current viewport.

`get_whole_scene_img() -> QImage`

Returns an image of the whole scene, scaled accordingly to current scale factor.

> [!WARNING|label:Bug]
    Currently, this only works relative to the viewport's position (downwards and to the right), so the user has to scroll to the top left corner in order to get the full scene.

<!-- `show_framerate(show: bool = True, m_sec_interval: int = 1000)` -->

## [class] `Node`

Actual nodes are subclasses of the `Node` class. The individual node objects will be instances of the according class.

> EXAMPLE
> ``` python
> import ryvencore_qt as rc
>
> class PrintNode(rc.Node):
>     """Prints your data"""    
> 
>     title = 'Print'
>     init_inputs = [
>         rc.NodeInput()
>     ]
>     init_outputs = []
>     color = '#A9D5EF'
> 
>     # we could also skip the constructor here
>     def __init__(self, params):
>         super().__init__(params)
> 
>     def update_event(self, inp=-1):
>         data = self.input(0)  # get data from the first input
>         print(data)
> ```

### Static Attributes

Use the following static attributes to define the basic properties of your node.

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `title: str`                      | The node's initial title. It doesn't have to be unique.    |
| `tags: list`                      | A list of string tags to support search.    |
| `version: str`                    | The version tag of your node. Using this can save you a lot of trouble.    |
| `init_inputs: [NodeInputBP]`      | Initial inputs.    |
| `init_outputs: [NodeOutputBP]`    | Initial outputs.    |
| `identifier: str`                 | A unique identifier string. If nothing is provided, the node's class name will be used. |
| `main_widget_class`               | *[`RC-QT`]* A reference to the class of the `main_widget` if used.    |
| `main_widget_pos: str`            | *[`RC-QT`]* `'between ports'` or `'below ports'` if a `main_widget` is used. |
| `input_widget_classes: dict`      | *[`RC-QT`]* A dict for custom input widgets in format `{name: class}`. |
| `style: str`                      | *[`RC-QT`]* `'normal'` (default) or `'small'`. |
| `color: str`                      | *[`RC-QT`]* A color in hex format. |
| `icon: str`                       | *[`RC-QT`]* The file path to an icon. |
<!-- | `type_: str`                      | Optional way to specify the node.    | -->
<!-- | `description_html: str`           | A description in html format.    | -->

### Methods

Methods meant to be overridden by your node implementation to define behavior are marked as *[override]*.

*[override]* `update_event(inp=-1)`

Triggered when the node is updated through `update()`.

> EXAMPLE
> ``` python
> def update_event(self, inp=-1):
>     arr = self.input(0)
>     index = self.input(1)
>     self.set_output_val(0, arr[index])
> ```

*[override]* `place_event()`

Called when the node is added to the flow. Notice that this can happen multiple times, for instance when undoing a remove operation in the flow, but also when the node is first constructed and placed in the flow. The `place_event` is called **before** any incident connections are built, so it is often used to trigger updates since setting outputs here does not affect any other presumably sequential nodes since the connections are not added yet.

*[override]* `remove_event()`

Called when the node is removed from the flow. Can also happen multiple times. You might want to stop timers etc. here.

*[override]* `view_place_event()` *[`RC-QT`]*

Called once the whole GUI of the node (including custom widgets) has initialized, which is important when using custom widgets. Only do GUI related work here.

*[override]* `get_state() -> dict`

In case your node implements sequential behavior, provide all state defining data here in a dictionary. The dict will be serialized using `pickle` and `base64` encoding when copying/cutting nodes or when saving the project. Do the reverse in `set_state(data)`, see below.

*[override]* `set_state(data: dict, version)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `data`                | Holds the exact dictionary you returned in `get_state()`. |
| `version`             | The `version` of you node when it created `data` in `get_state()`. |

Reinitialize your node's state here.

> [!NOTE]
> All framework-internal objects, such as the `actions` dict, **as well as inputs and outputs** get saved and restored automatically exactly as they were when the node was serialized. If you added some inputs, for instance, don't add them again manually in `set_state()`, this happens automatically. Just update your own internal variables.

`update(inp=-1)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `inp`                 | If the node has exec inputs, you might want to pass the input the update is referring to. |

Triggers `update_event()`.

`input(index: int)`

Returns the data held at the input with given index. If the input is not connected but has a widget, the input will return the widget's data, otherwise it will return `None`.

`exec_output(index: int)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `index`               | Index of the output (has to be an exec output). |

Executes the output with given index.

`set_output_val(index: int, val)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `index`               | Index of the output (has to be a data output). |
| `val`                 | The data to propagate. This can be anything. |

In data-flows, this causes update events in all connected nodes. This way, change of data is forward propagated through all nodes that depend on it.

`new_logger(title: str) -> Logger`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `title`               | The logger's display title. |

Creates and returns a new logger, owned by the node.

`disable_loggers()`

Disables all loggers owned by the node which can cause log widgets to adapt for example. Gets called automatically when the node is removed.

`enable_logs()`

Enables all loggers owned by the node. Gets called automatically when a node is added to the flow.

`update_shape()` *[`RC-QT`]*

Causes recompilation of the whole shape of the GUI item of the node.

`create_input(type_: str = 'data', label: str = '', add_config={}, insert: int = None)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `type_`               | `'data'` or `'exec'` |
| `label`               | The input's displayed label string. |
| `add_config`          | For additional config data for the frontend, used for custom widgets in `ryvencore-qt`, format: `{'widget name': str, 'widget pos': 'besides' | 'below'}`. |
| `insert`              | Set to a value if you want to insert the input at a specific position. |

`create_input_dt(dtype: DType, label: str = '', insert: int = None)`

Creates a `dtype` data input.

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `dtype`               | Provide a `dtype` object, for instance `dtypes.Integer(default=10)`. |

other params same as above.

`ryvencore-qt` will automatically add default widgets for the supported `dtypes`.

`delete_input(index: int)`

Removes the input at `index` and all connections incident to this input.

`create_output(type_: str = 'data', label: str = '', insert: int = None)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `type_`               | `'data'` or `'exec'` |
| `label`               | The output's displayed label string. |
| `insert`              | Set to a value if you want to insert the output at a specific position. |

`delete_output(index: int)`

Removes the output at `index` and all connections incident to this output.

`get_var_val(name: str)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `name`                | script variable's name |

Returns the current value of a script variable with name `name`, and `None` if it couldn't be found.

`set_var_val(name: str, val)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `name`                | script variable's name |
| `val`                 | the variable's value |

Sets the value of a script variable (which causes all registered receivers to update).

`register_var_receiver(name: str, method)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `name`                | script variable's name |
| `method`              | a ref to the receiver method |

Registers a method as receiver for changes of script variable with given name.

> EXAMPLE
> ``` python
> # connect to variable changes
> # self.var_val_updated refers to the receiver method
> self.register_var_receiver('x', self.var_val_updated)
> self.used_variable_names.append('x')
> ```

`unregister_var_receiver(name: str)`

Un-registers a previously registered variable receiver.

<!-- [Edit this page on GitHub](https://github.com/leon-thomm/ryvencore){: .md-button } -->
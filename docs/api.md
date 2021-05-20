# API Reference

## [class] `Session`

A session is the top-most interface to your components. Usually you will want to create one session per application instance, but you could create multiple ones to have different independent environments in one application.

### Signals

The following signals are useful if you use custom widgets for listing the scripts. You can connect these signals to the corresponding GUI classes to make your GUI adapt. These signals equally apply on function-scripts.

| Name                              | Parameters                                | Description                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `new_script_created`              | `Script`                                  | Emitted when a new script is created.     |
| `script_renamed`                  | `Script`                                  | Emitted when a script has been renamed.   |
| `script_deleted`                  | `Script`                                  | Emitted when a script has been deleted.   |

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `nodes`                           | A list of all registered nodes.           |
| `design`                          | The session's `Design` reference.         |

### Methods

`Session(threaded: bool = False, gui_parent: QWidget = None, flow_theme_name=None, performance_mode=None, data_conn_class=None, data_conn_item_class=None, exec_conn_class=None, exec_conn_item_class=None, parent: QObject = None)`

| Parameter                         | Description                               |
| --------------------------------- | ----------------------------------------- |
| `threaded: bool = False`          | True for threaded applications. |
| `gui_parent: QObject = None`      | The parent (i.e. MainWindow) for the GUI, only important for threaded applications |
| `flow_theme_name`                 | The name of the flow theme used |
| `performance_mode`                | `'pretty'` or `'fast'` |
| `data_conn_class=None`            | A ref to your custom implementation of `DataConnection` if you want to provide one. |
| `data_conn_item_class=None`       | A ref to your custom implementation of `DataConnectionItem` if you want to provide one. |
| `exec_conn_class=None`            | A ref to your custom implementation of `ExecConnection` if you want to provide one. |
| `exec_conn_item_class=None`       | A ref to your custom implementation of `ExecConnectionItem` if you want to provide one. |
| `parent: QObject = None`          | The session's parent object. |

This list (and especially the order) might get changed in the future multiple times, so make sure you always use the parameter names. Also, while I think subclassing the connection classes is a great feature, the default class's implementations are young and might receive changes in the future.

`register_node(node)`

Registers a Node which then can be accessed in all scripts,

> [!NOTE]
> You can register and unregister nodes at any time! Unregistering a node does not affect existent instances (so you can also reregister nodes).

`register_nodes(node_classes: list)`

Convenience class for registering a list of nodes at once.

`unregister_node(node_class)`

Unregisters a node which will then be removed from the internal list. Existing instances won't be affected.

`create_script(title: str, flow_view_size: list = None, create_default_logs=True) -> Script`

| Parameter                         | Description                               |
| --------------------------------- | ----------------------------------------- |
| `title`                           | The title of the new script. Script titles have to be unique. |
| `flow_view_size`                  | the pixel size of the flow in format `[x, y]`. |
| `create_default_logs`             | Indicates whether the script's default logs (*Global* and *Errors*) should get created. You can also do this later manually via `Script.logger.create_default_logs()`. |

Creates and returns a script which triggers the `Session.new_script_created()` signal. By the time the script is returned, all abstract as well as the GUI components have been created.

`create_func_script(title: str, flow_view_size: list = None, create_default_logs=True) -> Script`

Same thing as `Session.create_script()` for `FunctionScript`s.

`all_scripts() -> list`

Returns a list containing all scripts and function scripts.

`check_new_script_title_validity(title: str) -> bool`

Checks whether a considered title for a new script (i.e. unique) is valid or not.

`rename_script(script: Script, title: str)`

Renames an existing script which triggers the `Session.script_renamed` signal.

`delete_script(script: Script)`

Deletes a script and triggers the `Session.script_deleted` signal.

`load(project: dict) -> bool`

Loads a project, which means creating all scripts saved in the provided project dict and building all their contents including the flows.

`serialize() -> dict`

Returns the project as dict to be saved and loaded again using load().

`info_messenger()`

Returns a reference to the `InfoMsgs` class for printing only if info messages are enabled.

`all_nodes() -> list`

Returns a list of all Node **instances** (objects) from all flows of the session's scripts.

`set_stylesheet(s: str)`

Sets the session's global stylesheet which can be accessed by nodes and their widgets.

## [class] `InfoMsgs`

The `InfoMsgs` class just provides a convenient way to print, such that the additional info is disabled by default but can be enabled for troubleshooting.

### Methods

`enable()`

Enables the printing.

`disable()`

Disables the printing.

`write(*args)`

Writes a list of arguments stringified using `str()` in the same format `print()` does.

`write_err(*args)`

Same as `write(*args)` but for highlighted errors.

## [class] `Script`

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `session`                         | a ref to the session                      |
| `flow`                            | the script's flow                         |
| `flow view`                       | the script's flow view, which is the GUI representative of the flow |
| `logger`                          | the script's logger                       |
| `vars_manager`                    | the script's vars manager for managing the script variables |
| `title`                           | the script's current tile                 |

The `FunctionScript` class used for function scripts extends the `Script`'s functionality by a few things such as input node and output node that get added automatically to the flow.

## [class] `Logger`

The logger manages all the logs of a script.

### Signals

| Name                              | Parameters                                | Description                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `new_log_created`                 | `Log`                                     | Emitted when a new Log has been created, either manually through `new_log()` or automatically (default logs). |

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `script: Script`                  | A ref to the script.                       |
| `logs: list`                      | A list of all the logs registered in the script. |

### Methods

`create_default_logs()`

Creates the default script's logs *Global* and *Errors*. This is done automatically if you didn't disable default logs when creating the the script.

`log_message(msg: str, target: str = '')`

Logs a message to all logs with name `target`. If you want to print to a specific log individual log (not one of the default logs), you should use the `Log.write()` method.

`new_log(title: str) -> Log`

Creates an individual new log which you can use for anything. Emits the `new_log_created` signal.

## [class] `Log`

### Signals

The following signals are useful if you implement your own log GUI. Connect them to your widget so it catches those events.

| Name                              | Parameters                                | Description                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `enabled`                         | `-`                                       | Emitted when the log has been enabled. For instance when a Node which requested the log was removed from the flow and has been restored through an undo command, the logs get 'reenabled'. |
| `disabled`                        | `-`                                       | Emitted when the log has been disabled. For instance when a Node which requested the log has been removed from the flow. |
| `wrote`                           | `str`                                     | Emitted when something wrote a message to the log. |
| `cleared`                         | `-`                                       | Emitted when the log has been cleared. |

### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `title: str`                      | The log's title string.                    |
| `lines: [str]`                    | A list of all logged strings (doesn't get cleared when the log gets cleared). |
| `current_lines: [str]`            | All *current* `lines`, i.e. the ones that haven't been cleared. |

### Methods

`write(*args)`

Writes a list of arguments to the log like `print()` does, stringifying everything using `str()`.

`clear()`

Clears the log and emits `cleared`. This doesn't clear the `lines` attribute!

`disable()`

Disables the log and emits `disabled`. A disabled log does not `write` anymore.

`enable()` 

Enables the log and emits `enabled`.

`save_to_file(filepath: str, all_lines=True)`

Saves `lines` to a file. If `all_lines` is `False` it only saves `current_lines`.

## [class] `VarsManager`

### Signals

The following signals are useful if you implement your own script vars list GUI.

| Name                              | Parameters                                | Description                               |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `new_var_created`                 | `Variable`                                | Emitted when a new script variable has been created. |
| `var_deleted`                     | `Variable`                                | Emitted when a script variable has been deleted. |
| `var_val_changed`                 | `Variable, object`                        | Emitted when a script variable's value has been changed. |

#### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `variables: [Variable]`           | A list of all the managed script vars.    |

### Methods

`check_new_var_name_validity(name: str) -> bool`

Checks whether `name` is a valid name for a new script variable.

`create_new_var(name: str, val=None) -> Variable`

Creates and returns a new script variable with given name and initial value. Emits the `new_var_created` signal.

`get_var(name) -> Variable`

Returns script variable with given name or `None` if it couldn't be found.

`get_var_val(name)`

Returns the value of a script variable with given name or `None` if it couldn't be found.

`set_var(name, val) -> bool`

Sets the value of an existing script variable. Returns `False` if the var couldn't be found.

`delete_variable(var: Variable)`

Deletes a script variable and emits `var_deleted`.

`register_receiver(receiver, var_name: str, method)`

Registers a var receiver. A registered receiver (method) gets triggered every time the value of a variable with the given name changes (also when it gets created).

`unregister_receiver(receiver, var_name: str) -> bool`

Unregisters a var receiver.

## [class] `Flow`

The `Flow` class represents the abstract flow (no GUI) and stores all the node objects and connections. You can access a script's flow via `Script.flow`.

### Signals

| Name                              | Parameters                                | Emitted when...                         |
| --------------------------------- | ----------------------------------------- | ----------------------------------------- |
| `node_added`                      | `Node`                                    | a node has been added (also happens when a reoved node is restored through an undo). |
| `node_removed`                    | `Node`                                    | a node has been removed. |
| `connection_added`                | `Connection`                              | a connection has been added. |
| `connection_removed`              | `Connection`                              | a connection has been removed. |
| `algorithm_mode_changed`          | `str`                                     | the flow's algorithm mode changed, see `set_algorithm_mode()`. |

#### Attributes

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `nodes: [Node]`                   | A list of all currently present nodes. |
| `connections: [Connection]`       | A list of all current connections. |

### Methods

`create_node(node_class, config=None)`

Creates, adds and returns a new node object; emits node_added.

`remove_node(node: Node)`

Removes a node from internal list without deleting it; emits node_removed.

`algorithm_mode() -> str`

Returns the flow's current algorithms mode (`data` for *data flow* or `exec` for *execution flow*). By default, flows run in data flow mode.

`set_algorithm_mode(mode: str)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `mode`                | `'data'` or `'exec'`                      |

## [class] FlowView

The `FlowView` is the GUI representative for the `Flow`, i.e. the widget, and is accessible via `Script.flow_view`.

`get_viewport_img() -> QImage`

Returns a clear image of the viewport.

`get_whole_scene_img() -> QImage`

Returns an image of the whole scene, scaled accordingly to current scale factor.

!!! bug
    Currently, this only works from the viewport's position down and right, so the user has to scroll to the top left corner in order to get the full scene.

`show_framerate(show: bool = True, m_sec_interval: int = 1000)`

**WIP**

## [class] `Node`

Nodes are defined by subclasses of `Node`. The individual objects will be instances of the according class. The `Node` class contains the whole API for programming nodes.

<details>
  <summary>Example</summary>
  

``` python
class PrintNode(rc.Node):

    title = 'Print'
    description = 'prints your data'
    init_inputs = [
        rc.NodeInput('data')
    ]
    init_outputs = []
    color = '#A9D5EF'

    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(params)

    def update_event(self, input_called=-1):
        data = self.input(0)  # get data from the first input
        print(data)
```


</details>

### Static Attributes

Use the following static attributes to define the basic properties of your node.

| Name                              | Description                               |
| --------------------------------- | ----------------------------------------- |
| `title: str`                      | The Node's initial title. It doesn't have to be unique.    |
| `type_: str`                      | Optional way to specify the node.    |
| `init_inputs: [NodeInput]`        | Initial inputs.    |
| `init_outputs: [NodeOutput]`      | Initial outputs.    |
| `identifier: str`                 | A unique identifier string. If nothing is provided, the node's class name will be used. |
| `description: str`                | A description shown as tool tip when hovering about the node.    |
| `description_html: str`           | A description in html format.    |
| `main_widget_class: list`         | A reference to the class of the `main_widget` if used.    |
| `main_widget_pos: str`            | `'between ports'` or `'below ports'` if a `main_widget` is used. |
| `input_widget_classes: dict`      | A dict for custom input widgets in format `{name: class}` which can then be used when defining initial data inputs or creating ones at runtime. |
| `style: str`                      | `'extended'` (default) or `'small'`. Those are the two different design styles for nodes. |
| `color: str`                      | A color in hex format. |
| `icon: str`                       | The file path to an icon. |

### Methods

[override] `update_event(input_called=-1)`

Triggered when the Node is activated, usually through `Node.update()`.

> EXAMPLE
> ``` python
> def update_event(self, input_called=-1):
>     arr = self.input(0)
>     index = self.input(1)
>     self.set_output_val(0, arr[index])
> ```

[override] `get_data() -> dict`

In this method, you need to provide all your internal data that defines your Node's current state (if there are different states). The dict will be encoded using `pickle` and `base64` when copying nodes (via ctrl+c) or when saving the project. You do the reverse in `Node.set_data(data)` (see below). 

> EXAMPLE
>
> Example for a *+* Node with a dynamic number of inputs, which can be changed by the user.
> ``` python
> def get_data(self):
>     data = {'num inputs': self.num_inputs}
>     return data
> ```


[override] `set_data(data: dict)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `data`                | Holds the exact value you returned in `Node.get_data()`. |

Here you do the reverse of what you did in `Node.get_data()`.

> [!NOTE]
> All ryvencore internal objects, such as the `special_actions` dict, **as well as inputs and outputs** get saved and restored automatically by ryvencore exactly as they were when the flow was saved. So, if you added some inputs for example, don't add them again manually in `set_data()` according to your attribute which indicates how many you added, this happens automatically. Just update your own internal variables.


> EXAMPLE
> ``` python
> def set_data(self, data):
>     self.num_inputs = data['num inputs']
> ```

[override] `place_event()`

Triggered when the Node has been added to the flow **and all GUI has been initialized**. Don't try to access GUI components in the constructor, they don't exist yet, use this method instead.

[override] `remove_event()`

Triggered when the Node is removed from the flow. You can use this method do stop threads and timers etc. Note that this action might be undone by an undo operation by the user, in this case the exact Node object will just be placed again resulting in a `place_event()`.



> EXAMPLE
>
> Example from a *clock* Node running a timer.
> ``` python
> def remove_event(self):
>     self.timer.stop()
> ```


</details>


`update(input_called=-1)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `input_called`        | If the Node is active, living in an exec flow, i.e. if it has exec inputs, you might want to pass the input the update is supposed to refer to. |

Triggers an update event.

`input(index: int)`

Returns the data that is at the data input with given index. If the input is not connected, the input will return the widget's data (if it has a widget), otherwise it will return the data from the output of the connected Node. In all other cases, it returns `None`.

`exec_output(index: int)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `index`               | Index of the output. It has to be an exec output. |

Executes the output with given index.

`set_output_val(index: int, val)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `index`               | Index of the output. It has to be a data output. |
| `val`                 | The data that gets set at the output. This can be anything. |

In dataflows, this causes update events in all connected nodes. This way, change of data is forward propagated through all nodes that depend on it.

`new_log(title: str) -> Log`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `title`               | The log's display title. |

Creates and returns a new log, owned by the Node.

`disable_logs()`

Disables all logs owned by the Node. The convenience Log widget ryvencore provides then can be hidden. All logs owned by a Node automatically get disabled when the Node is removed.

`enable_logs()`

Enables all logs owned by the Node. The convenience Log widget ryvencore provides then shows the widget again, in case it has been hidden after it was disabled. All logs owned by a Node automatically get enabled again when a removed Node is restored through an undo operation.

`log_message(msg: str, target: str)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `msg`                 | The message as string. |
| `target`              | `'Global'` or `'Errors'`. Refers to one of the script's default logs. |

`update_shape()`

Causes recompilation of the whole shape of the GUI item of the node.

`create_input(type_: str = 'data', label: str = '', widget_name=None, widget_pos='besides', pos=-1, ...)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `type_`               | `'data'` or `'exec'` |
| `label`               | The input's displayed label string. |
| `widget_name`         | The name the input widget has been registered under. `None` means no widget gets used. |
| `widget_pos`          | `'besides'` or `'below'` the port. |
| `pos`                 | The index this input should be inserted at. `-1` means appending at the end. |

`delete_input(i)`

Deletes the input at index `i`. All existing connections get removed automatically.

`create_output(type_: str = 'data', label: str = '', pos=-1)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `type_`               | `'data'` or `'exec'` |
| `label`               | The output's displayed label string. |
| `pos`                 | The index this output should be inserted at. `-1` means appending at the end. |

`delete_output(o)`

Deletes the output at index `o`. All existing connections get removed automatically.

`session_stylesheet() -> str`

Returns the stylesheet registered via `Session.set_stylesheet()`. This can be useful for custom widgets.

`get_var_val(name: str)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `name`                | script variable's name |

Returns the current value of a script variable and `None` if it couldn't be found.

`set_var_val(name: str, val)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `name`                | script variable's name |
| `val`                 | the variable's value |

Sets the value of a script variable and causes all registered receivers to update (see below).

`register_var_receiver(name: str, method)`

| Parameter             | Description                               |
| --------------------- | ----------------------------------------- |
| `name`                | script variable's name |
| `method`              | a *reference* to the receiver method |

Registers a method as receiver for changes of script variable with given name.



> EXAMPLE
> ``` python
> # connect to variable changes
> # self.var_val_updated refers to the receiver method
> self.register_var_receiver('x', self.var_val_updated)
> self.used_variable_names.append('x')
> ```

`unregister_var_receiver(name: str)`

Unregisters a previously registered variable receiver.

<!-- [Edit this page on GitHub](https://github.com/leon-thomm/ryvencore){: .md-button } -->
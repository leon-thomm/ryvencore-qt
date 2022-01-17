<p align="center">
  <img src="img/logo.png" width="60%"/>
</p>

<h1 align="center"> Welcome to the ryvencore[-qt] documentation </h1>

> [!NOTE]
> All this is in the making and some information and examples might not be 100% up to date. This documentation is generated using [Docsify](https://github.com/docsifyjs/docsify/), so feel free to fork the project and improve it by simply editing the markdown.

The [`ryvencore-qt`](https://github.com/leon-thomm/ryvencore-qt) library provides a Qt frontend for [`ryvencore`](https://github.com/leon-thomm/ryvencore). It can be used to build Python-based cross platform node editors, but so far it mainly serves as base for [Ryven](https://github.com/leon-thomm/ryven) and the development is closely tied to it.

Following are some specifications of the fundamental concepts (regarding both, ryvencore and ryvencore-qt)

# Specifications

# `ryvencore`

## Flows - A Rigorous Definition

A *flow* in this context is a directed, usually but not necessarily acyclic, multigraph whose vertices are *nodes* with edges as *connections* between them.

The fundamental operations to perform on a flow are

- adding a node
- removing a node and all incident connections
- adding a connection between ports (output -> input) of two different nodes
- removing an existing connection

### Flow Modes

### data flows

The default flow mode is *data*. The flow execution here is defined as follows:

By calling `Node.set_output_val(index, val)`, every connection at the output with given index is *activated* with `val` as payload, which leads to an *update event* in the according connected node. No automatic inspection, nor modification is performed on `val`. If there are multiple connections, the order of activation is the order in which they have been added.

### exec flows

> [!NOTE]
> While the *data* mode is the more common use case, you can think of the *exec* mode as UnrealEngine's BluePrints system (*exec*) compared to their material editor (*data*). The *exec* mode implementation might receive some modifications in the future.

For exec connections, by calling `Node.exec_output(index)`, the same process of connection activation takes place, just that there is no `val` payload, it's just an activation signal causing an update in the connected nodes.

The fundamental difference is that in contrast to *data* mode, values residing on data connections is not forward propagated on change, but requested (backwards), meaning a combinational node passively generating some data (like addition of two values at inputs) is not updated when input data changes, but when the output is requested in another connected node via `Node.input(index)`. See the Ryven documentation for an example.

### advanced flow executors

There are some (very experimental) flow executors in the making which make some assumptions about the type of graph (i.e. acyclic), based on that perform some additional graph analysis, to then provide asymptotically more efficient flow execution. Notice that those executors will likely receive major changes in the future.

***

The mode of a flow can be set at any time via `Flow.set_algorithm_mode`, default is `'data'`.

The `inp` parameter in `Node.update_event` represents the input index that received data or an activation signal. If data was requested backwards in exec mode (so an output was called rather than an input), `inp` will be `-1`.

## Nodes System

Nodes are subclasses of the `Node` class. Single node instances/objects are instances of their class, and the basic properties that apply on all those nodes equally are stored as static attributes. Individually changing properties include inputs and outputs (which can be added, removed and modified at any time), display title, actions (see below) etc. You can put any code into your node classes, no limitations, and for sophisticated applications you can override the default behavior by reimplementing methods and by creating node class hierarchies.

### Node Actions

Node actions are a very simple way to define an interface of possible (in most cases state changing) operations for your node. `ryvencore-qt` generates right-click menus for them. The (non-static) `Node.actions` attribute is a dictionary which you can edit like this

```python
# creating a new entry
self.actions['add some input'] = {'method': self.add_some_input_action}


# with a corresponding method
def add_some_input_action(self):
    self.create_input(label='new input', type_='data')


# removing an entry
del self.actions['add some input']

# storing individual data for multiple actions pointing to the same target method
# which enables dynamic, current state dependent actions
self.actions['add some input at index 0'] = {
    'method': self.add_some_input_at,
    'data': 0
}
self.actions['add some input at index 1'] = {
    'method': self.add_some_input_at,
    'data': 1
}


def add_some_input_at(self, index):
    self.create_input(label='inserted input', type_='data')
```

Node actions are saved and reloaded automatically.

> [!WARNING]
> Only refer to your according node's methods in the `method` field, not some other objects'. When saving, the referred method's name is stored and the method field in the `actions` entry is recreated on load via `getattr(node, method_name)`.

## Load & Save

To save a project use `Session.serialize()`. To load a saved project use `Session.load()`. Before loading a project, you need to register all required nodes in the session.

**load & save in nodes**

`ryvencore` provides a dedicated system for loading and saving states of nodes, which is quite important. As nodes are allowed to store anything internally, if your node has states, or some internal data that needs to be restored on load (or paste) you need to define their encoding to make them serializable, i.e. in your `MyNode.get_state() -> dict` method you return a `pickle` serializable dictionary containing all your node's (plain or abstracted) state defining data. In `MyNode.set_state(self, data, version)` you then do the exact opposite. All features provided by ryvencore are stored and saved automatically. The following is important when building complex stateful nodes:

Data input values are saved and restored if and only if the input wasn't connected (and therefore can be seen as the source of some data). Also, once your nodes get a little more complex, you'll want to make use of the `version` parameter in `set_state()` which corresponds to the `version` of the node when the loaded data was saved (this way you can provide backward compatibility to older versions of your node).

It is important to note that nodes which change their state when they receive new inputs are not quite as simple as they might seem, as you need to consider the process of rebuilding a flow that your node is part of. The flow building process works roughly like this:

```
for all saved nodes:
    instantiate node object (__init__())
    initialize node (building ports, loading actions, set_data())
    trigger place_event()
    if GUI:
        build GUI item and widgets
        trigger view_place_event()

for all saved connections:
    n1, n2 = nodes to be connected
    instanciate connection object
    connect according ports 
      causes update in n2 if n2.block_init_updates=False (default)
```

a few important points:

- Your node is instantiated (`__init__()`) and initialized (`set_state()`) *before* any incident connections are built. Therefore, you are free to set your output values, you will not harm any potentially later connected stateful nodes, but input values of originally *connected* inputs will not be available yet.
- When connections are built, the node receives update events when inputs are connected, which also happens during this build process, if the node had connected inputs in the original graph. In case of stateful nodes, you might want to prevent this by setting `self.block_init_updates = True` in the constructor of your node.
- It often makes sense to complete the custom initialization of your node in the `place_event()`.

## Script Variables

Script variables are a nice way to improve the interface to your data. There is a really simple but extremely powerful *registration system* that you can use to register methods as *receivers* on a variable name with a method that gets called every time a script var's value with that name changed. The registration process is part of the API of the `Node` class, so you can easily create highly dynamic nodes.

> EXAMPLE
>
> I made a small *Matrix* node in Ryven where you can just type a few numbers into a small textedit (which is the custom `main_widget` of the node) and it creates a numpy array out of them. But you can also type in the name of a script variable somewhere (instead of a number) which makes the matrix node register as a receiver, so it updates and regenerates the matrix every time the value of a script variable with that name updated.
    
> [!NOTE]
> You could also work with default variables, for example, that you always create when creating a new script, by default, which all your nodes use to communicate or transmit data in more complex ways. This illustrates, there is really a bunch of quite interesting possibilities for sophisticated optimization with this. The system might be expanded in the future.

## Logging

Every *script* has a *logs manager*. The `Node`'s API already includes methods for requesting custom loggers.

<!--
## Convenience Classes

ryvecore already comes with a few convenience classes for widgets. Those convenience classes only use ryvencore's public API, so if you have experience with Qt, you can totally implemenent them yourself. But in most cases they make it much easier to get started. See [convenience GUI section](../conv_gui).
-->

# `ryvencore-qt`

### Custom GUI

You can add custom Qt widgets to your nodes. For instructions on how to register custom widgets in your nodes see Ryven docs.

## Styling

Of course, design splays a huge role when talking about *visual* scripting. Therefore, there's a focus on styling freedom.

### Flow Themes

There is a list of available flow themes (which will hopefully grow). You can choose one via `Session.design.set_flow_theme()`. Currently available flow themes are

- `pure dark`
- `pure light`
- `colorful dark`
- `colorful light`
- `Fusion`
- `Ueli`
- `Blender`
- `Simple`
- `Toy`
- `Tron`

To make sure you can create a look that fits in nicely wherever you might integrate your editor, you can customize the colors for all the above themes using a config json file and passing it to the design using `Session.design.load_from_config(filepath)`. The json file should look like this, for any value you can either write `"default"` or specify a specific setting according to the instructions in the info box.

<details><summary>config file</summary>


You can also specify the initial flow theme, the performance mode (`'pretty'` or `'fast'`) and animations (which currently don't work I think). You can just copy the following json, save it in a file and specify.
```python
{
  "init flow theme": "pure light",
  "init performance mode": "pretty",
  "init animations enabled": true,
  "flow themes": {
    "Toy": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default"
    },
    "Tron": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default"
    },
    "Ghost": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default",

      "nodes color": "default",
      "small nodes color": "default"
    },
    "Blender": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default",

      "nodes color": "default"
    },
    "Simple": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default",

      "nodes background color": "default",
      "small nodes background color": "default"
    },
    "Ueli": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default",

      "nodes background color": "default",
      "small nodes background color": "default"
    },
    "pure dark": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default",

      "extended node background color": "default",
      "small node background color": "default",
      "node title color": "default",
      "port pin pen color": "default"
    },
    "pure light": {
      "exec connection color": "default",
      "exec connection width": "default",
      "exec connection pen style": "default",
      "data connection color": "default",
      "data connection width": "default",
      "data connection pen style": "default",
      "flow background color": "default",

      "extended node background color": "default",
      "small node background color": "default",
      "node title color": "default",
      "port pin pen color": "default"
    }
  }
}
```

</details>

Also note that the syntax of these configurations might receive some changes in the future. Give non-default values for widths in number format, not `str`. Possible values for pen styles are

- `solid line`
- `dash line`
- `dash dot line`
- `dash dot dot line`
- `dot line`

Give colors as string in hex format (also compatible with alpha values like `#aabb4499`).

### StyleSheets

The styling of widgets is pretty much in your hands. 
<!-- You can also store a stylesheet via `Session.design.set_stylesheet()` which is then accessible in custom node widget classes via `self.session.design.global_stylesheet`.  -->
When making a larger editor, you can style the builtin widgets (like the builtin input widgets for nodes) by referencing their class names in your qss.

## Flow View Features

The `FlowView` class, which is a subclass of `QGraphicsView`, supports some special features such as

- stylus support for adding simple handwritten notes
- rendered images of the flow including high-res for presentations

## GUI-less Deployment

You can deploy saved projects (`Session.serialize()`) directly on `ryvencore` without any frontend dependencies. You have full access to the whole `ryvencore` API, so you can even perform all modifications with the expected results. GUI-less deployment is like code generation but better, since you still have API access and `ryvencore` is lightweight.

```python
import json
import ryvencore as rc

if __name__ == '__main__':

    with open('path/to/your/project_file', 'r') as f:
        project_str = f.read()

    project_dict = json.loads(project_str)

    # creating session and loading the contents
    session = rc.Session()
    session.register_nodes([ <your_used_nodes_here> ])
    scripts = session.load(project_dict)

    # now you have manual access like this...
    myscript = scripts[0]
    myflow = script.flow

    node1, node2, node3 = flow.nodes
    node1.update()
    ...
```

Of course, your nodes are not allowed to access `ryvencore-qt` API, as this API does not exist when running it on the backend, since there is no frontend then. To make your nodes compatible with this, you can check the boolean `Session.gui` attribute to determine whether the session is aware of a frontend or not.

``` python
def update_event(self, inp=-1):
    # ...
    if self.session.gui:
        self.main_widget().update()
    # ...
    
```

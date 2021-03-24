# Features

## Flows - A Rigurous Definition

A *flow* is like a directed multigraph (not necessarily acyclic) whose vertices are *nodes* with *connections* as edges to other nodes.

The fundamental actions that can be performed on a flow are

- adding a node
- removing a node and all incident connections
- adding a connection between ports of two different nodes
- removing an existing connection

Standard flow execution (for data flows) is defined as follows:

By calling `Node.set_output_val(index, val)`, every outgoing connection is *activated*, with `val` as payload, which leads to an *update event* in every connected node. No automatic modification is performed on `val`. If there are multiple connections, the order of activation is the order in which they have been added.

***

### exec flows
There are two types of connections, namely *data* and *exec*, and hence two types of node ports. Usually you will want to only use data connections and ports (-> *data flows*). For execution connections, by calling `Node.exec_output(index)`, the same happens as for data propagation described above, just that there is no `val` payload.

***

In both cases does the `input_called` parameter in `Node.update_event` represent the input index that received data, or a signal from an activated connection.

The mode of a flow (*data* or *exec*) can be set at any time using `Flow.set_algorithm_mode`, default is *data*.

## Nodes System

Nodes are subclasses of the `Node` class. Single node instances are instances of their class, and the basic properties that apply on all those nodes equally are stored as static attributes. Individually changing properties are inputs and outputs (which can be added, removed and modified at any time), display title, actions (see below) etc. You can put any code into your node classes, no limitations, and for sophisticated use you can override the default behavior by reimplementing methods.

<!--
One very important feature is the possibility of defining custom GUI components, i.e. widgets, for your nodes. A node can have a `main_widget` and input widgets, whose classes are stored in the `input_widget_classes` attribute.
-->

### Special Actions

Special actions are a very simple way to define right click operations for your nodes. The non-static `Node.special_actions` attribute is a dictionary which you can edit like this

```python
# creating a new entry
self.special_actions['add some input'] = {'method': self.add_some_input_action}

# with a corresponding method
def add_some_input_action(self):
    self.create_input(type_='data', label='new input')

# removing an entry
del self.special_actions['add some input']

# and storing individual data for multiple actions pointing to the same target method
# which enables dynamic, current state dependent actions
self.special_actions['add some input at index 0'] = {
    'method': self.add_some_input_at,
    'data': 0
}
self.special_actions['add some input at index 1'] = {
    'method': self.add_some_input_at,
    'data': 1
}
def add_some_input_at(self, index):
    self.create_input(type_='data', label='inserted input', pos=index)
```

Special actions are saved and reloaded automatically.

## Load&Save

To save a project, simply use `Session.serialize()`, to load a saved project use `Session.load()`. Before loading a project, you need to register all required nodes in the session.

## Script Variables

Script variables are a nice way to improve the interface to your data. There is a really simple but extremely powerful *registration system* that you can use to register methods as *receivers* for a variable with a given name. Then, every time the variable's value gets updated, all registered receiver methods are called. The registration process is part of the API of the `Node` class, so you can easily create highly responsive nodes.

!!! example
    I made a small *Matrix* node in Ryven where you can just type a few numbers into a small textedit (which is the custom `main_widget` of the node) and it creates a numpy array out of them. But you can also type in the name of a script variable somewhere (instead of a number) which makes the matrix node register as a receiver, so it updates and regenerates the matrix every time the value of a script variable with that name updated.
    
!!! note
    You could also work with default variables, for example, that you always create when creating a new script, by default, which all your nodes use to communicate or transmit data in more complex ways. This illustrates, there is really a bunch of quite interesting possibilities for sophisticated optimization with this. The system might be expanded in the future.

## Logging

There is a `Logger` class which every script has an instance of. You can use the logger's [API](../api/#class-logger) to write messages to default logs and to request custom logs and write directly to them. The `Node`'s API already includes methods for requesting custom logs and manages *enable*-and *disable*-events according to actions in the flow (like removing the Node), but you can also request logs for anything else.

<!--
## Convenience Classes

ryvecore already comes with a few convenience classes for widgets. Those convenience classes only use ryvencore's public API, so if you have experience with Qt, you can totally implemenent them yourself. But in most cases they make it much easier to get started. See [convenience GUI section](../conv_gui).
-->

## Styling

Of course, design splays a huge role when thinking about *visual* scripting. Therefore, you have wide freedom in styling.

### Flow Themes

There is a list of available flow themes (which I want to expand as far as possible). You can choose one via `Session.design.set_flow_theme()`. Currently available flow themes are `Samuel 1d`, `Samuel 1l`, `Samuel 2d`, `Samuel 2l`, `Ueli`, `Blender`, `Simple`, `Toy` and `Tron`. To make sure you can create a look that fits in nicely wherever you might integrate your editor, you can customize the colors for all the above themes using a config json file and passing it to the design using `Sessiong.design.load_from_config(filepath)`. The json file should look like this, for any value you can either write "default" or specify a specific setting according to the instructions in the info box.

??? note "config file"
    You can also specify the initial flow theme, the performance mode (`'pretty'` or `'fast'`) and animations (which currently don't work I think). You can just copy the following json, save it in a file and specify.
    ```python
    {
      "init flow theme": "Samuel 1l",
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
        "Samuel 1d": {
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
        "Samuel 1l": {
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
    Also note that the syntax of these configurations might receive some changes in the future. Give non-default values for widths in number format, not `str`. Possible values for pen styles are `solid line`, `dash line`, `dash dot line`, `dash dot dot line` and `dot line`. Give color as string in hex format (also compatible with alpha values like `#aabb4499`).

### StyleSheets

The styling of widgets is pretty much in your hands. You can also store a stylesheet via `Session.design.set_stylesheet()` which is then accessible in custom node widget classes via `self.session.design.global_stylesheet`. When making a larger editor, you can style the builtin widgets (like the builtin input widgets for nodes) by referencing their class names in your qss.

## Customizing Connections

You can provide your own reimplementations of the connection classes, since this is an excellent point to add domain-specific additional functionality to your editor (like 'edge weights' for example). There are no detailed instructions on that in the docs yet, but you can take a look at the implementations, and then pass your implementations of the classes you want to enhance to the `Session`'s constructor, see [API](../api/#class-session).

## Flow View Features

The `FlowView` class, which is a subclass of `QGraphicsView`, supports some special features such as

- stylus support for adding simple handwritten notes
- rendered images of the flow including high res for presentations
<!-- - algorithm modes for the flow (data and exec) -->
<!-- - touch events (needs improvement) -->
<!-- - viewport update modes -->

<!--
!!! bug "Bug (help pls)"
    After pasting drawings in the scene, when undoing (ctrl+z), it doesn't work and this seems so point to a bigger issue, which I described in the issues section on GitHub. I'm a bit lost about this, so please take a look if you think you could help with solving this.
-->

<!--
### Algorithm Mode

Most flow-based visual scripting editors either support data flows or exec flows. In ryvencore I wanted to enable both, so there are two modes for that. A structure like the flow-based paradigm has most potential for pure data flows, I guess. But exec flows can be really useful too, as can be seen in UnrealEngine's blueprint editor for example.

The technical differences only regard connections. In a data flow, you only have data connections, in an exec flow you can have both. In data flows any change of data (which is setting the value of a *data-output-port* of a NodeInstance) is *forward propagated* and leads to update events in all connected node instances. In an exec flow, contrary to exec connections (which just trigger NodeInstances to update, see `input_called` in `NodeInstance.update_event()`), data is not forward propagated, but requested, *backwards*. Meaning that the API call `NodeInstance.input(i)` calls the connected *output* and requests the data which causes *passive NodeInstances* (those without exec ports) to update/recompute completely.  That's the technical version... Usually, one just wants data flows. -->

<!-- ### Viewport Update Mode

There are two *viewport update modes*, `'sync'` and `'async'`. The only difference is that in `sync` mode, any update event that propagates through the flow is finished before the viewport is updated. `async` mode can sometimes be useful for larget data flows, in `async` mode, the flow first updates the scene rectangle of the *main-widgets* of NodeInstances before passing the update event to the next connected NodeInstance (so you can see your flow procedurally execute). -->

## Threading

The internal communication between backend and frontend is done in a somewhat thread-safe way. This means, you can initialize the `Session` object in a separate thread, and provide a GUI parent for the flow view, which will then be initialized in this GUI component's thread. This generally speeds up the backend and makes sure it's not significantly affected by performance fluctuations of the frontend. Further parallelization of the tasks that your individual nodes perform is up to you.

!!! note
    Be careful with calling `Session.serialize()` from different threads simultaneously, as the serialization of the FlowView is currently "joined" with the session's thread by setting an attribute (see `Session.serialize()` implementation).

## GUI-less Deployment

When you saved a project in your editor (via `Session.serialize()`), you can reload it using ryvencore (the backend) manually to deploy your flows anywhere. You have full access to the whole ryvencore API, so you can even perform modifications with the expected results. So, GUI-less deployment is like code generation but better, since you still have API access.

```python
if __name__ == '__main__':

    with open('path/to/your/project_file', 'r') as f:
        project_str = f.read()

    project_dict = json.loads(project_str)

    # creating session and loading the contents
    session = Session(no_gui=True)
    session.register_nodes([ <your_used_nodes_here> ])
    function_scripts, scripts = session.load(project_dict)

    # now you have manual access like this...
    myscript = scripts[0]
    myflow = script.flow

    node1, node2, node3 = flow.nodes
    node1.update()
```

Which of the API calls you use in ryvencore-qt are from ryvencore is indicated in the API reference. Of course, your nodes are not allowed to access ryvencore-qt API, as this API does not exist when running it on the backend, since there is no frontend then. To make your nodes compatible with this, you can check the `Session.no_gui` attribute to determine whether the session is having a frontend or not.

``` python
def update_event(self, input_called=-1):

    # doing some work
    
    if not self.session.no_gui:
        self.main_widget().update()
    
    # setting some outputs
```

Currently, when running it in GUI mode, ryvencore uses Qt signals so the frontend is notified when events like placement of a node in a flow happen. When running ryvencore without frontend, these signals do nothing, so there is no Qt dependency then. This dualism is planned to get replaced in the future by something more scalable, possibly a brokerless message queue to easily enable network scaling.

<!--
## Code Generation [idea]

Now, there currently isn't a code generation mechanism for ryvencore, however I already implemented a prototype for Ryven once and Ryven 3 will probably receive this as an official feature at some point. I think the requirements for something like this only regard the file structure of your node definitions. If you are coming from Ryven and want to contribute to the development, this would be something that I'm sure some people using the software are much more capable of implementing than I am. On the dev branch in the Ryven repo you can find the basic idea that I followed for creating the source code implemented, there are just still a few (quite solvable) issues regarding the recursive module imports.

Continuing is some thoughts for people who want to work on this:

!!! note
    **Files might get large!** Because the resulting code has to include implementations of the basic abstract components (ideally just the ryvencore classes) as well as the definitions of all used nodes, the resulting code might quickly reach 1000 lines.

The resulting code should be completely independent without Qt dependencies. When generating the code, Ryven runs a dependency analysis of all nodes' sources. Some nodes might just use standard packages and modules (like numpy), while others might include external sources that one wants to have included in the generated code, like some functions or classes used by many of your nodes which are therefore kept in their own modules. Ryven analyzes normal (module-wide) import statements recursively and includes all sources that are not builtin modules or installed packages or part of an ignore list.

-->
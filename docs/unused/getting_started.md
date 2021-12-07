# Getting Started

## Installation

```
pip install ryvencore-qt
```

or from sources

```
git clone https://github.com/leon-thomm/ryvencore-qt
cd ryvencore-qt
python setup.py install
```

## First Editor

> [!NOTE]
> You can copy the full example code at the bottom of this page.
   
Let's build our first editor. First thing is importing the library

``` python
import ryvencore_qt as rc
```

### Overall Structure

Your main interface to the current project is the **Session**, which basically represents a project. We can leave everything as default for now.

``` python
my_session = rc.Session()
```

Now let's create a flow, which is part of a **Script**. Scripts are managed by the session and contain the **flow**, **script variables** and **logs**.

``` python
script = my_session.create_script('hello world', flow_view_size=[800, 500])
```

With the `flow_view_size` you can set the pixel size of the flow view that will be created. You can access the view via `my_session.flow_views[script]`. The flow view itself is a `QGraphicsView` subclass, which is a GUI class of Qt.

### Setting Up a Window

This is not a tutorial on getting started with Qt for Python, but setting up a basic GUI structure is quite simple.

``` python
import ryvencore-qt as rc
import sys
from PySide2.QtWidgets import QMainWindow, QApplication

if __name__ == "__main__":

    # create a QApplication and a MainWindow
    # the QMainWindow will be subclassed later
    app = QApplication()
    mw = QMainWindow()

    # creating the session
    session = rc.Session()
    session.design.set_flow_theme(name='pure light')

    # registering the nodes
    session.register_nodes([PrintNode, RandNode])

    # creating a script with a flow
    script = session.create_script('hello world', flow_view_size=[800, 500])

    # and setting the flow widget as the windows central widget
    mw.setCentralWidget(session.flow_views[script])

    mw.show()
    sys.exit(app.exec_())
```

And there we go, that's it. You can left click into the scene to see a node selection widget pop up. Well, there isn't any content yet to use, so let's add that.

### Nodes

> [!NOTE]
> Nodes (their classes) are defined the same way as in Ryven, so I won't go too much into the details here.

In `ryvencore` the nodes system works like this:

A node's blueprint is defined by its class, making heavy use of Pythons static attributes system. As the accessible nodes are managed by the session, you need to register the *classes* of the nodes you want to use like this:

``` python
session.register_nodes( list_of_nodes )
```

> [!NOTE]
> You can put any code into your Node subclass, no limits! You can define additional classes, use external packages, basically everything you can do in a python class.

> [!TIP]
> You can register (and unregister) nodes at any time! This enables dynamic import mechanisms as implemented in Ryven for example.

Let's define a simple node. For a detailed description of the members, take a look into the [API reference](/api#class-node). We'll just create a very simple print node, which prints data from an input every time it receives some.

``` python
class PrintNode(rc.Node):
    """Prints your data"""

    # all basic properties
    title = 'Print'
    init_inputs = [
        rc.NodeInputBP()
    ]
    color = '#A9D5EF'
    # see API doc for a full list of all properties

    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):
        data = self.input(0)  # get data from the first input
        print(data)
```

Make your class derive from `rc.Node` and then enhance it the way you like. The `update_event` is the important part, it gets triggered every time the node is updated.

> [!NOTE]
> While most flow-based visual scripting software out there implements either the approach of *execution-flows* or *data-flows*, `ryvencore` implements them both. Generally, data flows are more flexible and powerful, so the focus is on them, but there are cases where exec flows make more sense, so I wanted to leave it as an option.

> [!TIP|label:Custom Node Base Class]
> In more sophisticated editors, you may want to define your custom `NodeBase` class to add functionality to all your nodes. If you want ryvencore-internal nodes (like macro nodes) to be children of this class too, you can provide your base class when initializing the `Session` object.

And let's add another node which generates a random number in a given range, so we have something to print.

``` python
from random import random

class RandNode(rc.Node):
    """Generates random float"""
    
    title = 'Rand'
    init_inputs = [
        rc.NodeInputBP(dtype=rc.dtypes.Integer(default=1, bounds=(1, 100)))
    ]
    init_outputs = [
        rc.NodeOutputBP())
    ]
    color = '#fcba03'

    def update_event(self, inp=-1):
        # random float between 0 and value at input
        val = random()*self.input(0)

        # setting the value of the first output
        self.set_output_val(0, val)
```

Notice, instead of a `dtype`, we could also provide a more sophisticated custom widget via `NodeInputBP(add_config={'widget name': 'some_registered_widget', 'widget pos': 'besides'})` which is explained below.

#### Input Widgets

Data inputs can have widgets, more specifically a *QWidget* (which is a GUI class of Qt) or any subclass. Custom input widget classes can be registered for a node by listing them in the Node's static field `input_widget_classes` (see [API](/api#class-node)). However, `ryvencore-qt` also provides a few built-in convenience widgets that are automatically added when using `dtypes`.

### Finishing

Now you can run this and if everything works fine you already have a small editor with all major features. You can place the two nodes, connect them by mouse, type something into the random node's input field and hit enter to trigger the update. This will cause the `self.set_output_val(...)` call which triggers the connected print node to update and print.

Of course there is much more you can do. For example you can change the flow theme.

``` python
session.design.set_flow_theme(name='pure light')
```

There are a few different themes and you can configure the their colors using a json config file, so you'll definitely be able to give your flows a look that fits in the application environment it's going to be a part of. 

You can also change the performance mode to *fast* which results in some less pretty simplifications in rendering.

``` python
session.design.set_performance_mode('fast')
```

<details><summary>CODE</summary>


``` python
import ryvencore_qt as rc
import sys
from PySide2.QtWidgets import QMainWindow, QApplication
from random import random


class PrintNode(rc.Node):
    """Prints your data"""

    # all basic properties
    title = 'Print'
    init_inputs = [
        rc.NodeInputBP()
    ]
    color = '#A9D5EF'
    # see API doc for a full list of all properties

    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):
        data = self.input(0)  # get data from the first input
        print(data)


class RandNode(rc.Node):
    """Generates random float"""
    
    title = 'Rand'
    init_inputs = [
        rc.NodeInputBP(dtype=rc.dtypes.Integer(default=1, bounds=(1, 100)))
    ]
    init_outputs = [
        rc.NodeOutputBP())
    ]
    color = '#fcba03'

    def update_event(self, inp=-1):
        # random float between 0 and value at input
        val = random()*self.input(0)

        # setting the value of the first output
        self.set_output_val(0, val)


if __name__ == "__main__":

    # create a QApplication and a MainWindow
    # the QMainWindow will be subclassed later
    app = QApplication()
    mw = QMainWindow()

    # creating the session
    session = rc.Session()
    session.design.set_flow_theme(name='pure light')

    # registering the nodes
    session.register_nodes([PrintNode, RandNode])

    # creating a script with a flow
    script = session.create_script('hello world', flow_view_size=[800, 500])

    # and setting the flow widget as the windows central widget
    mw.setCentralWidget(session.flow_views[script])

    mw.show()
    sys.exit(app.exec_())
```


</details>
   

## Second Editor

Here I will just throw at you the commented code for another editor that demonstrates how slightly larger `ryvencore-qt` editors might generally be structured. It was a first prototype I made for a software to simulate flows of logic gates.


<details><summary>CODE</summary>


`main.py`
``` python
import ryvencore_qt as rc
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget

# nodes.py is defined below
from nodes import SignalNode, ANDGateNode, ORGateNode, NANDGateNode, NORGateNode, NOTGateNode, XORGateNode, LEDNode, \
    NodeBase


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # if I wanted to make all ryvencore-internally defined nodes 
        # (like macro nodes) also inherit from our NodeBase, I'd provide 
        # it as node_class parameter here, but I don't need it here
        self.session = rc.Session()

        # some design specs
        self.session.design.set_flow_theme(name='pure light')
        self.session.design.set_performance_mode('pretty')

        # registering the nodes
        self.session.register_nodes(
            [
                SignalNode,
                ANDGateNode,
                ORGateNode,
                NANDGateNode,
                NORGateNode,
                NOTGateNode,
                XORGateNode,
                LEDNode,
            ]
        )
        self.script = self.session.create_script(title='main')
        view = self.session.flow_views[self.script]

        # creating a widget and adding the flow view of the script
        w = QWidget()
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(view)

        self.setCentralWidget(w)
        self.resize(1500, 800)  # resizing the window


if __name__ == '__main__':
    app = QApplication()

    mw = MainWindow()
    mw.show()

    sys.exit(app.exec_())
```
`nodes.py`
``` python
import ryvencore_qt as rc

# some Qt imports...
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QCheckBox, QPushButton


class NodeBase(rc.Node):
    """Base class for the nodes in this application"""

    style = 'small'
    color = '#cc7777'


class SignalNode_MainWidget(rc.MWB, QCheckBox):
    """Custom MainWidget for the signal node, just a simple check box for now.
    Note that QCheckBox is a QWidget. Also note that we must also derive rc.MWB,
    the MainWidgetBase of ryvencore_qt."""

    def __init__(self, params):
        rc.MWB.__init__(self, params)
        QCheckBox.__init__(self)

        self.stateChanged.connect(self.node.update_signal)

    def get_state(self) -> dict:
        # saving the checked state
        return {
            'checked': self.checkState()
        }

    def set_state(self, data: dict):
        # reloading the checked state
        self.setChecked(data['checked'])


class SignalNode(NodeBase):
    """A node for generating high or low voltage signals."""

    title = 'signal'
    description = 'creates a signal, 1 or 0'
    init_inputs = []
    init_outputs = [
        rc.NodeOutputBP('data')
    ]
    main_widget_class = SignalNode_MainWidget
    main_widget_pos = 'between ports'  # alternatively 'below ports'
    style = 'extended'

    def __init__(self, params):
        super().__init__(params)
        self.signal_high = False

    def update_signal(self, state):
        self.signal_high = True if state == Qt.Checked else False
        self.update()

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.signal_high))
        # note that 1 and 0 can be interpreted as True and False
        # by all the logical operators that these nodes use

    def get_state(self) -> dict:
        # saving signal state
        return {
            'signal high': self.signal_high
        }

    def set_state(self, data):
        # reloading signal state
        self.signal_high = data['signal high']


class ANDGateNode(NodeBase):
    title = 'AND'
    description = '1 <=> both inputs are 1'
    init_inputs = [
        rc.NodeInputBP('data'),
        rc.NodeInputBP('data'),
    ]
    init_outputs = [
        rc.NodeOutputBP('data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.input(0) and self.input(1)))


class ORGateNode(NodeBase):
    title = 'OR'
    description = '1 <=> at least one input is 1'
    init_inputs = [
        rc.NodeInputBP('data'),
        rc.NodeInputBP('data'),
    ]
    init_outputs = [
        rc.NodeOutputBP('data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.input(0) or self.input(1)))


class XORGateNode(NodeBase):
    title = 'XOR'
    description = '1 <=> odd number of inputs is 1'
    init_inputs = [
        rc.NodeInputBP('data'),
        rc.NodeInputBP('data'),
    ]
    init_outputs = [
        rc.NodeOutputBP('data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.input(0) != self.input(1)))


class NOTGateNode(NodeBase):
    title = 'NOT'
    description = 'negates the signal'
    init_inputs = [
        rc.NodeInputBP('data'),
    ]
    init_outputs = [
        rc.NodeOutputBP('data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(not self.input(0)))


class NANDGateNode(NodeBase):
    title = 'NAND'
    description = 'NOT AND'
    init_inputs = [
        rc.NodeInputBP('data'),
        rc.NodeInputBP('data'),
    ]
    init_outputs = [
        rc.NodeOutputBP('data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(not (self.input(0) and self.input(1))))


class NORGateNode(NodeBase):
    title = 'NOR'
    description = 'NOT OR'
    init_inputs = [
        rc.NodeInputBP('data'),
        rc.NodeInputBP('data'),
    ]
    init_outputs = [
        rc.NodeOutputBP('data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(not (self.input(0) or self.input(1))))


class LED_MainWidget(rc.MWB, QPushButton):
    """LED widget for the LED node, for now just a simple disabled button"""

    def __init__(self, params):
        rc.MWB.__init__(self, params)
        QPushButton.__init__(self)

        self.setEnabled(False)
        self.setFixedSize(70, 50)
        self.setStyleSheet(self.gen_style_sheet(False))

    def gen_style_sheet(self, high_potential: bool):
        # generate stylesheet with red or transparent background

        return f'''
QPushButton {{
    border: 1px solid transparent;
    background: {('red' if high_potential else 'transparent')};
}}'''

    def potential_updated(self, high_potential: bool):
        # called from self.node
        self.setStyleSheet(self.gen_style_sheet(high_potential))


class LEDNode(NodeBase):
    title = 'LED'
    description = 'shows red if signal is 1, black if it is 0'
    init_inputs = [
        rc.NodeInputBP('data')
    ]
    init_outputs = []
    main_widget_class = LED_MainWidget
    main_widget_pos = 'between ports'

    def update_event(self, inp=-1):
        # note that such unchecked calls to GUI components are not allowed in nodes 
        # that are intended to run on ryvencore without GUI. But because this isn't
        # really a use case here, we can keep it simple for now
        mw = self.main_widget()
        mw.potential_updated(bool(self.input(0)))

```


</details>

And now we have a basic little editor to play around with logic gates, yay!
![](../img/logic_editor_screenshot1.png)
![](../img/logic_editor_screenshot2.png)
![](../img/logic_editor_screenshot3.png) 
The actual editor I made for this is a bit more sophisticated and pretty, and might get its own repository soon.

> [!TIP|label:Done]
> `ryvencore-qt` has much more features than I showed here, and there are lots of things that might be added in the future. See the [Features](/features) section where you will find more detailed descriptions of all the internal systems, from save&load over stylus-and touch-support to execution flows. The world is yours, have fun!

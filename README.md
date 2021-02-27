rvencore is a framework for building flow-based visual scripting editors for Python. It comes from the Ryven project and will be the foundation for future Ryven versions amongst other editors. ryvencore lets you create Ryven-like editors which you then can optimize for specific domains. It provides a backend structure that enables a range of useful features and the GUI for the flows.

### Installation

```
pip install ryvencore
```

### Features

- **load & save**
- **variables system** with registration mechanism to build nodes that automatically adapt to change of data
- **built in logging**
- **simple nodes system** (see Usage below)
- **dynamic nodes registration mechanism** to register and unregister nodes at runtime
- **function nodes/subgraphs**
- **right click operations system for nodes**
- **you can add any Qt widgets to your nodes** (hence you could also embed your Python-Qt applications with GUI)
- **convenience GUI classes**
- **many different modifiable themes**
- **data *and* exec flow support**
- **stylus support for adding handwritten notes**
- **rendering flow images**
- **THREADING READY** [extremely experimental though]

Threading ready means that all internal communication between the abstract components and the GUI of the flows is implemented in a somewhat thread save way, so, while still providing an intuitive API, ryvencore is compatible with applications that keep their abstract components in a separate thread. While this is currently a very experimental feature whose implementation will experience improvement in the future, all the foundation is there and successful tests have been made. A lot of work went into this and I think it's of crucial importance as this opens the door to the world of realtime data processing.

### Usage

Following is a short example for a simple editor with a random number generator node and a print node. The example can also be found in the docs linked below.

``` python
import sys
from random import random
import ryvencore as rc
from PySide2.QtWidgets import QMainWindow, QApplication


class PrintNode(rc.Node):

    # all basic properties
    title = 'Print'
    description = 'prints your data'
    # there is also description_html
    init_inputs = [
        rc.NodeInput('data')
    ]
    init_outputs = []
    color = '#A9D5EF'
    # see API doc for a full list of all properties

    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(params)

    def update_event(self, input_called=-1):
        data = self.input(0)  # get data from the first input
        print(data)


class RandNode(rc.Node):
    
    title = 'Rand'
    description = 'generates random float'
    init_inputs = [
        rc.NodeInput('data', widget='std line edit', widget_pos='besides')
    ]
    init_outputs = [
        rc.NodeOutput('data')
    ]
    color = '#fcba03'

    def update_event(self, input_called=-1):
        # random float between 0 and value at input
        val = random()*self.input(0)

        # setting the value of the first output
        self.set_output_val(0, val)


if __name__ == "__main__":

    # creating the application and a window
    app = QApplication()
    mw = QMainWindow()

    # creating the session, registering, creating script
    session = rc.Session(flow_theme_name='Samuel 1l')
    session.register_nodes([PrintNode, RandNode])
    script = session.create_script('hello world', flow_view_size=[800, 500])

    # and setting the flow widget as the windows central widget
    mw.setCentralWidget(script.flow_view)

    mw.show()
    sys.exit(app.exec_())
```

I am excited about this, biggest room for improvement currently regards convenience GUI classes and touch support. For a more detailed overview visit the [docs page](https://leon-thomm.github.io/ryvencore/).

### Future

#### Qt Dependency

ryvencore could probably easily be modified to run without any GUI (it probably only needs a simple dummy `FlowView` class for `Script`). However, all the abstract internal components are QObjects to use Qt's signals and slots system, which is really nice when embedding a ryvencore editor into another Qt application. However, it means that the abstract components are not Qt independent. And it might make much more sense to soon introduce another system for simple communication that does not depend on Qt.

#### Code Generation

I already made a working code generation prototype for Ryven 2. For Ryven 3 I made a new one, which currently has a (quite solvable) issue in the recursive module import when loading modules that are part of the current package (see this). For ryvencore, it might be possible to add the code generation algorithm for use under a few conditions regarding the file structure of the nodes that are used. In the end this, however, will probably also depend on how the *Qt Dependency* thing described above will evolve.

### Contributing

Contributions are very welcome. Due to my study, I myself will not have the time to work on this a lot during the next months. I did my best to create an internal structure that is a good foundation for further development.

For discussing general ideas, notice there is a *Discussions* area.

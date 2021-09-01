import sys
import os
from random import random

os.environ['QT_API'] = 'pyside2'  # tells qtpy to use PyQt5
import ryvencore_qt as rc
from qtpy.QtWidgets import QMainWindow, QApplication


class PrintNode(rc.Node):
    """Prints your data"""

    # all basic properties
    title = 'Print'
    init_inputs = [
        rc.NodeInputBP()
    ]
    init_outputs = []
    color = '#A9D5EF'

    # see API doc for a full list of properties

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
        rc.NodeInputBP(dtype=rc.dtypes.Data(default=1))
    ]
    init_outputs = [
        rc.NodeOutputBP()
    ]
    color = '#fcba03'

    def update_event(self, inp=-1):
        # random float between 0 and value at input
        val = random() * self.input(0)

        # setting the value of the first output
        self.set_output_val(0, val)


if __name__ == "__main__":

    # creating the application and a window
    app = QApplication()
    mw = QMainWindow()

    # creating the session, registering, creating script
    session = rc.Session()
    session.design.set_flow_theme(name='pure light')
    session.register_nodes([PrintNode, RandNode])
    script = session.create_script('hello world', flow_view_size=[800, 500])

    mw.setCentralWidget(session.flow_views[script])

    mw.show()
    sys.exit(app.exec_())
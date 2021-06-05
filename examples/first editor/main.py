import ryvencore_qt as rc
import sys
from PySide2.QtWidgets import QMainWindow, QApplication
from random import random


class PrintNode(rc.Node):

    """prints your data"""
    # all basic properties
    title = 'Print'
    # there is also description_html
    init_inputs = [
        rc.NodeInputBP(type_='data')
    ]
    init_outputs = []
    color = '#A9D5EF'
    # see API doc for a full list of all properties

    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(params)

    def update_event(self, inp=-1):
        data = self.input(0)  # get data from the first input
        print(data)


class RandNode(rc.Node):
    """generates random float"""

    title = 'Rand'
    init_inputs = [
        rc.NodeInputBP('', 'data', {'widget name': 'std line edit', 'widget pos': 'besides'})
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data')
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

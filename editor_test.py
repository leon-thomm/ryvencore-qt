import json
import sys
import os
from random import random

os.environ['QT_API'] = 'pyside2'  # tells qtpy to use PyQt5
import ryvencore_qt as rc
from qtpy.QtWidgets import QMainWindow, QApplication

example_project = {'macro scripts': [],
 'scripts': [{'title': 'hello world',
   'variables': {},
   'flow': {'algorithm mode': 'data',
    'nodes': [{'identifier': 'PrintNode',
      'state data': 'gAR9lC4=',
      'inputs': [{'type': 'data', 'label': '', 'GID': 6, 'has widget': False}],
      'outputs': [],
      'special actions': {},
      'display title': 'Print',
      'GID': 5,
      'pos x': 513.0,
      'pos y': 277.0,
      'unconnected ports hidden': False,
      'collapsed': False},
     {'identifier': 'RandNode',
      'state data': 'gAR9lC4=',
      'inputs': [{'type': 'data',
        'label': '',
        'GID': 8,
        'val': 'gARLKi4=',
        'dtype': 'DType.Data',
        'dtype state': 'gASVLwAAAAAAAAB9lCiMB2RlZmF1bHSUSwGMA2RvY5SMAJSMBmJvdW5kc5ROjARzaXpllIwBbZR1Lg==',
        'has widget': True,
        'widget data': 'gASVEAAAAAAAAAB9lIwEdGV4dJSMAjQylHMu'}],
      'outputs': [{'type': 'data', 'label': '', 'GID': 9}],
      'special actions': {},
      'display title': 'Rand',
      'GID': 7,
      'pos x': 238.0,
      'pos y': 134.0,
      'unconnected ports hidden': False,
      'collapsed': False}],
    'connections': [{'GID': 10,
      'parent node index': 1,
      'output port index': 0,
      'connected node': 0,
      'connected input port index': 0}],
    'GID': 4,
    'flow view': {'drawings': [], 'view size': [800.0, 500.0]}},
   'GID': 1}]}



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
    session.design.set_flow_theme(name='Fusion')
    session.register_nodes([PrintNode, RandNode])
    session.load(example_project)
    script = session.create_script('hello world', flow_view_size=[8000, 5000])
    # script = session.scripts[0]

    mw.setCentralWidget(session.flow_views[script])

    mw.show()
    sys.exit(app.exec_())

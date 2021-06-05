import ryvencore_qt as rc

# some Qt imports...
from PySide2.QtCore import Qt
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
    doc = 'creates a signal, 1 or 0'
    init_inputs = []
    init_outputs = [
        rc.NodeOutputBP(type_='data')
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
    doc = '1 <=> both inputs are 1'
    init_inputs = [
        rc.NodeInputBP(type_='data'),
        rc.NodeInputBP(type_='data'),
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.input(0) and self.input(1)))


class ORGateNode(NodeBase):
    title = 'OR'
    doc = '1 <=> at least one input is 1'
    init_inputs = [
        rc.NodeInputBP(type_='data'),
        rc.NodeInputBP(type_='data'),
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.input(0) or self.input(1)))


class XORGateNode(NodeBase):
    title = 'XOR'
    doc = '1 <=> odd number of inputs is 1'
    init_inputs = [
        rc.NodeInputBP(type_='data'),
        rc.NodeInputBP(type_='data'),
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(self.input(0) != self.input(1)))


class NOTGateNode(NodeBase):
    title = 'NOT'
    doc = 'negates the signal'
    init_inputs = [
        rc.NodeInputBP(type_='data'),
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(not self.input(0)))


class NANDGateNode(NodeBase):
    title = 'NAND'
    doc = 'NOT AND'
    init_inputs = [
        rc.NodeInputBP(type_='data'),
        rc.NodeInputBP(type_='data'),
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data'),
    ]

    def update_event(self, inp=-1):
        self.set_output_val(0, int(not (self.input(0) and self.input(1))))


class NORGateNode(NodeBase):
    title = 'NOR'
    doc = 'NOT OR'
    init_inputs = [
        rc.NodeInputBP(type_='data'),
        rc.NodeInputBP(type_='data'),
    ]
    init_outputs = [
        rc.NodeOutputBP(type_='data'),
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
    doc = 'shows red if signal is 1, black if it is 0'
    init_inputs = [
        rc.NodeInputBP(type_='data')
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

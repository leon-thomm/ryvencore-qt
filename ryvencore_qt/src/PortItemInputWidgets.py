from qtpy.QtCore import Signal
from qtpy.QtGui import QFontMetrics
from qtpy.QtWidgets import QSpinBox, QLineEdit


from .WidgetBaseClasses import IWB
from .retain import M


class RCIW_BUILTIN_SpinBox(QSpinBox, IWB):
    """Convenience class for using a spin box widget as data input for nodes."""

    trigger_update = Signal(int)

    def __init__(self, params):
        QSpinBox.__init__(self)
        IWB.__init__(self, params)

        self.trigger_update.connect(self.node.update)

        self.port_local_pos = None

        self.setFixedWidth(50)
        self.setFixedHeight(25)
        self.setMaximum(1000000)
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        self.trigger_update.emit(self.node.inputs.index(self.input))

    def remove_event(self):
        pass

    def get_val(self):
        return self.value()

    def get_data(self) -> dict:
        return {'val': self.value()}

    def set_data(self, data):
        if type(data) == dict:
            self.setValue(data['val'])
        else:  # backwards compatibility
            self.setValue(data)


class RCIW_BUILTIN_LineEdit(QLineEdit, IWB):
    """Convenience class for using input fields (i.e. QLineEdits) as widgets for data inputs of nodes."""

    trigger_update = Signal(object)

    def __init__(self, params, size='medium', resize=False):
        IWB.__init__(self, params)
        QLineEdit.__init__(self)

        self.trigger_update.connect(self.input.update)

        self.port_local_pos = None
        self.resizing = resize

        if size == 'small':
            self.base_width = 30
        elif size == 'medium':
            self.base_width = 70
        elif size == 'large':
            self.base_width = 150

        self.setFixedWidth(self.base_width)

        # self.setFixedHeight(25)
        self.setPlaceholderText('')

        f = self.font()
        f.setPointSize(10)
        self.setFont(f)
        self.textChanged.connect(self.text_changed)
        self.editingFinished.connect(self.editing_finished)

    def text_changed(self, new_text):
        if self.resizing:
            fm = QFontMetrics(self.font())
            text_width = fm.width(new_text)
            new_width = text_width+15
            self.setFixedWidth(new_width if new_width > self.base_width else self.base_width)

            self.node.update_shape()
            # self.parent_node_instance.rebuild_ui()  # see rebuild_ui() for explanation

    def editing_finished(self):
        # self.node.update(self.node.inputs.index(self.input))
        self.trigger_update.emit(self.get_val())

    def remove_event(self):
        pass

    def get_val(self):
        val = None
        try:
            val = eval(self.text())
        except Exception as e:
            # type(eval(json.dumps(self.text()))) could be 'dict' <- need that for typing in dicts later if I want to
            val = self.text()
        return val

    def get_data(self) -> dict:
        return {'text': self.text()}

    def set_data(self, data):
        if type(data) == str:  # backwards compatibility
            self.setText(data)
        elif type(data) == dict:
            self.setText(data['text'])

    def val_update_event(self, val):
        self.setText(str(val))


class RCIW_BUILTIN_LineEdit_small(RCIW_BUILTIN_LineEdit):
    pass

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QCheckBox, QComboBox
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











class Data_IW(QLineEdit, IWB):  # virtual

    base_width = None  # specified by subclasses

    def __init__(self, params):
        QLineEdit.__init__(self)
        IWB.__init__(self, params)

        dtype = self.input.dtype

        self.setFont(QFont('source code pro', 10))
        self.val_update_event(dtype.default)
        if dtype.size == 's':
            self.base_width = 30
        elif dtype.size == 'm':
            self.base_width = 70
        elif dtype.size == 'l':
            self.base_width = 150
        self.max_width = self.base_width * 3
        self.setFixedWidth(self.base_width)
        self.fm = QFontMetrics(self.font())

        self.setToolTip(dtype.doc)
        self.textChanged.connect(self.text_changed)
        self.editingFinished.connect(self.editing_finished)

    def text_changed(self, new_text):
        text_width = self.fm.width(new_text)
        new_width = text_width+15  # add some buffer
        if new_width < self.max_width:
            self.setFixedWidth(new_width if new_width > self.base_width else self.base_width)
        else:
            self.setFixedWidth(self.max_width)
        self.node.update_shape()

    def editing_finished(self):
        self.update_node()

    def get_val(self):
        try:
            return eval(self.text())
        except Exception as e:
            return self.text()

    def val_update_event(self, val):
        try:
            self.setText(str(val))
        except Exception as e:
            pass

    def get_data(self) -> dict:
        return {'text': self.text()}

    def set_data(self, data: dict):
        self.setText(data['text'])


# custom sized classes for qss access:

class Data_IW_S(Data_IW):
    base_width = 30


class Data_IW_M(Data_IW):
    base_width = 70


class Data_IW_L(Data_IW):
    base_width = 150


# -----------------------------------


class String_IW(QLineEdit, IWB):  # virtual

    width = None  # specified by subclasses

    def __init__(self, params):
        QLineEdit.__init__(self)
        IWB.__init__(self, params)

        dtype = self.input.dtype

        self.setFont(QFont('source code pro', 10))
        self.setText(dtype.default)
        self.setFixedWidth(self.width)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        if not self.block:
            self.update_node()

    def get_val(self):
        return self.text()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setText(val)
        finally:
            self.block = False

    def get_data(self) -> dict:
        return {'text': self.text()}

    def set_data(self, data: dict):
        self.setText(data['text'])


# custom sized classes for qss access:

class String_IW_S(String_IW):
    width = 30


class String_IW_M(String_IW):
    width = 70


class String_IW_L(String_IW):
    width = 150


# -----------------------------------


class Integer_IW(QSpinBox, IWB):
    def __init__(self, params):
        QSpinBox.__init__(self)
        IWB.__init__(self, params)

        dtype = self.input.dtype

        if dtype.bounds:
            self.setRange(dtype.bounds[0], dtype.bounds[1])
        self.setValue(dtype.default)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.valueChanged.connect(self.val_changed)

    def val_changed(self, val):
        if not self.block:
            self.update_node()

    def get_val(self):
        return self.value()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setValue(val)
        finally:
            self.block = False

    def get_data(self) -> dict:
        return {'val': self.value()}

    def set_data(self, data: dict):
        self.setValue(data['val'])


class Float_IW(QLineEdit, IWB):
    def __init__(self, params):
        QLineEdit.__init__(self)
        IWB.__init__(self, params)

        dtype = self.input.dtype

        self.setFont(QFont('source code pro', 10))
        fm = QFontMetrics(self.font())
        self.setMaximumWidth(fm.width(dtype.decimals+1))
        self.setText(dtype.default)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.textChanged.connect(self.text_changed)

    def text_changed(self):
        if not self.block:
            self.update_node()

    def get_val(self):
        return self.text()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setText(str(val))
        finally:
            self.block = False

    def get_data(self) -> dict:
        return {'text': self.text()}

    def set_data(self, data: dict):
        self.setText(data['text'])


class Boolean_IW(QCheckBox, IWB):
    def __init__(self, params):
        QCheckBox.__init__(self)
        IWB.__init__(self, params)

        dtype = self.input.dtype

        self.setChecked(dtype.default)

        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.stateChanged.connect(self.state_changed)

    def state_changed(self, state):
        if not self.block:
            self.update_node()

    def get_val(self):
        return self.isChecked()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setChecked(val)
        finally:
            self.block = False

    def get_data(self) -> dict:
        return {'checked': self.isChecked()}

    def set_data(self, data: dict):
        self.setChecked(data['checked'])


class Choice_IW(QComboBox, IWB):
    def __init__(self, params):
        QComboBox.__init__(self)
        IWB.__init__(self, params)

        dtype = self.input.dtype

        self.addItems(dtype.items)
        self.setCurrentText(dtype.default)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.currentTextChanged.connect(self.text_changed)

    def text_changed(self):
        if not self.block:
            self.update_node()

    def get_val(self):
        return self.currentText()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setCurrentText(val)
        finally:
            self.block = False

    def get_data(self) -> dict:
        return {
            'items': [self.itemText(i) for i in range(self.count())],
            'active': self.currentText(),
        }

    def set_data(self, data: dict):
        self.clear()
        self.addItems(data['items'])
        self.setCurrentText(data['active'])

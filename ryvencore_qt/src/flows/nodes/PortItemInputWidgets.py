from qtpy.QtGui import QFontMetrics, QFont
from qtpy.QtWidgets import QSpinBox, QLineEdit, QCheckBox, QComboBox

from .WidgetBaseClasses import IWB


class DType_IW_Base(IWB):
    def __str__(self):
        return self.__class__.__name__


class Data_IW(DType_IW_Base, QLineEdit):  # virtual

    base_width = None  # specified by subclasses

    def __init__(self, params):
        DType_IW_Base.__init__(self, params)
        QLineEdit.__init__(self)

        dtype = self.input.dtype
        self.last_val = None

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
        v = self.get_val()
        if v != self.last_val:
            self.update_node_input(v)
            self.last_val = v

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

    def get_state(self) -> dict:
        return {'text': self.text()}

    def set_state(self, data: dict):
        self.setText(data['text'])
        # self.update_node_input(self.get_val())


# custom sized classes for qss access:

class Data_IW_S(Data_IW):
    base_width = 30


class Data_IW_M(Data_IW):
    base_width = 70


class Data_IW_L(Data_IW):
    base_width = 150


# -----------------------------------


class String_IW(DType_IW_Base, QLineEdit):  # virtual

    width = None  # specified by subclasses

    def __init__(self, params):
        DType_IW_Base.__init__(self, params)
        QLineEdit.__init__(self)

        dtype = self.input.dtype
        self.last_val = None

        self.setFont(QFont('source code pro', 10))
        self.setText(dtype.default)
        self.setFixedWidth(self.width)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        if not self.block:
            v = self.get_val()
            if v != self.last_val:
                self.update_node_input(v)
                self.last_val = v

    def get_val(self):
        return self.text()

    def val_update_event(self, val):
        self.block = True
        self.setText(str(val))
        self.block = False

    def get_state(self) -> dict:
        return {'text': self.text()}

    def set_state(self, data: dict):
        self.setText(data['text'])
        # self.editing_finished()


# custom sized classes for qss access:

class String_IW_S(String_IW):
    width = 30


class String_IW_M(String_IW):
    width = 70


class String_IW_L(String_IW):
    width = 150


# -----------------------------------


class Integer_IW(DType_IW_Base, QSpinBox):
    def __init__(self, params):
        DType_IW_Base.__init__(self, params)
        QSpinBox.__init__(self)

        dtype = self.input.dtype

        if dtype.bounds:
            self.setRange(dtype.bounds[0], dtype.bounds[1])
        self.setValue(dtype.default)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.valueChanged.connect(self.val_changed)

    def val_changed(self, val):
        if not self.block:
            self.update_node_input(val)

    def get_val(self):
        return self.value()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setValue(val)
        except Exception as e:
            pass
        finally:
            self.block = False

    def get_state(self) -> dict:
        return {'val': self.value()}

    def set_state(self, data: dict):
        self.setValue(data['val'])


class Float_IW(DType_IW_Base, QLineEdit):
    def __init__(self, params):
        DType_IW_Base.__init__(self, params)
        QLineEdit.__init__(self)

        dtype = self.input.dtype

        self.setFont(QFont('source code pro', 10))
        fm = QFontMetrics(self.font())
        self.setMaximumWidth(fm.width(' ')*dtype.decimals+1)
        self.setText(str(dtype.default))
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.textChanged.connect(self.text_changed)

    def text_changed(self):
        if not self.block:
            self.update_node_input(self.get_val())

    def get_val(self):
        return float(self.text())

    def val_update_event(self, val):
        self.block = True
        try:
            self.setText(str(val))
        except Exception as e:
            pass
        finally:
            self.block = False

    def get_state(self) -> dict:
        return {'text': self.text()}

    def set_state(self, data: dict):
        self.setText(data['text'])
        # self.update_node_input(self.get_val())


class Boolean_IW(DType_IW_Base, QCheckBox):
    def __init__(self, params):
        DType_IW_Base.__init__(self, params)
        QCheckBox.__init__(self)

        dtype = self.input.dtype

        self.setChecked(dtype.default)

        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.stateChanged.connect(self.state_changed)

    def state_changed(self, state):
        if not self.block:
            self.update_node_input(self.get_val())

    def get_val(self):
        return self.isChecked()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setChecked(bool(val))
        except Exception as e:
            pass
        finally:
            self.block = False

    def get_state(self) -> dict:
        return {'checked': self.isChecked()}

    def set_state(self, data: dict):
        self.setChecked(data['checked'])


class Choice_IW(DType_IW_Base, QComboBox):
    def __init__(self, params):
        DType_IW_Base.__init__(self, params)
        QComboBox.__init__(self)

        dtype = self.input.dtype

        self.addItems(dtype.items)
        self.setCurrentText(dtype.default)
        self.setToolTip(dtype.doc)

        self.block = False  # ignore updates from val_update_event
        self.currentTextChanged.connect(self.text_changed)

    def text_changed(self):
        if not self.block:
            self.update_node_input(self.get_val())

    def get_val(self):
        return self.currentText()

    def val_update_event(self, val):
        self.block = True
        try:
            self.setCurrentText(val)
        except Exception as e:
            pass
        finally:
            self.block = False

    def get_state(self) -> dict:
        return {
            'items': [self.itemText(i) for i in range(self.count())],
            'active': self.currentText(),
        }

    def set_state(self, data: dict):
        self.clear()
        self.addItems(data['items'])
        self.setCurrentText(data['active'])

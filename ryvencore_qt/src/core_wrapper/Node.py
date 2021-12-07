from qtpy.QtCore import QObject, Signal

from ryvencore import Node as RC_Node
from ..GlobalAttributes import Location
from ryvencore.dtypes import DType


class Node(RC_Node, QObject):
    """Base class nodes in ryvencore-qt"""

    description_html: str = None
    main_widget_class: list = None
    main_widget_pos: str = 'below ports'
    input_widget_classes: dict = {}
    style: str = 'normal'
    color: str = '#c69a15'
    icon: str = None

    # SIGNALS
    updated = Signal()
    input_added = Signal(object, object)
    output_added = Signal(object, object)
    input_removed = Signal(object)
    output_removed = Signal(object)
    update_shape_triggered = Signal()
    hide_unconnected_ports_triggered = Signal()
    show_unconnected_ports_triggered = Signal()

    def __init__(self, params):
        QObject.__init__(self)
        RC_Node.__init__(self, params)

        self.default_actions = self.init_default_actions()
        self.actions = {}
        self.display_title = self.title

        self.item = None  # set by the flow view

    """actions"""

    def init_default_actions(self) -> dict:
        actions = {
            'update shape': {'method': self.update_shape},
            'hide unconnected ports': {'method': self.hide_unconnected_ports},
            'change title': {'method': self.change_title}
        }
        return actions


    def set_special_actions_data(self, actions_data):
        actions = {}
        for key in actions_data:
            if type(actions_data[key]) != dict:
                if key == 'method':
                    try:
                        actions['method'] = getattr(self, actions_data[key])
                    except AttributeError:  # outdated method referenced
                        pass
                elif key == 'data':
                    actions['data'] = actions_data[key]
            else:
                actions[key] = self.set_special_actions_data(actions_data[key])
        return actions


    def get_special_actions_data(self, actions):
        cleaned_actions = actions.copy()
        for key in cleaned_actions:
            v = cleaned_actions[key]
            # if type(v) == M:  # callable(v):
            #     cleaned_actions[key] = v.method_name
            if callable(v):
                cleaned_actions[key] = v.__name__
            elif type(v) == dict:
                cleaned_actions[key] = self.get_special_actions_data(v)
            else:
                cleaned_actions[key] = v
        return cleaned_actions


    def get_extended_default_actions(self):
        actions_dict = self.default_actions.copy()
        for index in range(len(self.inputs)):
            inp = self.inputs[index]
            if inp.type_ == 'exec':
                actions_dict['exec input '+str(index)] = {'method': self.action_exec_input,
                                                          'data': {'input index': index}}
        return actions_dict


    def action_exec_input(self, data):
        self.update(data['input index'])

    """
    specifications of ryvencore.Node's default behavior:
    """

    # @override
    def update(self, inp=-1):
        RC_Node.update(self, inp)
        self.updated.emit()

    # @override
    def create_input(self, label: str = '', type_: str = 'data', add_data={}, insert: int = None):
        RC_Node.create_input(self, label=label, type_=type_, add_data=add_data, insert=insert)

        if insert is not None:

            if insert < 0:
                index = insert-1
            else:
                index = insert

            self.input_added.emit(self.inputs[index], insert)

        else:
            self.input_added.emit(self.inputs[-1], None)

    # @override
    def create_input_dt(self, dtype: DType, label: str = '', add_data={}, insert: int = None):
        RC_Node.create_input_dt(self, dtype=dtype, label=label, add_data=add_data, insert=insert)

        if insert is not None:

            if insert < 0:
                index = insert-1
            else:
                index = insert

            self.input_added.emit(self.inputs[index], insert)
        else:
            self.input_added.emit(self.inputs[-1], None)

    # @override
    def rename_input(self, index: int, label: str):
        RC_Node.rename_input(self, index=index, label=label)
        self.update_shape()

    # @override
    def delete_input(self, index):
        inp = self.inputs[index]
        RC_Node.delete_input(self, index=index)
        self.input_removed.emit(inp)

    # @override
    def create_output(self, label: str = '', type_: str = 'data', insert: int = None):
        RC_Node.create_output(self, label=label, type_=type_, insert=insert)

        if insert is not None:

            if insert < 0:
                index = insert-1
            else:
                index = insert

            self.output_added.emit(self.outputs[index], insert)
        else:
            self.output_added.emit(self.outputs[-1], None)

    # @override
    def rename_output(self, index: int, label: str):
        RC_Node.rename_output(self, index=index, label=label)
        self.update_shape()

    # @override
    def delete_output(self, index):
        out = self.outputs[index]
        RC_Node.delete_output(self, index=index)
        self.output_removed.emit(out)

    # @override
    def additional_data(self) -> dict:
        return {
            'special actions': self.get_special_actions_data(self.actions),
            'display title': self.display_title,
        }

    # @override
    def load_additional_data(self, data: dict):
        self.actions = self.set_special_actions_data(data['special actions'])
        self.display_title = data['display title']

    # @override
    def input(self, index: int):
        if len(self.inputs[index].connections) == 0 and self.item:
            iw = self.input_widget(index)
            return iw.get_val() if iw else None
        else:
            return RC_Node.input(self, index)

    # @override
    def prepare_removal(self):  # gets also subclassed by user
        if self.main_widget():
            self.main_widget().remove_event()
        RC_Node.prepare_removal(self)


    """
    additional stuff for GUI access:
    [everything below is pure ryvencore-qt API]
    """


    def set_display_title(self, t: str):
        self.display_title = t
        self.update_shape()


    def flow_view(self):
        """Returns the registered FlowView of the parent script, but None if the view isn't existent
        which can happen if you call this early"""

        return self.session.flow_views[self.flow.script] if self.flow.script in self.session.flow_views else None


    def main_widget(self):
        """Returns the main_widget object, or None if the item doesn't exist (yet)"""
        if self.item:
            return self.item.main_widget
        else:
            return None


    def has_main_widget(self):
        return self.main_widget() is not None


    def input_widget(self, index: int):
        """Returns a reference to the widget of the corresponding input"""

        return self.port_item(self.inputs[index]).widget


    def session_stylesheet(self) -> str:
        """Returns the registered stylesheet of the session"""

        return self.session.design.global_stylesheet


    def port_item(self, port_obj):
        """Returns the port item object associated with a given port object"""

        if port_obj in self.inputs:
            return self.item.inputs[self.inputs.index(port_obj)]
        elif port_obj in self.outputs:
            return self.item.outputs[self.outputs.index(port_obj)]
        return None


    def update_shape(self):
        """Causes recompilation of the whole shape of the GUI item."""

        self.update_shape_triggered.emit()


    def hide_unconnected_ports(self):
        """Causes the GUI item to hide all unconnected ports"""

        del self.default_actions['hide unconnected ports']
        self.default_actions['show unconnected ports'] = {'method': self.show_unconnected_ports}
        self.hide_unconnected_ports_triggered.emit()


    def show_unconnected_ports(self):
        """Causes the GUI item to show all unconnected ports that have been hidden previously"""

        del self.default_actions['show unconnected ports']
        self.default_actions['hide unconnected ports'] = {'method': self.hide_unconnected_ports}
        self.show_unconnected_ports_triggered.emit()


    def change_title(self):
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLineEdit

        class ChangeTitleDialog(QDialog):
            def __init__(self, title):
                super().__init__()
                self.new_title = None
                self.setLayout(QVBoxLayout())
                self.line_edit = QLineEdit(title)
                self.layout().addWidget(self.line_edit)
                self.line_edit.returnPressed.connect(self.return_pressed)

            def return_pressed(self):
                self.new_title = self.line_edit.text()
                self.accept()

        d = ChangeTitleDialog(self.display_title)
        d.exec_()
        if d.new_title:
            self.set_display_title(d.new_title)

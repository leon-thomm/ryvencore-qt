from qtpy.QtCore import QObject, Signal


class NodeGUI(QObject):
    """
    Interface class between nodes and their GUI representation.
    """

    updated = Signal()
    update_error = Signal(object)
    input_added = Signal(object, object)
    output_added = Signal(object, object)
    input_removed = Signal(object)
    output_removed = Signal(object)
    update_shape_triggered = Signal()
    hide_unconnected_ports_triggered = Signal()
    show_unconnected_ports_triggered = Signal()

    def __init__(self, node, node_item, session_gui):
        QObject.__init__(self)

        self.node = node
        self.node_item = node_item
        self.session_gui = session_gui
        setattr(node, 'gui', self)

        # TODO: move actions to ryvencore
        self.actions = self.init_default_actions()

        self.display_title = self.title
        self.error_during_update = False

        # turn ryvencore signals into Qt signals
        self.node.updated.connect(self.on_updated)
        self.node.update_error.connect(self.on_update_error)
        self.node.input_added.connect(self.input_added.emit)
        self.node.output_added.connect(self.output_added.emit)
        self.node.input_removed.connect(self.input_removed.emit)
        self.node.output_removed.connect(self.output_removed.emit)

    """
    actions
    """

    def init_default_actions(self):
        """
        Returns the default actions every node should have
        """
        return {
            'update shape': {'method': self.update_shape},
            'hide unconnected ports': {'method': self.hide_unconnected_ports},
            'change title': {'method': self.change_title},
        }

    def deserialize_actions(self, actions_data):
        """
        Recursively reconstructs the actions dict from the serialized version
        """

        def _transform(actions_data: dict):
            """
            Mutates the actions_data argument by replacing the method names
            with the actual methods.
            """
            for key, value in actions_data.items():
                if isinstance(value, dict):
                    if 'method' in value:
                        value['method'] = getattr(self, value['method'])
                    _transform(value)

        _transform(actions_data)
        return actions_data

    def serialize_actions(self, actions):
        """
        Recursively transforms the actions dict into a JSON-compatible dict
        by replacing methods with their name
        """

        def _transform(actions: dict):
            for key, value in actions.items():
                if isinstance(value, dict):
                    if 'method' in value:
                        value['method'] = value['method'].__name__
                    _transform(value)

        return _transform(actions)

    """
    extensions
    """

    def on_updated(self, inp):
        if self.error_during_update:
            # an error should prevent an update event, so if we
            # are here, the update was successful
            self.self.error_during_update = False
            self.item.remove_error_message()
        self.updated.emit()

    def on_update_error(self, e):
        self.item.display_error(e)
        self.error_during_update = True
        self.update_error.emit(e)

    def data(self):
        return {
            'actions': self.serialize_actions(self.actions),
            'display title': self.display_title,
        }

    def load(self, data):
        self.actions = self.deserialize_actions(data['actions'])
        self.display_title = data['display title']

        if 'special actions' in data:   # backward compatibility
            self.actions = self.deserialize_actions(data['special actions'])

    """
    GUI access methods
    """

    def set_display_title(self, t: str):
        self.display_title = t
        self.update_shape()

    def flow_view(self):
        return self.node_item.flow_view

    def main_widget(self):
        """Returns the main_widget object, or None if the item doesn't exist (yet)"""

        return self.node_item.main_widget

    def input_widget(self, index: int):
        """Returns a reference to the widget of the corresponding input"""

        return self.item.inputs[index].widget

    def session_stylesheet(self):
        return self.session_gui.design.global_stylesheet

    def update_shape(self):
        """Causes recompilation of the whole shape of the GUI item."""

        self.update_shape_triggered.emit()

    def hide_unconnected_ports(self):
        """Hides all ports that are not connected to anything."""

        del self.actions['hide unconnected ports']
        self.actions['show unconnected ports'] = {'method': self.show_unconnected_ports}
        self.hide_unconnected_ports_triggered.emit()

    def show_unconnected_ports(self):
        """Shows all ports that are not connected to anything."""

        del self.actions['show unconnected ports']
        self.actions['hide unconnected ports'] = {'method': self.hide_unconnected_ports}
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

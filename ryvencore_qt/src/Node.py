from qtpy.QtCore import Signal

from .ryvencore import *
from .ryvencore import Node as RC_Node
from .GlobalAttributes import Location


class Node(RC_Node):
    """Base class nodes in ryvencore-qt"""

    description_html: str = None
    main_widget_class: list = None
    main_widget_pos: str = 'below ports'
    input_widget_classes: dict = {}
    style: str = 'extended'
    color: str = '#c69a15'
    icon: str = None

    update_shape_triggered = Signal()
    hide_unused_ports_triggered = Signal()
    show_unused_ports_triggered = Signal()

    def __init__(self, params):
        super().__init__(params)

        self.default_actions = self.init_default_actions()
        self.special_actions = {}

        # self.display_title = self.title  TODO: Node display_title

        self.item = None  # set by the flow view

    @staticmethod
    def complete_default_node_classes():
        func_node_icon = Location.PACKAGE_PATH + '/resources/pics/function_picture.png'
        from .ryvencore.FunctionScript import FunctionScript
        FunctionScript.FunctionScriptNode.icon = func_node_icon


    def init_default_actions(self) -> dict:
        actions = {
            'update shape': {'method': self.update_shape},
            'hide unused ports': {'method': self.hide_unused_ports}
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
    Some specifications of ryvencore.Node's default behavior:
    """

    # @override
    def custom_config_data(self) -> dict:
        return {
            'special actions': self.get_special_actions_data(self.special_actions),
            # 'display title': self.display_title,
        }

    # @override
    def load_custom_config(self, data: dict):
        self.special_actions = self.set_special_actions_data(data['special actions'])
        # if 'display title' in data:
        #     self.display_title = data['display title']

    # @override
    def input(self, index: int):
        if len(self.inputs[index].connections) == 0:
            iw = self.input_widget(index)
            return iw.get_val() if iw else None
        else:
            return super().input(index)

    # @override
    def prepare_removal(self):  # gets also subclassed by user
        if self.main_widget():
            self.main_widget().remove_event()
        super().prepare_removal()


    """
    Additional stuff for GUI access:
    """


    def flow_view(self):
        """Returns the registered FlowView of the parent script, but None if the view isn't existent
        which can happen if you call this early"""

        return self.session.flow_views[self.flow.script] if self.flow.script in self.session.flow_views else None


    def main_widget(self):
        return self.item.main_widget


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


    def hide_unused_ports(self):
        """Causes the GUI item to hide all unconnected ports"""

        del self.default_actions['hide unused ports']
        self.default_actions['show unused ports'] = {'method': self.show_unused_ports}
        self.hide_unused_ports_triggered.emit()


    def show_unused_ports(self):
        """Causes the GUI item to show all unconnected ports that have been hidden previously"""

        del self.default_actions['show unused ports']
        self.default_actions['hide unused ports'] = {'method': self.hide_unused_ports}
        self.show_unused_ports_triggered.emit()

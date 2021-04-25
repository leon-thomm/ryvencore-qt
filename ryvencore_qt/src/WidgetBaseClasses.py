"""The base classes for node custom widgets for nodes."""


class MWB:
    """MainWidgetBase"""

    def __init__(self, params):
        self.node, self.node_item = params

    # OVERRIDE
    def get_state(self) -> dict:
        data = {}
        return data

    # OVERRIDE
    def set_state(self, data: dict):
        pass

    # OVERRIDE
    def remove_event(self):
        pass

    def update_node(self):
        self.node.update()

    def update_node_shape(self):
        self.node_item.update_shape()


class IWB:
    """InputWidgetBase"""

    def __init__(self, params):
        self.input, self.input_item, self.node, self.node_item = params

    # OVERRIDE
    def get_val(self):
        """
        Returns the value that the widget represents for the data input.
        It has to be (pickle) serializable!
        """

        return None

    # OVERRIDE
    def get_state(self) -> dict:
        data = {}
        return data

    # OVERRIDE
    def set_state(self, data: dict):
        pass

    # OVERRIDE
    def remove_event(self):
        pass

    # OVERRIDE
    def val_update_event(self, val):
        pass

    def update_node_input(self, val):
        self.input.update(val)

    def update_node(self):
        self.node.update(self.node.inputs.index(self.input))

    def update_node_shape(self):
        self.node_item.update_shape()

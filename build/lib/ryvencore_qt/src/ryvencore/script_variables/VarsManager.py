from PySide2.QtCore import Signal, QObject

from .Variable import Variable

from ..InfoMsgs import InfoMsgs


class VarsManager(QObject):
    """Manages script variables and triggers receivers when values of variables change"""

    new_var_created = Signal(Variable)
    var_deleted = Signal(Variable)
    var_val_changed = Signal(Variable, object)

    def __init__(self, script, config=None):
        super().__init__()

        self.script = script

        self.variables: [Variable] = []
        self.var_receivers = {}

        if config is not None:
            for name in config.keys():  # variables
                self.create_new_var(name, val=config[name])

    def check_new_var_name_validity(self, name: str) -> bool:
        """Checks if a var name candidate is empty or already used"""

        if len(name) == 0:
            return False

        # search for name issues
        for v in self.variables:
            if v.name == name:
                return False

        return True

    def create_new_var(self, name: str, val=None) -> Variable:
        """Creates and returns a new script variable and emits new_var_created"""

        v = Variable(name, val)
        self.variables.append(v)
        self.new_var_created.emit(v)
        return v

    def get_var(self, name) -> Variable:
        """Returns script variable with given name or None if it couldn't be found."""

        InfoMsgs.write('getting variable with name:', name)

        for v in self.variables:
            if v.name == name:
                return v
        return None

    def get_var_val(self, name):
        """Returns the value of a script variable with given name or None if it couldn't be found"""

        var = self.get_var(name)
        return var.val if var is not None else None

    def set_var(self, name, val) -> bool:
        """Sets the value of an existing script variable.
        Returns true in case of success, false if the var couldn't be found and set."""

        var_index = self._get_var_index_from_name(name)
        if var_index is None:
            return False

        var = self.variables[var_index]
        var.val = val
        self.var_val_changed.emit(var, var.val)

        # update all variable usages by calling all registered object's methods on updated variable with the new val
        for receiver, var_name in self.var_receivers.keys():
            if var_name == name:
                self.var_receivers[receiver, var_name](var_name, val)  # calling the slot method

        return True

    def _get_var_index_from_name(self, name):
        var_names_list = [v.name for v in self.variables]
        for i in range(len(var_names_list)):
            if var_names_list[i] == name:
                return i

        return None

    def delete_variable(self, var: Variable):
        """Deletes a variable and triggers the var_deleted signal."""

        self.variables.remove(var)
        self.var_deleted.emit(var)

    def register_receiver(self, receiver, var_name: str, method):
        """A registered receiver (method) gets triggered every time the
        value of a variable with the given name changes (also when it gets created)."""

        self.var_receivers[(receiver, var_name)] = method

    def unregister_receiver(self, receiver, var_name: str) -> bool:
        """Unregisters a method and returns true in case of success. See also register_receiver()."""

        try:
            del self.var_receivers[(receiver, var_name)]
            return True
        except Exception:
            return False

    def config_data(self) -> dict:
        """Returns the config data of the script variables."""

        vars_dict = {}
        for v in self.variables:
            vars_dict[v.name] = {'serialized': v.serialize()}
        return vars_dict

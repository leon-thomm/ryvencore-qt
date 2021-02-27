from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QWidget
from ..ConnectionItem import DataConnectionItem, ExecConnectionItem  # TODO [!DEPENDENCY!]

from .Connection import DataConnection, ExecConnection

from .Script import Script
from .FunctionScript import FunctionScript
from .FunctionNodeTypes import FunctionInputNode, FunctionOutputNode
from ..SessionThreadingBridge import SessionThreadingBridge  # TODO [!DEPENDENCY!]
from .InfoMsgs import InfoMsgs
from ..Design import Design  # TODO [!DEPENDENCY!]


class Session(QObject):
    """The Session is the top level interface to an editor, it represents a project and manages all project-wide
    components, i.e. Scripts, FunctionScripts and Node blueprints."""

    new_script_created = Signal(Script)
    script_renamed = Signal(Script)
    script_deleted = Signal(Script)


    def __init__(
            self,
            threaded: bool = False,
            gui_parent: QWidget = None,
            flow_theme_name=None,
            performance_mode=None,
            data_conn_class=None,
            data_conn_item_class=None,
            exec_conn_class=None,
            exec_conn_item_class=None,
            parent: QObject = None
    ):
        super().__init__(parent=parent)

        Design._register_fonts()

        # BASE CLASSES
        self.DataConnClass = DataConnection
        self.DataConnItemClass = DataConnectionItem
        self.ExecConnClass = ExecConnection
        self.ExecConnItemClass = ExecConnectionItem

        if data_conn_class:
            self.DataConnClass = data_conn_class
        if data_conn_item_class:
            self.DataConnItemClass = data_conn_item_class
        if exec_conn_class:
            self.ExecConnClass = exec_conn_class
        if exec_conn_item_class:
            self.ExecConnItemClass = exec_conn_item_class


        # ATTRIBUTES
        self.scripts: [Script] = []
        self.function_scripts: [FunctionScript] = []
        self.nodes = []  # list of node CLASSES
        self.invisible_nodes = [FunctionInputNode, FunctionOutputNode]  # might change that system in the future

        #   threading
        self.threaded = threaded
        self.threading_bridge = None
        self.gui_parent = gui_parent
        if self.threaded:
            self.threading_bridge = SessionThreadingBridge()
            self.threading_bridge.moveToThread(gui_parent.thread())

        #   design
        self.design = Design()
        if flow_theme_name:
            self.design.set_flow_theme(name=flow_theme_name)
        if performance_mode:
            self.design.set_performance_mode(performance_mode)

    def register_nodes(self, node_classes: list):
        """Registers a list of Nodes which you then can access in all scripts"""

        for n in node_classes:
            self.register_node(n)


    def register_node(self, node_class):
        """Registers a Node which then can be accessed in all scripts"""
        if not node_class.identifier:
            node_class.identifier = node_class.__name__
            InfoMsgs.write('assigned identifier:', node_class.identifier)

        self.nodes.append(node_class)


    def unregister_node(self, node_class):
        """Unregisters a Node which will then be removed from the available list.
        Existing instances won't be affected."""

        self.nodes.remove(node_class)


    def create_script(self, title: str, flow_view_size: list = None, create_default_logs=True) -> Script:
        """Creates and returns a new script"""

        script = Script(session=self, title=title, flow_view_size=flow_view_size, create_default_logs=create_default_logs)

        self.scripts.append(script)
        self.new_script_created.emit(script)

        return script


    def create_func_script(self, title: str, flow_view_size: list = None, create_default_logs=True) -> Script:
        """Creates and returns a new FUNCTION script"""

        func_script = FunctionScript(
            session=self, title=title, flow_view_size=flow_view_size, create_default_logs=create_default_logs
        )
        func_script.initialize()

        self.function_scripts.append(func_script)
        self.new_script_created.emit(func_script)

        return func_script


    def all_scripts(self) -> list:
        """Returns a list containing all scripts and function scripts"""
        return self.function_scripts + self.scripts


    def _load_script(self, config: dict):
        """Loads a script from a project dict; emits new_script_created"""

        script = Script(session=self, config_data=config)
        self.scripts.append(script)
        self.new_script_created.emit(script)
        return script

    def _load_func_script(self, config: dict):
        """Loads a function script from a project dict without initializing it"""

        fscript = FunctionScript(session=self, config_data=config)
        self.function_scripts.append(fscript)

        # NOTE: no script_created emit here because the fscript hasn't finished initializing yet

        return fscript


    def rename_script(self, script: Script, title: str):
        """Renames an existing script; emits script_renamed"""

        script.title = title
        self.script_renamed.emit(script)


    def check_new_script_title_validity(self, title: str) -> bool:
        """Checks whether a considered title for a new script (i.e. unique) is valid or not"""

        if len(title) == 0:
            return False
        for s in self.all_scripts():
            if s.title == title:
                return False

        return True


    def delete_script(self, script: Script):
        """Deletes an existing script; emits script_deleted"""

        if isinstance(script, FunctionScript):
            self.unregister_node(script.function_node_class)
            self.function_scripts.remove(script)
        else:
            self.scripts.remove(script)

        self.script_deleted.emit(script)


    def info_messenger(self):
        """Returns a reference to InfoMsgs to print info data"""
        return InfoMsgs


    def load(self, project: dict) -> bool:
        """Loads a project and raises an error if required nodes are missing"""
        if 'scripts' not in project and 'function scripts' not in project:
            return False

        if 'function scripts' in project:
            new_func_scripts = []
            for fsc in project['function scripts']:
                new_func_scripts.append(self._load_func_script(config=fsc))

            # now all func nodes have been registered, so we can initialize the scripts

            for fs in new_func_scripts:
                fs.initialize()
                self.new_script_created.emit(fs)

        for sc in project['scripts']:
            self._load_script(config=sc)

        return True


    def serialize(self) -> dict:
        """Returns the project as dict to be saved and loaded again using load()"""

        data = {}

        func_scripts_list = []
        for fscript in self.function_scripts:
            func_scripts_list.append(fscript.serialize())
        data['function scripts'] = func_scripts_list

        scripts_list = []
        for script in self.scripts:
            scripts_list.append(script.serialize())
        data['scripts'] = scripts_list

        return data


    def all_nodes(self) -> list:
        """Returns a list containing all Node objects used in any flow which is useful for advanced project analysis"""

        nodes = []
        for s in self.all_scripts():
            for n in s.flow.nodes:
                nodes.append(n)
        return nodes


    def save_as_project(self, fpath: str):
        """Convenience method for directly saving the the all content as project to a file"""
        pass


    def set_stylesheet(self, s: str):
        """Sets the session's stylesheet which can be accessed by NodeItems.
        You usually want this to be the same as your window's stylesheet."""

        self.design.global_stylesheet = s

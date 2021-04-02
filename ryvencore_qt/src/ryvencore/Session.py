from .Base import Base


from .Script import Script, Flow, Logger, VarsManager
from .logging.Log import Log
from .FunctionScript import FunctionScript
from .InfoMsgs import InfoMsgs
from .RC import CLASSES
from .Node import Node
from .Connection import DataConnection, ExecConnection


class Session(Base):
    """The Session is the top level interface to an editor, it represents a project and manages all project-wide
    components, i.e. Scripts, FunctionScripts and Node blueprints."""

    def __init__(
            self,
            gui: bool = False,
    ):
        Base.__init__(self)

        if not CLASSES['node base']:
            CLASSES['node base'] = Node
        if not CLASSES['data conn']:
            CLASSES['data conn'] = DataConnection
        if not CLASSES['exec conn']:
            CLASSES['exec conn'] = ExecConnection
        if not CLASSES['logger']:
            CLASSES['logger'] = Logger
        if not CLASSES['log']:
            CLASSES['log'] = Log
        if not CLASSES['vars manager']:
            CLASSES['vars manager'] = VarsManager
        if not CLASSES['flow']:
            CLASSES['flow'] = Flow

        # initialize node classes for FunctionScripts with correct Node base
        FunctionScript.build_node_classes()

        # ATTRIBUTES
        self.scripts: [Script] = []
        self.function_scripts: [FunctionScript] = []
        self.nodes = []  # list of node CLASSES
        self.invisible_nodes = [FunctionScript.FunctionInputNode, FunctionScript.FunctionOutputNode]  # might change that system in the future
        self.gui: bool = gui


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


    def create_script(self, title: str = None, create_default_logs=True,
                      config: dict = None) -> Script:

        """Creates and returns a new script.
        If a config is provided the title parameter will be ignored."""

        script = Script(
            session=self, title=title, create_default_logs=create_default_logs,
            config_data=config
        )

        self.scripts.append(script)
        script.load_flow()

        return script


    def create_func_script(self, title: str = None, create_default_logs=True,
                           config: dict = None) -> Script:

        """Creates and returns a new function script.
        If a config is provided the title parameter will be ignored and the script will not be initialized,
        which you need to do manually after you made sure that the config doesnt contain other function nodes
        that have not been loaded yet."""

        func_script = FunctionScript(
            session=self, title=title, create_default_logs=create_default_logs,
            config_data=config
        )

        self.function_scripts.append(func_script)

        # if config is provided, the script's flow contains content that might include
        # functions nodes that are not loaded yet, so initialization is triggered manually from outside then
        if not config:
            func_script.load_flow()

        return func_script


    def all_scripts(self) -> list:
        """Returns a list containing all scripts and function scripts"""
        return self.function_scripts + self.scripts


    def rename_script(self, script: Script, title: str):
        """Renames an existing script"""

        script.title = title


    def check_new_script_title_validity(self, title: str) -> bool:
        """Checks whether a considered title for a new script (i.e. unique) is valid or not"""

        if len(title) == 0:
            return False
        for s in self.all_scripts():
            if s.title == title:
                return False

        return True


    def delete_script(self, script: Script):
        """Deletes an existing script"""

        if isinstance(script, FunctionScript):
            self.unregister_node(script.function_node_class)
            self.function_scripts.remove(script)
        else:
            self.scripts.remove(script)


    def info_messenger(self):
        """Returns a reference to InfoMsgs to print info data"""
        return InfoMsgs


    def load(self, project: dict) -> ([Script], [Script]):
        """Loads a project and raises an exception if required nodes are missing"""

        if 'scripts' not in project and 'function scripts' not in project:
            raise Exception('not a valid project dict')

        new_func_scripts = []
        if 'function scripts' in project:
            for fsc in project['function scripts']:
                new_func_scripts.append(self.create_func_script(config=fsc))

            # now all func nodes have been registered, so we can initialize the scripts

            for fs in new_func_scripts:
                fs.load_flow()

        new_scripts = []
        for sc in project['scripts']:
            new_scripts.append(self.create_script(config=sc))

        return new_scripts, new_func_scripts


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


    # def save_as_project(self, fpath: str):
    #     """Convenience method for directly saving the the all content as project to a file"""
    #     pass

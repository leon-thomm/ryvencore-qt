from .Base import Base


from .Script import Script
from .MacroScript import MacroScript
from .InfoMsgs import InfoMsgs
from .RC import CLASSES
from .Node import Node


class Session(Base):
    """The Session is the top level interface to an editor, it represents a project and manages all project-wide
    components, i.e. Scripts, MacroScripts and Node blueprints."""

    def __init__(
            self,
            gui: bool = False,
    ):
        Base.__init__(self)

        # register classes
        self.register_default_classes()

        # initialize node classes for MacroScripts with correct Node base
        MacroScript.build_node_classes()

        # ATTRIBUTES
        self.scripts: [Script] = []
        self.macro_scripts: [MacroScript] = []
        self.nodes = []  # list of node CLASSES
        self.invisible_nodes = [MacroScript.MacroInputNode, MacroScript.MacroOutputNode]  # might change that system in the future
        self.gui: bool = gui


    def register_default_classes(self):
        """
        Registers the default ryvencore-internal implementations of all exposed classes that COULD have been
        extended by the frontend, in which case it won't set the class.
        So, if the frontend extended a class like Node, it will have set CLASSES['node base'] to its own subclass,
        so we leave it as it is then. It is assumed that the frontend's extensions work properly and don't modify
        the functionality to the backend.
        """

        if not CLASSES['node base']:
            CLASSES['node base'] = Node

        if not CLASSES['data conn']:
            from .Connection import DataConnection
            CLASSES['data conn'] = DataConnection

        if not CLASSES['exec conn']:
            from .Connection import ExecConnection
            CLASSES['exec conn'] = ExecConnection

        if not CLASSES['logs manager']:
            from .logging.LogsManager import LogsManager
            CLASSES['logs manager'] = LogsManager

        if not CLASSES['logger']:
            from .logging.Logger import Logger
            CLASSES['logger'] = Logger

        if not CLASSES['vars manager']:
            from .script_variables.VarsManager import VarsManager
            CLASSES['vars manager'] = VarsManager

        if not CLASSES['flow']:
            from .Flow import Flow
            CLASSES['flow'] = Flow


    def register_nodes(self, node_classes: list):
        """Registers a list of Nodes which you then can access in all scripts"""

        for n in node_classes:
            self.register_node(n)


    def register_node(self, node_class):
        """Registers a Node which then can be accessed in all scripts"""

        # build node class identifier
        node_class.build_identifier()

        self.nodes.append(node_class)


    def unregister_node(self, node_class):
        """Unregisters a Node which will then be removed from the available list.
        Existing instances won't be affected."""

        self.nodes.remove(node_class)


    def all_node_objects(self) -> list:
        """Returns a list containing all Node objects used in any flow which is useful for advanced project analysis"""

        nodes = []
        for s in self.scripts:
            for n in s.flow.nodes:
                nodes.append(n)
        return nodes


    def create_script(self, title: str = None, create_default_logs=True,
                      data: dict = None) -> Script:

        """Creates and returns a new script.
        If data is provided the title parameter will be ignored."""

        script = Script(
            session=self, title=title, create_default_logs=create_default_logs,
            load_data=data
        )

        self.scripts.append(script)
        script.load_flow()

        return script


    def create_macro(self, title: str = None, create_default_logs=True,
                     data: dict = None) -> MacroScript:

        """
        Creates and returns a new macro script.
        If data is provided the title parameter will be ignored and the script will not be initialized,
        which you need to do manually after you made sure that the data doesnt contain other macro nodes
        that have not been loaded yet.
        """

        macro_script = MacroScript(
            session=self, title=title, create_default_logs=create_default_logs,
            load_data=data
        )

        self.scripts.append(macro_script)
        self.macro_scripts.append(macro_script)

        # if data is provided, the script's flow contains content that might include
        # macro nodes that are not loaded yet, so initialization is triggered manually from outside then
        if not data:
            macro_script.load_flow()

        return macro_script


    def rename_script(self, script: Script, title: str) -> bool:
        """Renames an existing script"""

        if self.script_title_valid(title):
            script.title = title
            return True
        else:
            return False


    def script_title_valid(self, title: str) -> bool:
        """Checks whether a considered title for a new script is valid (unique) or not"""

        if len(title) == 0:
            return False
        for s in self.scripts:  # all_scripts():
            if s.title == title:
                return False

        return True


    def delete_script(self, script: Script):
        """Deletes an existing script. If the script is a macro script, the macro node is unregistered."""

        if isinstance(script, MacroScript):
            self.unregister_node(script.macro_node_class)
            self.macro_scripts.remove(script)
            self.scripts.remove(script)
        else:
            self.scripts.remove(script)


    def info_messenger(self):
        """Returns a reference to InfoMsgs to print info data"""
        return InfoMsgs


    def load(self, project: dict) -> [Script]:
        """Loads a project and raises an exception if required nodes are missing"""

        if 'scripts' not in project and 'macro scripts' not in project:
            raise Exception('not a valid project dict')

        new_macro_scripts = []
        if 'macro scripts' in project:
            for msc in project['macro scripts']:
                new_macro_scripts.append(self.create_macro(data=msc))

            # now all macro nodes have been registered, so we can initialize the scripts

            for ms in new_macro_scripts:
                ms.load_flow()

        new_scripts = []
        for sc in project['scripts']:
            new_scripts.append(self.create_script(data=sc))

        return new_scripts + new_macro_scripts

    def serialize(self):
        """Returns the project as JSON compatible dict to be saved and loaded again using load()"""

        return self.complete_data(self.data())


    def data(self) -> dict:

        data = {}

        macro_scripts_list = []
        for m_script in self.macro_scripts:
            macro_scripts_list.append(m_script.data())
        data['macro scripts'] = macro_scripts_list

        scripts_list = []
        for script in set(self.scripts) - set(self.macro_scripts):  # exclude macro scripts
            scripts_list.append(script.data())
        data['scripts'] = scripts_list

        return data

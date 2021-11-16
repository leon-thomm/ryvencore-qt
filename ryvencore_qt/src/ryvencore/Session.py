from .Base import Base


from .Script import Script
from .InfoMsgs import InfoMsgs
from .Node import Node


class Session(Base):
    """
    The Session is the top level interface to an editor, it represents a project and manages all project-wide
    components.
    """

    def __init__(
            self,
            gui: bool = False,
            custom_classes: dict = None,
    ):
        Base.__init__(self)

        if custom_classes is None:
            custom_classes = {}

        # registry for custom class implementations
        self.CLASSES = custom_classes
        self.register_default_classes()

        # ATTRIBUTES
        self.scripts: [Script] = []
        self.nodes = []  # list of node CLASSES
        self.invisible_nodes = []
        self.gui: bool = gui
        self.init_data = None


    def register_default_classes(self):
        """
        Registers the default ryvencore-internal implementations of all exposed classes that COULD have been
        extended externally, in which case it won't set the class.
        So, if the a class like Node was extended externally, CLASSES['node base'] will be set to this custom Node
        class, so we leave it as it is then.
        """

        if 'node base' not in self.CLASSES:
            self.CLASSES['node base'] = Node

        if 'data conn' not in self.CLASSES:
            from .Connection import DataConnection
            self.CLASSES['data conn'] = DataConnection

        if 'exec conn' not in self.CLASSES:
            from .Connection import ExecConnection
            self.CLASSES['exec conn'] = ExecConnection

        if 'logs manager' not in self.CLASSES:
            from .logging import LogsManager
            self.CLASSES['logs manager'] = LogsManager

        if 'logger' not in self.CLASSES:
            from .logging import Logger
            self.CLASSES['logger'] = Logger

        if 'vars manager' not in self.CLASSES:
            from .script_variables import VarsManager
            self.CLASSES['vars manager'] = VarsManager

        if 'flow' not in self.CLASSES:
            from .Flow import Flow
            self.CLASSES['flow'] = Flow


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
        for s in self.scripts:
            if s.title == title:
                return False

        return True


    def delete_script(self, script: Script):
        """Removes an existing script."""

        self.scripts.remove(script)


    def info_messenger(self):
        """Returns a reference to InfoMsgs to print info data"""

        return InfoMsgs


    def load(self, project: dict) -> [Script]:
        """Loads a project and raises an exception if required nodes are missing"""

        if 'scripts' not in project:
            raise Exception('not a valid project dict')

        self.init_data = project

        new_scripts = []
        for sc in project['scripts']:
            new_scripts.append(self.create_script(data=sc))

        return new_scripts

    def serialize(self):
        """Returns the project as JSON compatible dict to be saved and loaded again using load()"""

        return self.complete_data(self.data())


    def data(self) -> dict:
        return {
            'scripts': [
                s.data() for s in self.scripts
            ],
        }

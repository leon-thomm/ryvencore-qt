import time

from qtpy.QtWidgets import QWidget, QApplication
from qtpy.QtCore import QObject, Signal, Qt

from .ryvencore import Session as RC_Session, Script
from .ryvencore.MacroScript import MacroScript
from .ryvencore.RC import CLASSES

from .Design import Design
from .ConnectionItem import DataConnectionItem, ExecConnectionItem
from .SessionThreadingBridge import SessionThreadingBridge
from .Node import Node
from .FlowView import FlowView
from .WRAPPERS import VarsManager, LogsManager, DataConnection, Flow, Logger


class Session(RC_Session, QObject):

    new_script_created = Signal(object)
    flow_view_created = Signal(object, object)
    script_renamed = Signal(object)
    script_deleted = Signal(object)

    build_flow_view_request = Signal(object, tuple)
    complete_flow_view_config = Signal(dict)

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
            node_class=None,
    ):
        QObject.__init__(self)

        # custom WRAPPERS
        CLASSES['node base'] = Node if not node_class else node_class
        CLASSES['data conn'] = DataConnection if not data_conn_class else data_conn_class
        CLASSES['logs manager'] = LogsManager
        CLASSES['logger'] = Logger
        CLASSES['vars manager'] = VarsManager
        CLASSES['flow'] = Flow

        if exec_conn_class:
            CLASSES['exec conn'] = exec_conn_class

        # register additional classes
        CLASSES['data conn item'] = DataConnectionItem if not data_conn_item_class else data_conn_item_class
        CLASSES['exec conn item'] = ExecConnectionItem if not exec_conn_item_class else exec_conn_item_class

        RC_Session.__init__(self, gui=True)

        # flow views
        self.flow_views = {}  # {Script : FlowView}

        # nodes
        Node.complete_default_node_classes()

        # threading
        self.threaded = threaded
        self.threading_bridge = None
        self.gui_parent = gui_parent
        self.threading_bridge = SessionThreadingBridge()
        self.threading_bridge.moveToThread(gui_parent.thread() if threaded else self.thread())
        self.build_flow_view_request.connect(self.threading_bridge.init_flow_view)

        # design
        app = QApplication.instance()
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        Design.register_fonts()
        self.design = Design()
        if flow_theme_name:
            self.design.set_flow_theme(name=flow_theme_name)
        if performance_mode:
            self.design.set_performance_mode(performance_mode)


    def create_macro(self, title: str = None, create_default_logs=True,
                     config: dict = None,
                     flow_view_size: list = None) -> MacroScript:
        """Creates and returns a new macro script.
        If a config is provided the title parameter will be ignored and the script will not be initialized,
        which you need to do manually after you made sure that the config doesnt contain other macro nodes
        that have not been loaded yet."""

        script = RC_Session.create_macro(self, title=title, create_default_logs=create_default_logs, config=config)

        self.new_script_created.emit(script)

        self._build_flow_view(script, flow_view_size)

        return script

    def create_script(self, title: str = None, create_default_logs=True,
                      config: dict = None,
                      flow_view_size: list = None) -> Script:
        """Creates and returns a new script.
        If a config is provided the title parameter will be ignored."""

        script = RC_Session.create_script(self, title=title, create_default_logs=create_default_logs, config=config)

        self.new_script_created.emit(script)

        self._build_flow_view(script, flow_view_size)

        return script

    def rename_script(self, script: Script, title: str) -> bool:
        """Renames an existing script; emits script_renamed"""

        success = RC_Session.rename_script(self, script=script, title=title)

        if success:
            self.script_renamed.emit(script)

        return success

    def delete_script(self, script: Script):
        """Deletes an existing script; emits script_deleted"""

        RC_Session.delete_script(self, script=script)
        self.script_deleted.emit(script)


    def _build_flow_view(self, script, view_size):
        """Builds the flow view in the GUI thread"""

        script_config = script.init_config

        flow_view_config = None
        if script_config is not None:
            if 'flow view' not in script_config:  # backwards compatibility
                flow_view_config = script_config['flow']
            else:
                flow_view_config = script_config['flow view']

        flow_view_params = (
            self,
            script,
            script.flow,
            flow_view_config,
            view_size,
            self.gui_parent,
        )

        # build flow view in GUI thread
        self.tmp_data = None
        self.build_flow_view_request.emit(self, flow_view_params)
        while self.tmp_data is None:
            time.sleep(0.001)
        self.tmp_data: FlowView
        flow_view = self.tmp_data

        self.flow_views[script] = flow_view
        self.flow_view_created.emit(script, flow_view)

        return flow_view

    def serialize(self) -> dict:
        """Returns the project as JSON compatible dict to be saved and loaded again using load()"""

        # adds the frontend related data to the abstract project data by the ryvencore Session

        data = RC_Session.serialize(self)

        # MACRO SCRIPTS
        complete_macro_scripts_data = []
        for ms_cfg in data['macro scripts']:
            title = ms_cfg['name']  # script titles are unique!
            macro_script = self._script_from_title(title)
            view = self.flow_views[macro_script]

            # complete script config in FlowView in GUI thread
            self.complete_flow_view_config.connect(view.generate_config_data)
            view._tmp_data = None
            self.complete_flow_view_config.emit(ms_cfg)
            while view._tmp_data is None:
                time.sleep(0.001)
            self.complete_flow_view_config.disconnect(view.generate_config_data)

            complete_macro_scripts_data.append(view._tmp_data)

        # SCRIPTS
        complete_scripts_data = []
        for s_cfg in data['scripts']:
            title = s_cfg['name']  # script title are unique!
            script = self._script_from_title(title)
            view = self.flow_views[script]

            # complete script config in FlowView in GUI thread
            self.complete_flow_view_config.connect(view.generate_config_data)
            view._tmp_data = None
            self.complete_flow_view_config.emit(s_cfg)
            while view._tmp_data is None:
                time.sleep(0.001)
            self.complete_flow_view_config.disconnect(view.generate_config_data)

            complete_scripts_data.append(view._tmp_data)

        complete_data = {
            'macro scripts': complete_macro_scripts_data,
            'scripts': complete_scripts_data,
        }

        return complete_data

    def _script_from_title(self, title: str) -> Script:
        for s in self.scripts:  # all_scripts():
            if s.title == title:
                return s
        return None

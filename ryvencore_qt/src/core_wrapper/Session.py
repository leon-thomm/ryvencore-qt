import time
from waiting import wait

from PySide2.QtCore import QTimer
from qtpy.QtWidgets import QWidget, QApplication
from qtpy.QtCore import QObject, Signal, Qt

from ..SessionThreadInterface import SessionThreadInterface_Frontend, SessionThreadInterface_Backend
from ..ryvencore import Session as RC_Session, Script
from ..ryvencore.MacroScript import MacroScript
from ..ryvencore.RC import CLASSES

from ..Design import Design
from ..ConnectionItem import DataConnectionItem, ExecConnectionItem
from .Node import Node
from ..FlowView import FlowView
from .WRAPPERS import VarsManager, LogsManager, DataConnection, Flow, Logger
from ..tools import Container, wait_until


class Session(RC_Session, QObject):

    new_script_created = Signal(object)
    flow_view_created = Signal(object, object)
    script_renamed = Signal(object)
    script_deleted = Signal(object)

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

        # register custom wrappers
        CLASSES['node base'] = Node if not node_class else node_class
        CLASSES['data conn'] = DataConnection if not data_conn_class else data_conn_class
        CLASSES['logs manager'] = LogsManager
        CLASSES['logger'] = Logger
        CLASSES['vars manager'] = VarsManager
        CLASSES['flow'] = Flow
        if exec_conn_class:
            CLASSES['exec conn'] = exec_conn_class
        # and some additional classes
        CLASSES['data conn item'] = DataConnectionItem if not data_conn_item_class else data_conn_item_class
        CLASSES['exec conn item'] = ExecConnectionItem if not exec_conn_item_class else exec_conn_item_class

        RC_Session.__init__(self, gui=True)

        # flow views
        self.flow_views = {}  # {Script : FlowView}

        # nodes
        Node.complete_default_node_classes()

        # threading
        self.threaded = threaded
        self.gui_parent = gui_parent

        self.threading_bridge__backend = SessionThreadInterface_Backend()
        self.threading_bridge__frontend = self.threading_bridge__backend.frontend
        self.threading_bridge__frontend.moveToThread(gui_parent.thread() if threaded else self.thread())

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
                     data: dict = None,
                     flow_view_size: list = None) -> MacroScript:

        script = RC_Session.create_macro(self, title=title, create_default_logs=create_default_logs, data=data)
        self.new_script_created.emit(script)
        self._build_flow_view(script, flow_view_size)

        return script

    def create_script(self, title: str = None, create_default_logs=True,
                      data: dict = None,
                      flow_view_size: list = None) -> Script:
        """Creates and returns a new script.
        If a data is provided the title parameter will be ignored."""

        script = RC_Session.create_script(self, title=title, create_default_logs=create_default_logs, data=data)

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

        script_data = script.init_data

        flow_view_data = None
        if script_data is not None:
            if 'flow view' not in script_data:  # backwards compatibility
                flow_view_data = script_data['flow']
            else:
                flow_view_data = script_data['flow view']

        flow_view = self.threading_bridge__backend.run(
            FlowView, (
                self,
                script,
                script.flow,
                flow_view_data,
                view_size,
                self.gui_parent,
            )
        )

        self.flow_views[script] = flow_view
        self.flow_view_created.emit(script, flow_view)

        return flow_view

    def _flow_view_created(self, view):
        self.temp_data = view

    def _script_from_title(self, title: str) -> Script:
        for s in self.scripts:
            if s.title == title:
                return s
        return None

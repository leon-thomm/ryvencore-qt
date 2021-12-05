from qtpy.QtWidgets import QWidget, QApplication
from qtpy.QtCore import QObject, Signal, Qt

from ..GUIBase import GUIBase
from ..SessionThreadInterface import SessionThreadInterface_Backend
from ..Design import Design
from ..flows.FlowView import FlowView
from ..utils import translate_project

from ryvencore import Session as RC_Session, Script
from ryvencore.Base import Base

from typing import Dict, List


class Session(RC_Session, QObject):

    flow_view_created = Signal(object, object)

    def __init__(
            self,
            gui_parent: QWidget = None,
    ):
        QObject.__init__(self)

        RC_Session.__init__(self, gui=True)

        # flow views
        self.flow_views = {}  # {Script : FlowView}

        # gui hierarchy
        self.gui_parent = gui_parent

        # notice: true treading is currently not supported
        self.threading_bridge__backend = SessionThreadInterface_Backend()
        self.threading_bridge__frontend = self.threading_bridge__backend.frontend
        # self.threading_bridge__frontend.moveToThread(gui_parent.thread() if threaded else self.thread())

        # set complete_data function (needs threading_bridge)
        Base.complete_data_function = GUIBase.get_complete_data_function(self)

        # design
        app = QApplication.instance()
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        Design.register_fonts()
        self.design = Design()


    def load(self, project: Dict) -> List[Script]:

        if 'macro scripts' in project:
            # backwards compatibility
            project = translate_project(project)

        return super().load(project)


    def create_script(self, title: str = None, create_default_logs=True,
                      data: dict = None,
                      flow_view_size: list = None) -> Script:
        """Creates and returns a new script, and builds the flow view.
        If a data is provided the title parameter will be ignored."""

        script = RC_Session.create_script(self, title=title, create_default_logs=create_default_logs, data=data)

        # self.new_script_created.emit(script)

        self._build_flow_view(script, flow_view_size)

        return script


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

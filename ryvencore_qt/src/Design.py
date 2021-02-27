import json

from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QFontDatabase

from .FlowTheme import FlowTheme_Toy, FlowTheme_DarkTron, FlowTheme_Ghost, FlowTheme_Blender, \
    FlowTheme_Simple, FlowTheme_Ueli, FlowTheme_Samuel1, FlowTheme, FlowTheme_Samuel1_Light, \
    FlowTheme_Samuel2, FlowTheme_Samuel2_Light
from .. import Location


class Design(QObject):
    """Design serves as a container for the stylesheet and flow themes, and sends signals to notify GUI elements
    on change of the flow theme. A configuration for the flow themes can be loaded from a json file."""

    global_stylesheet = ''

    flow_theme_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.flow_themes = []
        self.flow_theme: FlowTheme = None
        self.performance_mode: str = None
        self.node_item_shadows_enabled: bool = None
        self.animations_enabled: bool = None
        self.node_selection_stylesheet = default_node_selection_stylesheet

        # load standard default values
        self.register_flow_themes()
        self._default_flow_theme = self.flow_themes[-1]
        self.set_performance_mode('pretty')
        self.set_flow_theme(self._default_flow_theme)

    def _register_fonts():
        QFontDatabase.addApplicationFont(
            Location.PACKAGE_PATH + '/resources/fonts/poppins/Poppins-Medium.ttf'
        )
        QFontDatabase.addApplicationFont(
            Location.PACKAGE_PATH + '/resources/fonts/source_code_pro/SourceCodePro-Regular.ttf'
        )
        QFontDatabase.addApplicationFont(
            Location.PACKAGE_PATH + '/resources/fonts/asap/Asap-Regular.ttf'
        )

    def register_flow_themes(self):
        self.flow_themes = [
            FlowTheme_Toy(),
            FlowTheme_DarkTron(),
            FlowTheme_Ghost(),
            FlowTheme_Blender(),
            FlowTheme_Simple(),
            FlowTheme_Ueli(),
            FlowTheme_Samuel1(),
            FlowTheme_Samuel2(),
            FlowTheme_Samuel1_Light(),
            FlowTheme_Samuel2_Light()
        ]

    def load_from_config(self, filepath: str):
        """Loads design configs from a config json file"""

        f = open(filepath, 'r')
        data = f.read()
        f.close()

        IMPORT_DATA = json.loads(data)

        if 'flow themes' in IMPORT_DATA:
            # load flow theme configs
            FTID = IMPORT_DATA['flow themes']
            for flow_theme in self.flow_themes:
                flow_theme.load(FTID)

        if 'init flow theme' in IMPORT_DATA:
            self._default_flow_theme = self.flow_theme_by_name(IMPORT_DATA.get('init flow theme'))
            self.set_flow_theme(self._default_flow_theme)

        if 'init performance mode' in IMPORT_DATA:
            self.set_performance_mode(IMPORT_DATA['init performance mode'])

    def available_flow_themes(self) -> dict:
        return {theme.name: theme for theme in self.flow_themes}

    def flow_theme_by_name(self, name: str) -> FlowTheme:
        for theme in self.flow_themes:
            if theme.name == name:
                return theme
        return None

    def set_flow_theme(self, theme: FlowTheme = None, name: str = ''):
        """You can either specify the theme by name, or directly provide a FlowTheme object"""
        if theme:
            self.flow_theme = theme
        elif name and name != '':
            self.flow_theme = self.flow_theme_by_name(name)
        else:
            return

        self.flow_theme_changed.emit(self.flow_theme.name)


    def set_performance_mode(self, new_mode: str):
        self.performance_mode = new_mode
        if new_mode == 'fast':
            self.node_item_shadows_enabled = False
        else:
            self.node_item_shadows_enabled = True

        self.flow_theme_changed.emit(self.flow_theme)

    def set_animations_enabled(self, b: bool):
        self.animations_enabled = b

    def set_node_item_shadows(self, b: bool):
        self.node_item_shadows_enabled = b





default_node_selection_stylesheet = '''
QWidget {
	background-color: #2b2b2b;
	border-radius: 3px;
	border: 1px solid #404040;;
	color: #dddddd;
}

QPushButton {
	border-radius: 5px;
	padding: 4px;
	background-color: #333333;
	min-width: 60px;
}
QPushButton:pressed {
	background-color: #3B9CD9;
}

QGroupBox {
	border: 1px solid #3B9CD9;;
	padding-top: 10px;
}

QLineEdit {
	padding: 3px;
}

QScrollArea {
	border: none;
}



QScrollBar:horizontal {
	border: none;
	background: #3f3f46;
	height: 12px;
	margin: 0 22px 0 22px;
	border-radius: 7px;
}
QScrollBar::handle:horizontal {
	background: #BCBBF2;
	min-height: 12px;
	border-radius: 5px;
}
QScrollBar::add-line:horizontal {
	background: none;
}
QScrollBar::sub-line:horizontal {
	background: none;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
	background: none;
}

QScrollBar:vertical {
	border: none;
	background: #3f3f46;
	width: 12px;
	margin: 14px 0 14px 0;
	border-radius: 5px;
}
QScrollBar::handle:vertical {
	background: #BCBBF2;
	min-height: 20px;
	border-radius: 5px;
}
QScrollBar::add-line:vertical {
	background: none;
}
QScrollBar::sub-line:vertical {
	background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
	background: none;
	border: none;
}
'''

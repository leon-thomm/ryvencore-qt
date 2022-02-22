import json

from qtpy.QtCore import QObject, Signal
from qtpy.QtGui import QFontDatabase

from .flows.FlowTheme import FlowTheme_Toy, FlowTheme_DarkTron, FlowTheme_Ghost, FlowTheme_Blender, \
    FlowTheme_Simple, FlowTheme_Ueli, FlowTheme_PureDark, FlowTheme, FlowTheme_PureLight, \
    FlowTheme_Colorful, FlowTheme_ColorfulLight, FlowTheme_Industrial, FlowTheme_Fusion
from .utils import get_resource


class Design(QObject):
    """Design serves as a container for the stylesheet and flow themes, and sends signals to notify GUI elements
    on change of the flow theme. A configuration for the flow themes can be loaded from a json file."""

    global_stylesheet = ''

    flow_theme_changed = Signal(str)
    performance_mode_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.flow_themes = []
        self.flow_theme: FlowTheme = None
        self.default_flow_size = None
        self.performance_mode: str = None
        self.node_item_shadows_enabled: bool = None
        self.animations_enabled: bool = None
        self.node_selection_stylesheet: str = None

        # load standard default values
        self.register_flow_themes()
        self._default_flow_theme = self.flow_themes[-1]
        self.set_performance_mode('pretty')
        self.set_animations_enabled(True)
        self.default_flow_size = [1000, 700]
        self.set_flow_theme(self._default_flow_theme)

    @staticmethod
    def register_fonts():
        db = QFontDatabase()
        db.addApplicationFont(
            str(get_resource('fonts/poppins/Poppins-Medium.ttf'))
        )
        db.addApplicationFont(
            str(get_resource('fonts/source_code_pro/SourceCodePro-Regular.ttf'))
        )
        db.addApplicationFont(
            str(get_resource('fonts/asap/Asap-Regular.ttf'))
        )

    def register_flow_themes(self):
        self.flow_themes = [
            FlowTheme_Toy(),
            FlowTheme_DarkTron(),
            FlowTheme_Ghost(),
            FlowTheme_Blender(),
            FlowTheme_Simple(),
            FlowTheme_Ueli(),
            FlowTheme_PureDark(),
            FlowTheme_Colorful(),
            FlowTheme_PureLight(),
            FlowTheme_ColorfulLight(),
            FlowTheme_Industrial(),
            FlowTheme_Fusion(),
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

        if 'init animations enabled' in IMPORT_DATA:
            self.set_animations_enabled(IMPORT_DATA['init animations enabled'])

        if 'default flow size' in IMPORT_DATA:
            self.default_flow_size = IMPORT_DATA['default flow size']

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

        self.node_selection_stylesheet = self.flow_theme.build_node_selection_stylesheet()

        self.flow_theme_changed.emit(self.flow_theme.name)


    def set_performance_mode(self, new_mode: str):
        self.performance_mode = new_mode
        if new_mode == 'fast':
            self.node_item_shadows_enabled = False
        else:
            self.node_item_shadows_enabled = True

        self.performance_mode_changed.emit(self.performance_mode)

    def set_animations_enabled(self, b: bool):
        self.animations_enabled = b

    def set_node_item_shadows(self, b: bool):
        self.node_item_shadows_enabled = b





# default_node_selection_stylesheet = '''
# '''

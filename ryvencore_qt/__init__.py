
# package path
import os
from .src.GlobalAttributes import Location
Location.PACKAGE_PATH = os.path.normpath(os.path.dirname(__file__))


from .src.ryvencore import *


from .src.WidgetBaseClasses import MWB, IWB
from .src.ConnectionItem import DataConnectionItem, ExecConnectionItem


class GUI:

    # list widgets
    from .src.conv_gui.VariablesListWidget import VariablesListWidget as VarsList
    from .src.conv_gui.ScriptsListWidget import ScriptsListWidget as ScriptsList

    # logging
    from .src.conv_gui.LogWidget import LogWidget

    # input widgets
    from .src.PortItemInputWidgets import RCIW_BUILTIN_LineEdit
    from .src.PortItemInputWidgets import RCIW_BUILTIN_LineEdit_small
    from .src.PortItemInputWidgets import RCIW_BUILTIN_SpinBox


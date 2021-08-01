
# package path
import os
from .src.GlobalAttributes import Location
Location.PACKAGE_PATH = os.path.normpath(os.path.dirname(__file__))

# set ryvencore gui mode
os.environ['RC_MODE'] = 'gui'

# backend imports
from .src.ryvencore import InfoMsgs, NodeInputBP, NodeOutputBP, ExecConnection, LogsManager, dtypes
# Note: Node and DataConnection are subclassed by ryvencore-qt and imported below

# front end ...
from .src.Node import Node
from .src.Session import Session
from .src.WRAPPERS import DataConnection
from .src.WidgetBaseClasses import MWB, IWB
from .src.ConnectionItem import DataConnectionItem, ExecConnectionItem


class GUI:

    # list widgets
    from .src.conv_gui.VariablesListWidget import VariablesListWidget as VarsList
    from .src.conv_gui.ScriptsListWidget import ScriptsListWidget as ScriptsList

    # logging
    from .src.conv_gui.LogWidget import LogWidget


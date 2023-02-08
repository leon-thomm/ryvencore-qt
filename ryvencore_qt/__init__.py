
# set package path (for resources etc.)
import os
from .src.GlobalAttributes import Location
Location.PACKAGE_PATH = os.path.normpath(os.path.dirname(__file__))

# set ryvencore gui mode
os.environ['RC_MODE'] = 'gui'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

# import backend wrapper
from .src.core_wrapper import *

# import frontend
from .src.flows.nodes.WidgetBaseClasses import MWB, IWB
from .src.flows.connections.ConnectionItem import DataConnectionItem, ExecConnectionItem
from .src.widgets import *
from .src.flows.FlowTheme import flow_themes

# expose ryvencore
import ryvencore

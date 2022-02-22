
# set package path (for resources etc.)
import pathlib
from .src.GlobalAttributes import Location
Location.PACKAGE_PATH = pathlib.PurePath(__file__).parent

# set ryvencore gui mode
import os
os.environ['RC_MODE'] = 'gui'

# import backend wrapper
from .src.core_wrapper import *

# import frontend
from .src.flows.nodes.WidgetBaseClasses import MWB, IWB
from .src.flows.connections.ConnectionItem import DataConnectionItem, ExecConnectionItem
from .src.conv_gui import *

# expose ryvencore
import ryvencore

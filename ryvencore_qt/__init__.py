
# set package path (for resources, packages, saves, etc.)
import os
from .src.GlobalAttributes import Location
Location.PACKAGE_PATH = os.path.normpath(os.path.dirname(__file__))

# set ryvencore gui mode
os.environ['RC_MODE'] = 'gui'

# import backend
from .src.core_wrapper import *

# import frontend
from .src.WidgetBaseClasses import MWB, IWB
from .src.ConnectionItem import DataConnectionItem, ExecConnectionItem
from .src.conv_gui import *

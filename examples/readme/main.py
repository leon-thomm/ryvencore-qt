# Qt
import sys
import os
os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
from qtpy.QtWidgets import QMainWindow, QApplication

# ryvencore-qt
import ryvencore_qt as rc
from nodes import export_nodes


if __name__ == "__main__":

    # first, we create the Qt application and a window
    app = QApplication()
    mw = QMainWindow()

    # now we initialize a new ryvencore-qt session
    session = rc.Session()
    session.design.set_flow_theme(name='pure light')  # setting the design theme

    # and register our nodes and create a script
    session.register_nodes(export_nodes)

    # to get a flow where we can place nodes, we need to crate a new script
    script = session.create_script('hello world', flow_view_size=[800, 500])

    # getting the flow widget of the newly created script
    flow_view = session.flow_views[script]
    mw.setCentralWidget(flow_view)  # and show it in the main window

    # finally, show the window and run the application
    mw.show()
    sys.exit(app.exec_())
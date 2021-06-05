import ryvencore_qt as rc
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget

# nodes.py is defined below
from nodes import SignalNode, ANDGateNode, ORGateNode, NANDGateNode, NORGateNode, NOTGateNode, XORGateNode, LEDNode, \
    NodeBase


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # if I wanted to make all ryvencore-internally defined nodes 
        # (like function nodes) also inherit from our NodeBase, I'd provide 
        # it as node_class parameter here, but I dont want that in this case
        self.session = rc.Session()

        # some design specs
        self.session.design.set_flow_theme(name='pure light')
        self.session.design.set_performance_mode('pretty')

        # registering the nodes
        self.session.register_nodes(
            [
                SignalNode,
                ANDGateNode,
                ORGateNode,
                NANDGateNode,
                NORGateNode,
                NOTGateNode,
                XORGateNode,
                LEDNode,
            ]
        )
        self.script = self.session.create_script(title='main')
        view = self.session.flow_views[self.script]

        # creating a widget and adding the flow view of the script
        w = QWidget()
        w.setLayout(QHBoxLayout())
        w.layout().addWidget(view)

        self.setCentralWidget(w)
        self.resize(1500, 800)  # resizing the window


if __name__ == '__main__':
    app = QApplication()

    mw = MainWindow()
    mw.show()

    sys.exit(app.exec_())
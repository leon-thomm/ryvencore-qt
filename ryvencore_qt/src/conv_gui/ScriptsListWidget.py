from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QScrollArea

from .ScriptsList_ScriptWidget import ScriptsList_ScriptWidget


class ScriptsListWidget(QWidget):
    """Convenience class for a QWidget to easily manage the scripts of a session."""

    def __init__(self, session):
        super().__init__()

        self.session = session
        self.list_widgets = []
        self.ignore_name_line_edit_signal = False  # because disabling causes firing twice otherwise

        self.setup_UI()

        self.session.flow_view_created.connect(self.add_new_script)
        self.session.script_deleted.connect(self.recreate_list)


    def setup_UI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        # list scroll area

        self.list_scroll_area = QScrollArea(self)
        self.list_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_scroll_area.setWidgetResizable(True)
        self.list_scroll_area.setContentsMargins(0, 0, 0, 0)

        self.scroll_area_widget = QWidget()
        self.scroll_area_widget.setContentsMargins(0, 0, 0, 0)
        self.list_scroll_area.setWidget(self.scroll_area_widget)

        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area_widget.setLayout(self.list_layout)

        self.layout().addWidget(self.list_scroll_area)

        # line edit

        self.new_script_title_lineedit = QLineEdit()
        self.new_script_title_lineedit.setPlaceholderText('new script\'s title')
        self.new_script_title_lineedit.returnPressed.connect(self.create_script)

        main_layout.addWidget(self.new_script_title_lineedit)


        self.recreate_list()


    def recreate_list(self):
        # remove script widgets
        for i in reversed(range(self.list_layout.count())):
            self.list_layout.itemAt(i).widget().setParent(None)

        self.list_widgets.clear()

        for s in self.session.scripts:
            new_widget = ScriptsList_ScriptWidget(self, self.session, s)
            self.list_widgets.append(new_widget)

        for w in self.list_widgets:
            self.list_layout.addWidget(w)

    def create_script(self):
        title = self.new_script_title_lineedit.text()

        if self.session.script_title_valid(title):
            self.session.create_script(title=title)

    def add_new_script(self, script, flow_view):
        self.recreate_list()

    def del_script(self, script, script_widget):
        msg_box = QMessageBox(QMessageBox.Warning, 'sure about deleting script?',
                              'You are about to delete a script. This cannot be undone, all content will be lost. '
                              'Do you want to continue?', QMessageBox.Cancel | QMessageBox.Yes, self)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        ret = msg_box.exec_()
        if ret != QMessageBox.Yes:
            return

        self.list_widgets.remove(script_widget)
        script_widget.setParent(None)
        self.session.delete_script(script)
        # self.recreate_list()

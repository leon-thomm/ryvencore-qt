from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QScrollArea

from .ScriptsList_ScriptWidget import ScriptsList_ScriptWidget


class ScriptsListWidget(QWidget):
    """Convenience class for a QWidget to easily manage the scripts of a session."""

    # TODO: scroll area

    def __init__(self, session, parent=None):
        super(ScriptsListWidget, self).__init__(parent=parent)

        self.session = session
        self.session.script_flow_view_created.connect(self.add_new_script)

        self.list_widgets = []
        self.ignore_name_line_edit_signal = False  # because disabling causes firing twice otherwise

        self.setup_UI()


    def setup_UI(self):
        main_layout = QVBoxLayout()

        self.list_layout = QVBoxLayout()
        self.list_layout.setAlignment(Qt.AlignTop)

        # list scroll area

        self.list_scroll_area = QScrollArea()
        self.list_scroll_area.setWidgetResizable(True)
        self.list_scroll_area.setContentsMargins(0, 0, 0, 0)

        w = QWidget()
        w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(self.list_layout)

        self.list_scroll_area.setWidget(w)

        main_layout.addWidget(self.list_scroll_area)

        # ------------------

        # controls

        self.new_script_title_lineedit = QLineEdit()
        self.new_script_title_lineedit.setPlaceholderText('new script\'s title')
        self.new_script_title_lineedit.returnPressed.connect(self.new_script_LE_return_pressed)

        main_layout.addWidget(self.new_script_title_lineedit)

        buttons_layout = QHBoxLayout()

        create_function_button = QPushButton('func')
        create_function_button.clicked.connect(self.on_create_function_clicked)
        buttons_layout.addWidget(create_function_button)

        create_script_button = QPushButton('script')
        create_script_button.clicked.connect(self.on_create_script_clicked)
        buttons_layout.addWidget(create_script_button)

        main_layout.addLayout(buttons_layout)

        # ------------------

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.recreate_list()


    def recreate_list(self):
        for w in self.list_widgets:
            w.hide()
            del w

        self.list_widgets.clear()

        for s in self.session.all_scripts():
            new_widget = ScriptsList_ScriptWidget(self, self.session, s)
            self.list_widgets.append(new_widget)

        self.rebuild_list()


    def rebuild_list(self):
        # for i in range(self.layout().count()):
        #     self.list_layout.removeItem(self.layout().itemAt(0))

        for w in self.list_widgets:
            self.list_layout.addWidget(w)


    def new_script_LE_return_pressed(self):
        self.create_script()  # create normal scripts by default

    def on_create_function_clicked(self):
        self.create_function_script()

    def on_create_script_clicked(self):
        self.create_script()

    def create_function_script(self):
        title = self.new_script_title_lineedit.text()

        if self.session.script_title_valid(title):
            self.session.create_func_script(title=title)

    def create_script(self):
        title = self.new_script_title_lineedit.text()

        if self.session.script_title_valid(title):
            self.session.create_script(title=title)


    def add_new_script(self, script):
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
        self.recreate_list()

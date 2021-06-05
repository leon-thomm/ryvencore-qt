from qtpy.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QScrollArea
from qtpy.QtCore import Qt

from .VarsList_VarWidget import VarsList_VarWidget


class VariablesListWidget(QWidget):
    """Convenience class for a QWidget to easily manage script variables of a script."""

    def __init__(self, vars_manager):
        super(VariablesListWidget, self).__init__()

        self.vars_manager = vars_manager
        self.vars_manager.new_var_created.connect(self.add_new_var)
        self.widgets = []
        self.currently_edited_var = ''
        self.ignore_name_line_edit_signal = False  # because disabling causes firing twice otherwise
        # self.data_type_line_edits = []  # same here

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

        self.new_var_name_lineedit = QLineEdit()
        self.new_var_name_lineedit.setPlaceholderText('new var\'s title')
        self.new_var_name_lineedit.returnPressed.connect(self.new_var_LE_return_pressed)

        main_layout.addWidget(self.new_var_name_lineedit)

        # ------------------

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.recreate_list()


    def recreate_list(self):
        for w in self.widgets:
            w.hide()
            del w

        self.widgets.clear()
        # self.data_type_line_edits.clear()

        for v in self.vars_manager.variables:
            new_widget = VarsList_VarWidget(self, self.vars_manager, v)
            # new_widget.name_LE_editing_finished.connect(self.name_line_edit_editing_finished)
            self.widgets.append(new_widget)

        self.rebuild_list()


    def rebuild_list(self):
        for i in range(self.list_layout.count()):
            self.list_layout.removeItem(self.list_layout.itemAt(0))

        for w in self.widgets:
            self.list_layout.addWidget(w)


    def new_var_LE_return_pressed(self):
        name = self.new_var_name_lineedit.text()

        if not self.vars_manager.var_name_valid(name=name):
            return

        self.vars_manager.create_new_var(name=name)


    def add_new_var(self, var):
        self.recreate_list()


    # def name_line_edit_editing_finished(self):
    #     var_widget: VarsList_VarWidget = self.sender()
    #     var_widget.name_line_edit.setEnabled(False)
    #
    #     # search for name issues
    #     new_var_name = var_widget.name_line_edit.text()
    #     for v in self.vars_manager.variables:
    #         if v.name == new_var_name:
    #             var_widget.name_line_edit.setText(self.currently_edited_var.name)
    #             return
    #
    #     var_widget.var.name = new_var_name


    def del_variable(self, var, var_widget):
        self.widgets.remove(var_widget)
        var_widget.setParent(None)
        self.vars_manager.delete_var(var)
        # del self.vars_manager.variables[self.vars_manager.variables.index(var)]
        self.recreate_list()
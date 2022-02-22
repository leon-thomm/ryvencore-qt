from qtpy.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QAction
from qtpy.QtGui import QIcon, QDrag
from qtpy.QtCore import QMimeData, Qt, QEvent, QByteArray

import json

from .ListWidget_NameLineEdit import ListWidget_NameLineEdit
from ..utils import shorten, get_resource
from .EditVal_Dialog import EditVal_Dialog


class VarsList_VarWidget(QWidget):
    """A QWidget representing a single script variable for the VariablesListWidget."""

    def __init__(self, vars_list_widget, vars_manager, var):
        super().__init__()

        self.vars_manager = vars_manager
        self.var = var
        self.vars_list_widget = vars_list_widget
        self.previous_var_name = ''  # for editing

        self.ignore_name_line_edit_signal = False


        # UI

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # create icon

        variable_icon = QIcon(get_resource('pics/variable_picture.png'))

        icon_label = QLabel()
        icon_label.setFixedSize(15, 15)
        icon_label.setStyleSheet('border:none;')
        icon_label.setPixmap(variable_icon.pixmap(15, 15))
        main_layout.addWidget(icon_label)

        #   name line edit

        self.name_line_edit = ListWidget_NameLineEdit(var.name, self)
        self.name_line_edit.setPlaceholderText('name')
        self.name_line_edit.setEnabled(False)
        self.name_line_edit.editingFinished.connect(self.name_line_edit_editing_finished)

        main_layout.addWidget(self.name_line_edit)

        self.setLayout(main_layout)



    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.name_line_edit.geometry().contains(event.pos()):
                self.name_line_edit_double_clicked()
                return


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            data_text = self.get_drag_data()
            data = QByteArray(bytes(data_text, 'utf-8'))
            mime_data.setData('text/plain', data)
            drag.setMimeData(mime_data)
            drop_action = drag.exec_()
            return


    def event(self, event):
        if event.type() == QEvent.ToolTip:
            val_str = ''
            try:
                val_str = str(self.var.val)
            except Exception as e:
                val_str = "couldn't stringify value"
            self.setToolTip('val type: '+str(type(self.var.val))+'\nval: '+shorten(val_str, 3000, line_break=True))

        return QWidget.event(self, event)


    def contextMenuEvent(self, event):
        menu: QMenu = QMenu(self)

        delete_action = QAction('delete')
        delete_action.triggered.connect(self.action_delete_triggered)

        edit_value_action = QAction('edit value')
        edit_value_action.triggered.connect(self.action_edit_val_triggered)

        actions = [delete_action, edit_value_action]
        for a in actions:
            menu.addAction(a)

        menu.exec_(event.globalPos())


    def action_delete_triggered(self):
        self.vars_list_widget.del_variable(self.var, self)


    def action_edit_val_triggered(self):
        edit_var_val_dialog = EditVal_Dialog(self, self.var.val)
        accepted = edit_var_val_dialog.exec_()
        if accepted:
            self.vars_manager.set_var(self.var.name, edit_var_val_dialog.get_val())


    def name_line_edit_double_clicked(self):
        self.name_line_edit.setEnabled(True)
        self.name_line_edit.setFocus()
        self.name_line_edit.selectAll()

        self.previous_var_name = self.name_line_edit.text()


    def get_drag_data(self):
        data = {'type': 'variable',
                'name': self.var.name,
                'value': self.var.val}  # value is probably unnecessary
        data_text = json.dumps(data)
        return data_text


    def name_line_edit_editing_finished(self):
        if self.ignore_name_line_edit_signal:
            return

        name = self.name_line_edit.text()

        self.ignore_name_line_edit_signal = True

        if self.vars_manager.var_name_valid(name):
            self.var.name = name
        else:
            self.name_line_edit.setText(self.previous_var_name)

        self.name_line_edit.setEnabled(False)
        self.ignore_name_line_edit_signal = False

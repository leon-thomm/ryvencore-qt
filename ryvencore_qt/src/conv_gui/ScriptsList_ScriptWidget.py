from qtpy.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QAction
from qtpy.QtGui import QIcon, QImage
from qtpy.QtCore import Qt, QEvent, QBuffer, QByteArray

from ..GlobalAttributes import Location
from .ListWidget_NameLineEdit import ListWidget_NameLineEdit


class ScriptsList_ScriptWidget(QWidget):
    """A QWidget representing a single Script for the ScriptsListWidget."""

    def __init__(self, scripts_list_widget, session, script):
        super().__init__()

        self.session = session
        self.script = script
        self.flow_view = self.session.flow_views[script]
        self.scripts_list_widget = scripts_list_widget
        self.previous_script_title = ''
        self._thumbnail_source = ''
        self.ignore_title_line_edit_signal = False


        # UI

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        #   create icon

        script_icon = QIcon(Location.PACKAGE_PATH + '/resources/pics/script_picture.png')

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setStyleSheet('border:none;')
        icon_label.setPixmap(script_icon.pixmap(20, 20))
        main_layout.addWidget(icon_label)

        #   title line edit

        self.title_line_edit = ListWidget_NameLineEdit(script.title, self)
        self.title_line_edit.setPlaceholderText('title')
        self.title_line_edit.setEnabled(False)
        self.title_line_edit.editingFinished.connect(self.title_line_edit_editing_finished)

        main_layout.addWidget(self.title_line_edit)

        self.setLayout(main_layout)



    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.title_line_edit.geometry().contains(event.pos()):
                self.title_line_edit_double_clicked()
                return


    def event(self, event):
        if event.type() == QEvent.ToolTip:

            # generate preview img as QImage
            img: QImage = self.flow_view.get_viewport_img().scaledToHeight(200)

            # store the img data in QBuffer to load it directly from memory
            buffer = QBuffer()
            img.save(buffer, 'PNG')

            # generate html from data in memory
            html = f"<img src='data:image/png;base64, { bytes( buffer.data().toBase64() ).decode() }'>"

            # show tooltip
            self.setToolTip(html)

        return QWidget.event(self, event)


    def contextMenuEvent(self, event):
        menu: QMenu = QMenu(self)

        delete_action = QAction('delete')
        delete_action.triggered.connect(self.action_delete_triggered)

        actions = [delete_action]
        for a in actions:
            menu.addAction(a)

        menu.exec_(event.globalPos())


    def action_delete_triggered(self):
        self.scripts_list_widget.del_script(self.script, self)


    def title_line_edit_double_clicked(self):
        self.title_line_edit.setEnabled(True)
        self.title_line_edit.setFocus()
        self.title_line_edit.selectAll()

        self.previous_script_title = self.title_line_edit.text()


    def title_line_edit_editing_finished(self):
        if self.ignore_title_line_edit_signal:
            return

        title = self.title_line_edit.text()

        self.ignore_title_line_edit_signal = True

        if self.session.script_title_valid(title):
            self.session.rename_script(script=self.script, title=title)
        else:
            self.title_line_edit.setText(self.previous_script_title)

        self.title_line_edit.setEnabled(False)
        self.ignore_title_line_edit_signal = False

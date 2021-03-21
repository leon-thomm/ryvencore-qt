from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Signal


class ListWidget_NameLineEdit(QLineEdit):

    unfocused = Signal()

    def __init__(self, text, parent):
        super(ListWidget_NameLineEdit, self).__init__(text, parent)


    def focusOutEvent(self, arg__1):
        self.unfocused.emit()
        QLineEdit.focusOutEvent(self, arg__1)
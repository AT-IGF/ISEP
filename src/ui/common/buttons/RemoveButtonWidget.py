from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QApplication

from src.ui.dataViewer import Signal


def get_pollen_types(listWidget):
    return [str(listWidget.item(i).text()) for i in range(listWidget.count())]


class RemoveButtonWidget(QPushButton):
    value_changed = pyqtSignal(object)

    def __init__(self, types_signal: Signal, listWidget, width=None):
        super().__init__()
        self.app = QApplication.instance()
        self.setText("Remove")
        listWidget.itemSelectionChanged.connect(
            lambda: self.set_state(len(listWidget.selectedItems()) > 0)
        )
        self.clicked.connect(lambda: self.on_click(listWidget))
        self.setEnabled(False)
        if width != None:
            self.setFixedWidth(width)
        self.value_changed.connect(lambda value: types_signal.value_changed.emit(value))

    def set_state(self, value):
        self.setEnabled(value)

    def on_click(self, listWidget):
        [listWidget.takeItem(listWidget.row(x)) for x in listWidget.selectedItems()]
        value = get_pollen_types(listWidget)
        self.value_changed.emit(value)

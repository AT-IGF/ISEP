from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton

import copy
from src.ui.dataViewer import Signal


class ResetButtonWidget(QPushButton):
    value_changed = pyqtSignal(object)

    def __init__(self, types_signal: Signal, listWidget, width=None):
        super().__init__()
        self.value_original = copy.deepcopy(types_signal.value)
        types_signal.value_changed.connect(lambda value: self.set_state(value))

        self.setText("⟲")
        self.setToolTip("reset")
        if width != None:
            self.setFixedWidth(width)
        self.clicked.connect(lambda: self.on_click(listWidget))
        self.set_state(self.value_original)
        self.value_changed.connect(lambda value: types_signal.value_changed.emit(value))

    def set_state(self, value):
        self.setEnabled(value != self.value_original)

    def on_click(self, listWidget):
        listWidget.clear()
        listWidget.addItems(self.value_original)
        self.value_changed.emit(self.value_original)

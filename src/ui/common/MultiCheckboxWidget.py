from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QCheckBox

from src.ui.dataViewer import SettingsSignals


class MultiCheckboxWidget(QWidget):
    value_changed = pyqtSignal(object)

    def __init__(
        self, options, singals: SettingsSignals, preselected=None, parent=None
    ):
        super().__init__(parent)
        self.options = [
            (label, value) for opt in options for label, value in opt.items()
        ]

        self.singals = singals
        self.preselected = set(preselected or [])
        self.checkboxes = []

        layout = QHBoxLayout(self)
        for label, value in self.options:
            cb = QCheckBox(label, self)
            cb.setChecked(value in self.preselected)
            cb.stateChanged.connect(self.on_state_change)
            layout.addWidget(cb)
            self.checkboxes.append((cb, value))

        self._values = self.checked_values()
        self.values_original = self.checked_values()

        self.setLayout(layout)

    def on_state_change(self, state):
        self.values = self.checked_values()
        self.singals.value_changed.emit(
            self, sorted(self.checked_values()) != sorted(self.values_original)
        )

    def checked_key_values(self):
        return {cb.text(): val for cb, val in self.checkboxes if cb.isChecked()}

    def checked_values(self):
        return [val for cb, val in self.checkboxes if cb.isChecked()]

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value):
        self._values = value

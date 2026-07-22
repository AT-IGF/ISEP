from dataclasses import dataclass
from PyQt5.QtCore import pyqtSignal


@dataclass
class SettingsSignals:
    value_changed: pyqtSignal | None = None
    show_modal: pyqtSignal | None = None
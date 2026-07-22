from dataclasses import dataclass
from PyQt5.QtCore import pyqtSignal


@dataclass
class Signal:
    value: object
    value_changed: pyqtSignal | None = None
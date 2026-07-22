# path_signal_bus.py
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    path_changed = pyqtSignal(str)
    general_types_saved = pyqtSignal(object)


signal_bus = SignalBus()

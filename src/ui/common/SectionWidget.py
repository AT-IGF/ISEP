from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel

from src.ui.common import HrWidget


class SectionWidget(QWidget):
    def __init__(self, label: str, tooltip=None, margins=None):
        super().__init__()

        label = QLabel(label)
        hr_widget = HrWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 0)
        if margins != None:
            layout.setContentsMargins(*margins)

        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addWidget(hr_widget)
        self.setLayout(layout)

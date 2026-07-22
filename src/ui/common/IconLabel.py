import qtawesome as qta
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize, QEvent
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel

from src.ui.common.Tooltip import Tooltip


class IconLabel(QWidget):
    HorizontalSpacing = 1

    def __init__(
        self,
        qta_id,
        text=None,
        final_stretch=True,
        tooltip=None,
        color=QColor | str,
        size=20,
    ):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.icon = QLabel()
        icon_size = QSize(size, size)
        self.icon.setPixmap(qta.icon(qta_id, color=color).pixmap(icon_size))
        if tooltip != None and tooltip != "":
            self.icon.installEventFilter(Tooltip(tooltip, parent=self))

        layout.addWidget(self.icon)
        layout.addSpacing(self.HorizontalSpacing)
        layout.addWidget(QLabel(text))

        if final_stretch:
            layout.addStretch(1)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def update_tooptip(self, tooltip: str):
        self.setToolTip(tooltip)

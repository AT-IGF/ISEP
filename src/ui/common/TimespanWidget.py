from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize, QEvent
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel

from src.common import Consts
from src.ui.common.Tooltip import Tooltip
from src.ui.common import LabelValueWidget


class TimespanWidget(QWidget):
    HorizontalSpacing = 1

    def __init__(self, signals, days, hours, minutes, seconds, margins=None):
        super().__init__()
        self.days_widget = LabelValueWidget(
            "",
            days,
            signals,
            val_type=int,
            suffix_label="day(s)",
            tooltip="",
            width=50,
            margins=(0, 0, 0, 0),
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.hours_widget = LabelValueWidget(
            "",
            hours,
            signals,
            val_type=int,
            suffix_label="hour(s)",
            tooltip="",
            width=50,
            margins=(0, 0, 0, 0),
            bottom=0,
            top=23,
        )

        self.minutes_widget = LabelValueWidget(
            "",
            minutes,
            signals,
            val_type=int,
            suffix_label="minute(s)",
            tooltip="",
            width=50,
            margins=(0, 0, 0, 0),
            bottom=0,
            top=59,
        )

        self.seconds_widget = LabelValueWidget(
            "",
            seconds,
            signals,
            val_type=int,
            suffix_label="second(s)",
            tooltip="",
            width=50,
            margins=(0, 0, 0, 0),
            bottom=0,
            top=59,
        )

        layoutH = QHBoxLayout()
        layoutH.addWidget(self.days_widget)
        layoutH.addWidget(self.hours_widget)
        layoutH.addWidget(self.minutes_widget)
        layoutH.addWidget(self.seconds_widget)
        layoutH.setSpacing(0)
        layoutH.addStretch(1)
        layoutH.setContentsMargins(10, 0, 0, 0)
        if margins == None:
            layoutH.setContentsMargins(*margins)

        self.setLayout(layoutH)

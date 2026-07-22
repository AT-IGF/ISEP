from datetime import datetime
from functools import partial
from src.ui.common.General import set_style_sheet
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListWidget,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDateTimeEdit,
)
from PyQt5.QtCore import QDateTime

from src.ui.common import MeasurementWidget
from src.ui.dataViewer import SettingsSignals


class DateTimePickerWidget(QWidget):
    def __init__(self, signals: SettingsSignals, date_time: datetime | None):
        super().__init__()
        self._value = date_time

        self.picker_widget = QDateTimeEdit()
        self.picker_widget.setCalendarPopup(True)
        if self._value is None:
            self.picker_widget.setDateTime(QDateTime.currentDateTime())
        else:
            self.picker_widget.setDateTime(self._value)
        self.picker_widget.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        self.picker_widget.dateTimeChanged.connect(
            lambda dt: signals.value_changed.emit(self, dt != date_time)
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layout.addWidget(self.picker_widget)
        self.setLayout(layout)

    @property
    def value(self) -> str | datetime:
        return self.picker_widget.dateTime().toPyDateTime()

    @value.setter
    def value(self, value):
        self._value = value


class DateTimePickerOptionWidget(QWidget):
    def __init__(
        self,
        signals,
        date_time: datetime | None,
        label: str,
        layout: str = "Horizontal",
        margins=None,
    ):
        super().__init__()
        self._value = date_time
        self._value_original = date_time
        self.picker = DateTimePickerWidget(signals, date_time)

        self.option_widget = MeasurementWidget(
            self._value is not None,
            label=label,
            value_changed=signals.value_changed,
            children=[self.picker],
            layout=layout,
            margins=margins,
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layout.addWidget(self.option_widget)
        self.setLayout(layout)

    @property
    def value(self) -> datetime | None:
        if self.option_widget.is_checked():
            return self.picker.value
        else:
            return None

    @value.setter
    def value(self, value):
        self._value = value

    def value_str(self, value_format: str | None = None) -> str:

        if value_format == None:
            return self.value.isoformat()
        if not isinstance(value_format, str):
            raise ValueError(
                f"Datetime parse value format should be str, value_format_type={type(value_format)} value_format={value_format}"
            )
        picker_value = self.value
        if picker_value is None:
            return None
        else:
            return self.value.strftime(value_format)

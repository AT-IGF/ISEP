from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtCore import QDateTime

from src.common.config import Config
from src.common.config.configs import PredictionsMapperConfig

from src.ui.common import (
    TimespanWidget,
    LabelValueWidget,
    MeasurementWidget,
)
from src.ui.common import LayoutWidget, DateTimePickerOptionWidget


class SplitTimespanWidget(QWidget):
    def __init__(self, signals):
        super().__init__()
        self.current_config = Config.get(PredictionsMapperConfig)
        config = Config.get(PredictionsMapperConfig)
        self._value = config.split_timespan
        self._value_original = config.split_timespan

        self.timestamp_column_name_widget = LabelValueWidget(
            "Timestamp column name:",
            self._value.timestamp_column_name,
            signals,
            val_type=str,
            tooltip="Name of the column containing time of the measurement.",
            margins=(10, 10, 0, 0),
            bottom=0,
            top=1,
        )

        self.picker_from_option = DateTimePickerOptionWidget(
            signals=signals,
            date_time=self._value.range_from,
            label="From",
            margins=(10, 0, 0, 0),
        )
        self.picker_to_option = DateTimePickerOptionWidget(
            signals=signals,
            date_time=self._value.range_to,
            label="To",
            margins=(10, 0, 0, 0),
        )
        picker_layout = LayoutWidget(
            children=[self.picker_from_option, self.picker_to_option],
            layout_type="H",
            margins=(10, 10, 0, 0),
            label_tooltip=(
                "Date time range:",
                "Range between which data will be processed<br/><b>Note</b>: file to process due to its text character will be read as a whole, range will be applied for further steps",
            ),
        )

        self.timespan_widget = TimespanWidget(
            signals=signals,
            days=self._value.days,
            hours=self._value.hours,
            minutes=self._value.minutes,
            seconds=self._value.seconds,
            margins=(0, 0, 0, 0),
        )

        self.split_timespan_widget = MeasurementWidget(
            self.is_timespan_set(self._value),
            label="Split by time span",
            tooltip="Group measurements into periods, if not selected each result will be shown separately.",
            value_changed=signals.value_changed,
            children=[self.timespan_widget],
            layout="Vertical",
            margins=(10, 10, 0, 0),
        )

        layoutV = QVBoxLayout()
        # layoutV.addWidget(self.timestamp_column_name_widget)
        layoutV.addWidget(picker_layout)
        layoutV.addWidget(self.split_timespan_widget)
        layoutV.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layoutV)

    def is_timespan_set(self, timespan):
        return not (
            timespan.days == 0
            and timespan.hours == 0
            and timespan.minutes == 0
            and timespan.seconds == 0
        )

    @property
    def value(self):
        self._value.timestamp_column_name = self.timestamp_column_name_widget.value
        self._value.days = self.timespan_widget.days_widget.value
        self._value.hours = self.timespan_widget.hours_widget.value
        self._value.minutes = self.timespan_widget.minutes_widget.value
        self._value.seconds = self.timespan_widget.seconds_widget.value
        self._value.range_from = self.picker_from_option.value_str("%Y-%m-%d %H:%M:%S")
        self._value.range_to = self.picker_to_option.value_str("%Y-%m-%d %H:%M:%S")

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

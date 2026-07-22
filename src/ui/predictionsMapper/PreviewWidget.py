from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)


from src.common.config import Config
from src.common.config.configs import PredictionsMapperConfig

from src.ui.common import (
    LabelValueWidget,
    DirectorySelectorWidget,
)
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common import MeasurementWidget


class PreviewWidget(QWidget):
    def __init__(self, signals):
        super().__init__()
        self.current_config = Config.get(PredictionsMapperConfig)
        config = Config.get(PredictionsMapperConfig)
        self._value = config.preview
        self._value_original = config.preview

        self.keep_every_nth_row_widget = LabelValueWidget(
            "Sample interval:",
            self._value.keep_every_nth_row,
            signals,
            val_type=int | None,
            tooltip="Keep every n-th line of processed file. Allows to reduce number of processed samples for the 'quick-looks'",
            width=50,
            margins=(10, 5, 0, 0),
            bottom=0,
        )

        self.preview_widget = MeasurementWidget(
            self._value.keep_every_nth_row is not None,
            label="Preview settings",
            value_changed=signals.value_changed,
            children=[self.keep_every_nth_row_widget],
            layout="Vertical",
            margins=(0, 0, 0, 0),
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.preview_widget)
        layoutV.setContentsMargins(10, 15, 0, 0)
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        if self.preview_widget.is_checked():
            self._value.keep_every_nth_row = self.keep_every_nth_row_widget.value
        else:
            self._value.keep_every_nth_row = None

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

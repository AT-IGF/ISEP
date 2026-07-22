from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.common.config.configs.models.dataViewer import (
    SizeModel,
    HistogramModel,
    PlotCombinedModel,
)
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.dataViewer.aggregatedSamples.common import HistogramWidget


class SizeWidget(QWidget):
    def __init__(self, config: SizeModel, singals: SettingsSignals):
        super().__init__()
        self.config = config

        layoutV_plots = QVBoxLayout()
        self.setLayout(layoutV_plots)

        self.histogram_widget = HistogramWidget(
            config=config.histogram,
            singals=singals,
            units="μm",
            hide=[HistogramWidget.AGGREGATION_FUNCTION],
        )

        self._value = SizeModel(histogram=self.histogram_widget.value)

        layoutV_plots.addWidget(self.histogram_widget)
        self.setLayout(layoutV_plots)

    @property
    def value(self):
        self._value.histogram = self.histogram_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.common.config.configs.models.dataViewer import (
    SpectrumModel,
    HistogramModel,
    PlotCombinedModel,
)
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import SectionWidget
from src.ui.dataViewer.aggregatedSamples.common import HistogramWidget, PlotWidget


class SpectrumWidget(QWidget):
    AGGREGATION_FUNCTION_TOOLTIP = "For every channel takes columns and does on it aggregation operation, where rows are considered as consecutive measurements and values in rows detectors outputs."

    def __init__(self, config: SpectrumModel, singals: SettingsSignals):
        super().__init__()
        self.config = config

        layoutV_plots = QVBoxLayout()
        self.setLayout(layoutV_plots)

        self.channels_widget = LabelValueWidget(
            "Channels",
            config.channels,
            singals,
            tooltip="Florescence spectral ranges measured after n nanoseconds interval, where intervals are described as:\
                <ul>\
                <li>1 - 0 nm</li>\
                <li>2 - 500 ns</li>\
                <li>3 - 1000 ns</li>\
                <li>4 - 1500 ns</li>\
                <li>5 - 2000 ns</li>\
                <li>6 - 2500 ns</li>\
                <li>7 - 3000 ns</li>\
                <li>8 - 3500 ns</li>\
                </ul>",
            val_type=list[int],
            margins=(10, 0, 0, 0),
            specific_vals=[1, 2, 3, 4, 5, 6, 7, 8],
        )

        self.histogram_widget = HistogramWidget(
            config=config.histogram,
            singals=singals,
            aggregation_function_tooltip=self.AGGREGATION_FUNCTION_TOOLTIP,
        )
        self.plot_widget = PlotWidget(config=config.plot_combined, singals=singals)

        self._value = SpectrumModel(
            channels=self.channels_widget.value,
            histogram=self.histogram_widget.value,
            plot_combined=self.plot_widget.value,
        )

        layoutV_plots.addWidget(self.channels_widget)
        layoutV_plots.addWidget(self.histogram_widget)
        layoutV_plots.addWidget(self.plot_widget)
        self.setLayout(layoutV_plots)

    @property
    def value(self):
        self._value.channels = self.channels_widget.value
        self._value.histogram = self.histogram_widget.value
        self._value.plot_combined = self.plot_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

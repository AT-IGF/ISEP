from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.common.config.configs.models.dataViewer import (
    LifetimeModel,
    HistogramModel,
    PlotCombinedModel,
)
from src.common.config.configs import AllParticlesAvgsConfig
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import SectionWidget
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.dataViewer.aggregatedSamples.common import HistogramWidget, PlotWidget


class LifetimeWidget(QWidget):
    AGGREGATION_FUNCTION_TOOLTIP = "For every channel measurement aggregation operation is done. E.g. max will take max value from sample measurement."

    def __init__(self, config: LifetimeModel, singals: SettingsSignals):
        super().__init__()
        self.config = config

        layoutV_plots = QVBoxLayout()
        self.setLayout(layoutV_plots)

        self.channels_widget = LabelValueWidget(
            "Channels",
            config.channels,
            singals,
            tooltip="Florescence lifetime bands to show, where bands are described as:\
                <ul>\
                <li>1 - 350-400 nm</li>\
                <li>2 - 420-460 nm</li>\
                <li>3 - 511-572 nm</li>\
                <li>4 - 672-800 nm</li>\
                </ul>\
                Example input: [1, 2]",
            val_type=list[int],
            margins=(10, 0, 0, 0),
            nullable=False,
            specific_vals=[1, 2, 3, 4],
        )
        self.histogram_widget = HistogramWidget(
            config=config.histogram,
            singals=singals,
            aggregation_function_tooltip=self.AGGREGATION_FUNCTION_TOOLTIP,
        )
        self.plot_widget = PlotWidget(config=config.plot_combined, singals=singals)

        self._value = LifetimeModel(
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

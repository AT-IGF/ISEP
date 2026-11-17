from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.HistogramModel import HistogramModel
from src.common.config.configs.models.dataViewer.PlotCombinedModel import (
    PlotCombinedModel,
)


@dataclass
class SpectrumModel:
    """Fluorescence spectrum plots, used when ``metric_to_process`` is ``spectrum``."""

    channels: list[int] = field(default_factory=lambda: [1])
    """Channels. Fluorescence spectra measured after successive 500 ns intervals, numbered from 1 to 8:
    1 - 0 ns, 2 - 500 ns, 3 - 1000 ns, ..., 8 - 3500 ns. A separate plot is created for every selected
    channel."""

    histogram: HistogramModel = field(default_factory=HistogramModel)
    plot_combined: PlotCombinedModel = field(default_factory=PlotCombinedModel)

    def is_histogram(self):
        return self.histogram != None and self.histogram.plot == True

    def is_plot_combined(self):
        return self.plot_combined != None and self.plot_combined.plot == True

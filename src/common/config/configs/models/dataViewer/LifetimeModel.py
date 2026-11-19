from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.HistogramModel import HistogramModel
from src.common.config.configs.models.dataViewer.PlotCombinedModel import (
    PlotCombinedModel,
)


@dataclass
class LifetimeModel:
    """Fluorescence lifetime plots, used when ``metric_to_process`` is ``lifetime``."""

    channels: list[int] = field(default_factory=lambda: [1])
    """Channels. Fluorescence lifetime bands to show, numbered from 1 to 4: 1 - 350-400 nm,
    2 - 420-460 nm, 3 - 511-572 nm, 4 - 672-800 nm. A separate plot is created for every selected band."""

    histogram: HistogramModel = field(default_factory=HistogramModel)
    plot_combined: PlotCombinedModel = field(default_factory=PlotCombinedModel)

    def is_histogram(self):
        return self.histogram != None and self.histogram.plot == True

    def is_plot_combined(self):
        return self.plot_combined != None and self.plot_combined.plot == True

from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.HistogramModel import HistogramModel
from src.common.config.configs.models.dataViewer.PlotCombinedModel import (
    PlotCombinedModel,
)


@dataclass
class LifetimeModel:
    channels: list[int] = field(default_factory=lambda: [1])
    histogram: HistogramModel = field(default_factory=HistogramModel)
    plot_combined: PlotCombinedModel = field(default_factory=PlotCombinedModel)

    def is_histogram(self):
        return self.histogram != None and self.histogram.plot == True

    def is_plot_combined(self):
        return self.plot_combined != None and self.plot_combined.plot == True

from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.HistogramModel import HistogramModel
from src.common.config.configs.models.dataViewer.PlotCombinedModel import (
    PlotCombinedModel,
)


@dataclass
class ScatteringModel:
    """Scattering image histogram, used when ``metric_to_process`` is ``scattering``."""

    histogram: HistogramModel = field(default_factory=HistogramModel)
    """Histogram of the scattering images. The aggregation function is applied to the whole image of every
    particle."""

    def is_histogram(self):
        return self.histogram != None and self.histogram.plot == True

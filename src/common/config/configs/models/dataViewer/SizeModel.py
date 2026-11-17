from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.HistogramModel import HistogramModel
from src.common.config.configs.models.dataViewer.PlotCombinedModel import (
    PlotCombinedModel,
)


@dataclass
class SizeModel:
    """Particle size histogram, used when ``metric_to_process`` is ``size``. The size is calculated from
    the scattering image and expressed in μm."""

    histogram: HistogramModel = field(default_factory=HistogramModel)
    """Histogram of particle sizes. The aggregation function is not used, since every particle has a single
    size value."""

    def is_histogram(self):
        return self.histogram != None and self.histogram.plot == True

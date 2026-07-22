from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.HistogramModel import HistogramModel
from src.common.config.configs.models.dataViewer.PlotCombinedModel import (
    PlotCombinedModel,
)


@dataclass
class SizeModel:
    histogram: HistogramModel = field(default_factory=HistogramModel)

    def is_histogram(self):
        return self.histogram != None and self.histogram.plot == True

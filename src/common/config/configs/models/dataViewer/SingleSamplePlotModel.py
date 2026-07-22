from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer.SingleSamplePlotModels.BoundariesModel import (
    BoundariesModel,
)


@dataclass()
class SingleSamplePlotModel:
    show: bool = False
    boundaries: BoundariesModel = field(default_factory=BoundariesModel)

    def is_within_range(self, value):
        if self.boundaries == None:
            return True
        if (
            self.boundaries.exclude_lower_than != None
            and value < self.boundaries.exclude_lower_than
        ):
            return False

        if (
            self.boundaries.exclude_higher_than != None
            and value > self.boundaries.exclude_higher_than
        ):
            return False

        return True

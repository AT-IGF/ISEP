from dataclasses import dataclass
from datetime import datetime

from src.common.predictions.ClassesMapper import prediction_to_classes
from src.common.predictions.models import ClassesMetadataModel, MappingType

@dataclass(frozen=True)
class Prediction:
    predictions: list[float]
    timestamp: datetime
    classes: list[str]
    
    def as_dict(self, mapping_type: MappingType = MappingType.PERCENTAGE):
        return prediction_to_classes(y_pred=self.predictions,
                                     classes=self.classes, 
                                     metadata=ClassesMetadataModel(timestamp=self.timestamp),
                                     mapping_type=mapping_type)
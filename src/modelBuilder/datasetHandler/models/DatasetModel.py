from dataclasses import dataclass
from datetime import datetime

from src.common.rawData.features.models import FeatureModel


@dataclass(frozen=True)
class DatasetModel:
    data_X: list[list[list[float]]]
    data_y: list[list[float]]
    sets_names: list[str]
    times: list[list[datetime]]
    types: set[str]
    feature_models: list[FeatureModel]
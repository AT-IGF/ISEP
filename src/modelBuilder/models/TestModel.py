from dataclasses import dataclass

from src.common.rawData.features.models.FeatureModel import FeatureModel


@dataclass(frozen=True)
class TestModel:
    X_test: list[list]
    y_test: list[list]
    times_test: list
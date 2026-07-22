from dataclasses import dataclass


@dataclass()
class LearningRateReducerModel:
    enabled: bool
    patience: int
    min_lr: float
    min_delta: float
    factor: float

from dataclasses import dataclass


@dataclass()
class EarlyStoppingModel:
    enabled: bool
    min_delta: float
    patience: int

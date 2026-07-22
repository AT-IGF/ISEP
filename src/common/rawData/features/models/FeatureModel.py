from dataclasses import dataclass
from datetime import datetime

from src.common.rawData.Signal import RawData


@dataclass(frozen=True)
class FeatureModel:
    lifetime: list[float, float]
    lifetime_unsup: list[float, float]
    scattering: list[float, float]
    scattering_unsup: list[float, float]
    spectrum: list[float, float]
    spectrum_unsup: list[float, float]
    size: float
    type: str
    type_idx: int
    """if 'type_idx' is -1 => type unknown"""
    time: datetime
    raw_data: RawData
    

    def __getitem__(self, key):
        return super().__getattribute__(key)

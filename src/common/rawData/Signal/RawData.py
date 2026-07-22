import numpy as np
from dataclasses import dataclass
from datetime import datetime

from src.common.sampler import get_scattering_normalized
from src.core import File, is_blank
from src.common.tensorflow import InputModelNames


@dataclass(frozen=True)
class RawData:
    scattering: np.ndarray[np.int_]
    spectrometer: np.ndarray[np.int_]
    lifetime: np.ndarray[np.int_]
    time: datetime
    file: File
    type: str
    size: float | None

    def __post_init__(self):
        if is_blank(self.type):
            raise ValueError(f"Pollen type cannot be blank, type={self.type}")

    def to_raw_dict(self):
        return {
            "Scattering": self.scattering,
            "Spectrometer": self.spectrometer,
            "Lifetime": self.lifetime,
            "Time": self.time,
        }

    def get_int64_timestamp(self):
        temp_time = np.datetime64(self.time, "us")
        temp_time = temp_time.astype("int64")
        return temp_time

    def to_unsup_input_name_dict(self, scattering_cutoff=None, fill_unsup=True):
        temp_scattering = self.scattering
        if scattering_cutoff is not None:
            temp_scattering = (
                get_scattering_normalized(
                    self.scattering, scattering_cutoff=scattering_cutoff
                )
                .reshape([-1])
                .astype("int64")
            )
        temp_time = self.time
        if isinstance(temp_time, datetime):
            temp_time = self.get_int64_timestamp()
        return {
            InputModelNames.SCATTERING: temp_scattering,
            InputModelNames.SCATTERING_UNSUP: temp_scattering if fill_unsup else None,
            InputModelNames.SPECTRUM: self.spectrometer,
            InputModelNames.SPECTRUM_UNSUP: self.spectrometer if fill_unsup else None,
            InputModelNames.LIFETIME: self.lifetime,
            InputModelNames.LIFETIME_UNSUP: self.lifetime if fill_unsup else None,
            InputModelNames.TIME_UNSUP: temp_time,
            InputModelNames.SIZE: self.size,
            type: self.type,
        }

    def __getitem__(self, key):
        return super().__getattribute__(key)

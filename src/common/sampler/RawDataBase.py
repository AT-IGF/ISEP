import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True)
class RawDataBase:
    scattering: np.ndarray[np.int_]
    spectrometer: np.ndarray[np.int_]
    lifetime: np.ndarray[np.int_]
    time: str

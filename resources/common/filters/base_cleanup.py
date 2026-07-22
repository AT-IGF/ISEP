import random

from src.common import Consts
from src.common.rawData.Signal import RawData
from src.common.sampler import (
    is_within_scattering_len_limit,
    is_lifetime_peak_centered,
    is_spectrum_peak_positive,
)


def filter(sample: RawData, scattering_cutoff=Consts.SCATTERING_CUTOFF, resolution=1):
    rand_val = random.random()
    if resolution < rand_val:
        return False

    return (
        is_within_scattering_len_limit(
            sample.scattering, scattering_cutoff=scattering_cutoff
        )
        and is_lifetime_peak_centered(sample.lifetime)
        and is_spectrum_peak_positive(sample.spectrometer)
    )

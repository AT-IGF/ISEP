import random

import numpy as np

from src.common import Consts
from src.common.rawData.Signal import RawData
from src.common.sampler import (
    is_within_scattering_len_limit,
    is_lifetime_peak_centered,
    is_spectrum_peak_positive,
    get_scattering_normalized,
    get_particle_size,
)


def is_valid(sample: RawData, scattering_cutoff):
    return (
        is_within_scattering_len_limit(
            sample.scattering, scattering_cutoff=scattering_cutoff
        )
        and is_lifetime_peak_centered(sample.lifetime)
        and is_spectrum_peak_positive(sample.spectrometer)
    )


def filter(
    sample: RawData, scattering_cutoff=Consts.SCATTERING_CUTOFF, resolution=1
):  # least restrictive version of should_append
    rand_val = random.random()
    if resolution < rand_val:
        return False

    is_valid(sample, scattering_cutoff)
    """One common filter for all particles"""
    lifetimes = sample.lifetime.reshape(-1, 64)
    for idx, lifetime in enumerate(lifetimes):
        if idx == 0:
            lifetime_max = np.max(lifetime)
            if lifetime_max < 150.0:
                return False
    spectras = sample.spectrometer.reshape(-1, 8)
    parcitcles_cols = []
    for i in range(0, 8):
        parcitcles_cols.append(spectras[:, i])
    for idx, spectrum in enumerate(parcitcles_cols):
        if idx == 1:
            spectrum_max = np.max(spectrum)
            spectrum_avg = np.average(spectrum)
            if spectrum_max > 30004 or spectrum_avg < 100:
                return False
    img = get_scattering_normalized(
        sample.scattering, scattering_cutoff=scattering_cutoff
    )
    scattering_avg = np.average(img)
    if scattering_avg > 4000000 or scattering_avg < 100000:
        return False

    size = get_particle_size(sample.scattering)
    if size < 4.75:
        return False

    return True

import numpy as np
from scipy.ndimage import center_of_mass


def get_scattering(scattering, n_detectors=24):
    flat = np.asarray(scattering, dtype=np.float64).ravel()
    return np.reshape(flat, [-1,n_detectors])
    
def get_scattering_normalized(scattering, scattering_cutoff=120, n_detectors=24):
    """
    Scattering normalization adopted after:
     Šaulienė, I. et al.: Automatic pollen recognition with the Rapid-E
     particle counter: the first-level procedure, experience and next steps,
     Atmos. Meas. Tech., 12, 3435–3452, 2019.
     https://doi.org/10.5194/amt-12-3435-2019

     Sikoparija, B. et al.: Classification accuracy and compatibility across
     devices of a new Rapid-E+ flow cytometer,
     Atmos. Meas. Tech., 17, 5051–5070, 2024.
     https://doi.org/10.5194/amt-17-5051-2024
    """
    img = get_scattering(scattering, n_detectors)

    window_h = scattering_cutoff

    padded = np.pad(img, ((window_h, window_h), (0, 0)))

    cy, _ = center_of_mass(np.abs(padded))
    cy = int(cy)

    # crop around center
    y = cy - window_h // 2
    out = padded[y : y + window_h, :]

    return np.array(out).astype(np.float32)


def get_particle_size(scattering) -> float:
    """
    Estimate particle optical size from scattering sum — Rapid-E.

    Šaulienė 2019 §2.2.2 (Novi Sad): manufacturer's approximation.

    Returns: estimated size in µm.
    """
    scatter_sum = np.asarray(scattering, dtype=np.float64).sum()
    if scatter_sum < 5_500_000:
        return 0.5
    elif scatter_sum <= 500_000_000:
        return 9.95e-1 * np.log(3.81e-5 * scatter_sum) - 4.84
    else:
        return 0.0004 * scatter_sum**0.5 - 3.9


def is_lifetime_peak_centered(lifetime, n_bands=64):
    lifetime_channels = np.asarray(lifetime).reshape(-1, n_bands)
    sum_across_lifetime_channels = np.sum(lifetime_channels, axis=0)
    peak_index = np.argmax(sum_across_lifetime_channels)
    if (peak_index < 10) or (peak_index > 40):
        return False
    return True


def is_within_scattering_len_limit(
    scattering, scattering_cutoff=120, n_detectors=24, times_larger=3
):  # handle a case of overlapping images
    return len(scattering) <= times_larger * scattering_cutoff * n_detectors


def is_spectrum_peak_positive(
    spectrum, scattering_cutoff=120, n_detectors=24, times_larger=3
):  # handle a case of overlapping images
    return np.max(spectrum) > 0

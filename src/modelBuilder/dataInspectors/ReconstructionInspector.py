import logging
from src.common.sampler.RapidAdopted import get_particle_size
from src.common.config import Config, ModelBuilderUnsupervisedConfig, DataViewerConfig
from src.dataViewer.DataViewer import (
    plot_spectrum,
    plot_scattering_intensity,
    plot_lifetime,
)
from src.common.tensorflow import InputModelNames
from matplotlib import pyplot as plt
import numpy as np


def get_learn_model_idx(learn_model_name):
    idx = -1
    if (
        learn_model_name
        in Config().get(ModelBuilderUnsupervisedConfig).train_parameters.learningModels
    ):
        idx = (
            Config()
            .get(ModelBuilderUnsupervisedConfig)
            .train_parameters.learningModels.index(learn_model_name)
        )
    return idx

def get_reconstruction_index(dataset, input_name):
    return list(dataset.keys()).index(input_name)

def plot_reconstruction(dataset, reconstructions):
    logging.getLogger().info("Plotting autoencoder reconstrucions")
    import numpy as np

    input_suffix = "_input"
    spectrum_idx = get_learn_model_idx(InputModelNames.SPECTRUM_UNSUP)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if spectrum_idx != -1:
        input_name = InputModelNames.SPECTRUM_UNSUP + input_suffix
        reconstruction_index = get_reconstruction_index(dataset, input_name)
        config = Config.get(DataViewerConfig)
        # config.plots.spectrum_max_y = None
        for i in range(0, 3):
            plot_spectrum(dataset[input_name][i], f"true_{i}", 0, config, show=False, colors=colors)
            plot_spectrum(
                reconstructions[reconstruction_index][i],
                f"reconstructed_{i}",
                0,
                config,
                show=True,
                linestyle="--",
                colors=colors
            )
            plt.close()

    scattering_idx = get_learn_model_idx(InputModelNames.SCATTERING_UNSUP)
    if scattering_idx != -1:
        input_name = InputModelNames.SCATTERING_UNSUP + input_suffix
        reconstruction_index = get_reconstruction_index(dataset, input_name)
        for i in range(0, 3):
            plot_scattering_intensity(
                scattering=dataset[input_name][i],
                pollen_type=f"true_{i}",
                idx=0,
                size=None,
                config=None,
                show=True,
            )
            plot_scattering_intensity(
                scattering=reconstructions[reconstruction_index][i],
                pollen_type=f"reconstructed_{i}",
                idx=0,
                size=None,
                config=None,
                vmax=np.max(dataset[input_name][i]),
            )
            plt.close()
    lifetime_idx = get_learn_model_idx(InputModelNames.LIFETIME_UNSUP)
    if lifetime_idx != -1:
        input_name = InputModelNames.LIFETIME_UNSUP + input_suffix
        reconstruction_index = get_reconstruction_index(dataset, input_name)
        for i in range(0, 3):
            plot_lifetime(
                lifetime=dataset[input_name][i],
                pollen_type=f"true_{i}",
                idx=0,
                config=None,
                reshape=True,
                show=False,
                label_prefix="true: ",
                linestyle="-",
                colors=colors
            )
            plot_lifetime(
                lifetime=reconstructions[reconstruction_index][i],
                pollen_type=f"reconstructed_{i}",
                idx=0,
                config=None,
                reshape=True,
                label_prefix="reconst.: ",
                linestyle="--",
                colors=colors
            )
            plt.close()


def calculate_reconstruction_error(dataset, reconstructed, errors=None):
    n_samples = len(reconstructed)

    def flatten_orig(i):
        vals = list(dataset.values())
        return np.array([np.array(x).flatten() for x in vals[i]])

    # helper to flatten a reconstructed sample
    def flatten_recon(rec):
        return np.array([np.array(x).flatten() for x in rec])

    # 1) compute per-sample errors
    dataset_keys = list(dataset.keys())
    if errors is None:
        errors = [[] for x in range(0, n_samples)]
    for i in range(n_samples):
        orig_flat = flatten_orig(i)
        rec_flat = flatten_recon(reconstructed[i])
        logging.getLogger().info(f"{dataset_keys[i]}, {np.sum(orig_flat)}")
        if orig_flat.shape != rec_flat.shape:
            raise ValueError(
                f"Sample {str(dataset_keys[i])} dimension mismatch: "
                f"orig has {orig_flat.shape}, "
                f"recon has {rec_flat.shape}."
            )

        errors[i].extend(np.mean(np.square(orig_flat - rec_flat), axis=1))

    return errors, list(dataset.keys())


def calculate_reconstrucion_thresholds(reconstruction_errors, reconstruction_keys):
    if len(reconstruction_errors) != len(reconstruction_keys):
        ValueError(
            f"Number of reconstructions differ from inout modalities, modalities_len={len(reconstruction_keys)} reconstruction_errors_len={len(reconstruction_errors)}"
        )

    for idx, values in enumerate(reconstruction_errors):
        values = np.array(values)

        thresh_pct_99 = np.percentile(values, 99)
        thresh_pct_95 = np.percentile(values, 95)
        thresh_pct_90 = np.percentile(values, 90)
        thresh_std = values.mean() + 3 * values.std()  # Or mean + k·std

        logging.getLogger().info(f"Errors of {reconstruction_keys[idx]}")
        logging.getLogger().info(f"MSE mean: {values.mean():.6f} ± {values.std():.6f}")
        logging.getLogger().info(f"MSE 99th‑pct threshold={thresh_pct_99}")
        logging.getLogger().info(f"MSE 95th‑pct threshold={thresh_pct_95}")
        logging.getLogger().info(f"MSE 90th‑pct threshold={thresh_pct_90}")
        logging.getLogger().info(f"MSE mean+3σ threshold={thresh_std}")

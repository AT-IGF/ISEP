import os
from src.common import Consts
from src.common.filters.ExternalRunner import get_filter
from src.common.sampler import get_scattering_normalized, get_particle_size
from src.common.config.configs import TypesConfig
from src.common.config import Config, DataViewerConfig
from src.common.tensorflow.Settings import setup_logger

from collections import Counter
import logging
import numpy as np
from src.core import PathHelper
from matplotlib import pyplot as plt
import matplotlib.transforms as mtrans
from src.common import get_pollen_types, Consts, RawData
from src.common.rawData.Signal.RawDataAdapter import get_pollen_type_from_path
import random
from src.core.plots.plotting_utils import plt_show


def mkdirs_if_not_exists(path):
    os.makedirs(path, exist_ok=True)


def plot_spectrum(
    spectrum,
    pollen_type: str,
    idx: int,
    config: DataViewerConfig,
    show=True,
    reshape=False,
    linestyle="-",
    colors=None
):
    plt.rcParams.update({"font.size": 24})
    if reshape:
        spectrum = np.array(spectrum).reshape(-1, 8)
    x_range = np.arange(350, 800, 14)[:32]
    laser_shots_range = np.arange(0, 3501, 500)
    for i in range(0, 8):
        plt.plot(
            x_range,
            spectrum[:, i],
            label=str(f"{i} - {laser_shots_range[i]}ns"),
            linestyle=linestyle,
        )
    # if config != None and config.plots.spectrum_max_y is not None:
    #     plt.yticks(np.arange(-1000, config.plots.spectrum_max_y, 1000))
    plt.title(f"{pollen_type}")
    plt.ylabel("Amplitude [NA]")
    plt.xlabel("Wavelength [nm]")
    plt.legend()
    if config != None:
        path = PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            f"{config.get_save_path()}/spectrometer",
            raise_on_not_found=False,
        )
        mkdirs_if_not_exists(path)
        plt.savefig(f"{path}/{pollen_type}{idx}")
    plt.grid(True, linestyle='--', linewidth=0.6, alpha=0.4, color='gray')
    if colors != None:
        plt.gca().set_prop_cycle(color=colors)
    if show == True:
        plt_show(plt.gcf())
        plt.close()


def plot_lifetime(
    lifetime,
    pollen_type: str,
    idx: int,
    config: DataViewerConfig,
    reshape=False,
    show=True,
    linewidth=1,
    label_prefix="",
    colors=None,
    linestyle="-",
):
    plt.rcParams.update({"font.size": 24})
    if reshape:
        lifetime = np.reshape(lifetime, (-1, 64))
    x_range = np.arange(0, 64, 1)
    channels = ["350-400 nm", "420-460 nm", "511-572 nm", "672-800 nm"]
    for i in range(0, 4):
        plt.plot(
            x_range,
            lifetime[i],
            label=label_prefix + str(channels[i]),
            linestyle=linestyle,
            linewidth=linewidth,
        )
    # if config != None and config.plots.lifetime_max_y is not None:
    #     plt.yticks(np.arange(-1000, config.plots.lifetime_max_y, 1000))
    plt.ylabel("Amplitude [NA]")
    plt.xlabel("Time [ns]")
    plt.title(pollen_type)
    plt.legend()
    if config != None:
        path = PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            f"{config.get_save_path()}/lifetime",
            raise_on_not_found=False,
        )
        mkdirs_if_not_exists(path)
        plt.savefig(f"{path}/{pollen_type}{idx}")
    plt.grid(True, linestyle='--', linewidth=0.6, alpha=0.4, color='gray')
    if colors != None:
        plt.gca().set_prop_cycle(color=colors)
    if show == True:
        plt_show(plt.gcf())
        plt.close()


def plot_scattering_intensity(
    scattering,
    pollen_type: str,
    idx: int,
    size: float,
    config: DataViewerConfig | None,
    show=True,
    vmax=None,
):
    plt.rcParams.update({"font.size": 24})
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(scattering, vmax=vmax)
    ax.set_aspect("equal")

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation="vertical", pad=0.1)

    ax.set_ylabel("Time [us]")
    ax.set_xlabel("Angle [deg]")
    # xticks = np.arange(SCATTERING_ANGLE_MIN, SCATTERING_ANGLE_MAX, 1)
    ax2 = ax.twinx()
    ax2.set_ylabel("Amplitude [NA]", labelpad=25)
    ax2.set_xticks([])
    ax.set_xlim(-1, 24)
    ax.set_xticks(range(-1, 24, 1))
    ax.set_xticklabels(
        [
            "",
            "45",
            "",
            "",
            "",
            "",
            "",
            "60",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "105",
            "",
            "",
            "",
            "",
            "",
            "135",
        ]
    )
    trans = mtrans.Affine2D().translate(5, 0)
    for t in ax.get_xticklabels():
        t.set_transform(t.get_transform() + trans)

    if size is not None:
        plt.title(f"{pollen_type}, size={round(size, 2)}µm")
    else:
        plt.title(f"{pollen_type}")
    if config != None:
        path = PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            f"{config.get_save_path()}/scattering",
            raise_on_not_found=False,
        )
        mkdirs_if_not_exists(path)
        plt.savefig(f"{path}/{pollen_type}{idx}")
    if show == True:
        plt_show(plt.gcf())
    plt.close()


def plot_data(config: DataViewerConfig, raw_data: list[RawData]):
    logger = logging.getLogger()
    counter = Counter()

    logger.info(
        f"Random pickup frequency is set to={config.rand_0_1_frequency}. Value range=[0-1], 0-every particle, 0.5-every 2nd, etc."
    )
    logger.info(f"Same type particles to show count = {config.same_type_count}")
    for idx, temp_sample in enumerate(raw_data):
        if idx % 10:
            logger.info(f"({idx}/{len(raw_data)}) proceeded")

        rand_num = random.uniform(0, 1)
        if (
            temp_sample.type in counter.keys()
            and counter[temp_sample.type] >= config.same_type_count
            and rand_num >= config.rand_0_1_frequency
        ):
            logger.debug(
                f"Pollen type='{temp_sample.type}' max count={config.same_type_count} exceeded. Skipped"
            )

        scattering_normal = get_scattering_normalized(
            temp_sample.to_raw_dict()["Scattering"], scattering_cutoff=Consts.SCATTERING_CUTOFF
        )

        if config.show_plots:
            logger.info(f"Plotting: {temp_sample.type}{idx}")

        was_any_seen = False
        pollen_type = get_pollen_type_from_path(temp_sample.file.path)
        lifetime_plot = config.lifetime_plot
        lifetime_max = np.max(temp_sample.lifetime)
        if lifetime_plot.show and lifetime_plot.is_within_range(lifetime_max):
            temp_lifetime = np.reshape(temp_sample.lifetime, (-1, 64))
            plot_lifetime(temp_lifetime, pollen_type, idx, config, show=config.show_plots)
            was_any_seen = True

        spectrum_plot = config.spectrum_plot
        spectrum_max = np.max(temp_sample.spectrometer)
        if spectrum_plot.show and spectrum_plot.is_within_range(spectrum_max):
            temp_spectrum = np.reshape(temp_sample.spectrometer, (-1, 8))
            plot_spectrum(temp_spectrum, pollen_type, idx, config, show=config.show_plots)
            was_any_seen = True

        scattering_plot = config.scattering_plot
        scattering_avg = np.average(temp_sample.scattering)
        if scattering_plot.show and scattering_plot.is_within_range(scattering_avg):
            particle_size = get_particle_size(temp_sample.scattering)
            plot_scattering_intensity(
                scattering_normal, pollen_type, idx, particle_size, config, show=config.show_plots
            )
            was_any_seen = True

        if not was_any_seen:
            logger.info(
                f"Skipped: {temp_sample.type}{idx}. Filtered based on restrictions"
            )
            continue

        counter += Counter([temp_sample.type])


def handle():
    setup_logger(module_name=DataViewerConfig.module_name)
    config = Config.get(DataViewerConfig)
    pollen_types = Config.get(TypesConfig).pollen_types

    if len(pollen_types) == 0:
        logging.getLogger().warning(
            "No types to process set (general config -> pollen_types). Finishing."
        )
        return

    filter_callback = get_filter(config.filter_path)
    raw_data_types: list[RawData] = get_pollen_types(
        single_type_count=config.same_type_count,
        should_append_callback=filter_callback,
        pollen_types=config.pollen_types_to_show
    )

    plot_data(config, raw_data_types)


if __name__ == "__main__":
    handle()

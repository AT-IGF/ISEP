import math
from src.common.filters.ExternalRunner import get_filter
from src.helpers.PlotHelper import get_name
from src.common import Consts
from src.core.plots.plotting_utils import plt_show
import src.common.tensorflow.InputModelNames as inputNames
from src.common.tensorflow.Settings import setup_logger
from src.common.config import (
    Config,
    AllParticlesAvgsConfig,
    TypesConfig,
)

from src.common import RawData
import numpy as np
import matplotlib

import matplotlib.pyplot as plt
import logging

config: AllParticlesAvgsConfig | None = None
from src.common.sampler import get_scattering_normalized, get_particle_size

plt.rcParams.update({"font.size": 20})


def plot_hist(
    vals,
    type,
    ax,
    q_min=None,
    q_max=None,
    custom=None,
    title="",
    idx=None,
    label=None,
    bins=100,
    alpha=0.3,
    show=True,
):
    color = None
    label = None
    if idx != None:
        color = Consts.PLOT_COLORS[idx]
        label = type
    ax.hist(vals, bins=bins, edgecolor="black", alpha=alpha, color=color, label=label)
    ax.set_title(title)

    if q_min != None:
        bottom = np.percentile(vals, q=q_min)
        ax.axvline(x=bottom)
    if q_max != None:
        up = np.percentile(vals, q=q_max)
        ax.axvline(x=up)
    if custom != None:
        ax.axvline(x=custom, color="red")
    # print("5", bottom)
    # print("95", up)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.6, alpha=0.4, color='gray')
    if show:
        plt_show(plt.gcf())
        plt.close()

def plot_hist_plot(hist, vals, types, idx, ax, xlabel=None, ylabel=None):
    if hist.display_mode == hist.ONE_BY_ONE_MODE:
        fig, ax = plt.subplots()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    ax = ax[idx] if isinstance(ax, np.ndarray) else ax
    title = None
    if (
        hist.display_mode == hist.ONE_BY_ONE_MODE
        or hist.display_mode == hist.ALL_IN_ONE_MODE
        and hist.is_display_as_grid()
    ):
        title = f"{types[idx]}"
    plot_hist(
        vals=vals,
        type=types[idx],
        ax=ax,
        q_min=hist.q_min,
        q_max=hist.q_max,
        custom=hist.cutom_line,
        title=title,
        idx=idx,
        bins=hist.hist_bins,
        alpha=(
            0.3
            if hist.display_mode == hist.ALL_IN_ONE_MODE
            and not hist.is_display_as_grid()
            else 0.7
        ),
        show=hist.display_mode == hist.ONE_BY_ONE_MODE,
    )


def coalesce(value, default):
    return value if value is not None else default


def get_grid(n, n_cols=3, share_y=True):
    n_rows = math.ceil(n / n_cols)
    fig_size = n_cols * 4, n_rows * 3
    return plt.subplots(
        n_rows, n_cols, figsize=fig_size, squeeze=False, sharex=True, sharey=share_y
    )


def get_grid_axes(hist, types, xlabel=None, ylabel=None):
    fig, axe_s = plt.subplots()
    if hist.plot and hist.is_display_as_grid():
        fig, axe_s = get_grid(
            n=len(types), n_cols=hist.n_cols, share_y=hist.share_y_grid
        )
        axe_s = axe_s.ravel()
        for ax in axe_s[len(types) :]:
            fig.delaxes(ax)
        fig.supxlabel(xlabel)
        fig.supylabel(ylabel)
    return fig, axe_s


def plot_lifetime(lifetimes, types):
    if not config.lifetime.is_plot_combined():
        return

    logger = logging.getLogger(config.module_name)
    x_range = np.arange(0, 64, 1)
    channels = ["350-400 nm", "420-460 nm", "511-572 nm", "672-800 nm"]
    logger.info("for idx, lifetime in enumerate(lifetimes):")

    plot = config.lifetime.plot_combined
    for i in config.lifetime.channels:
        i = i - 1  # channels as first channel - 1 so enumeration decreased by 1
        logger.info(f"Channel: {channels[i]}")

        for idx, particle_lifetimes in enumerate(lifetimes):
            if particle_lifetimes == []:
                continue

            avgs = np.average(np.array(particle_lifetimes)[:, i], axis=0)
            plt.plot(
                x_range,
                avgs,
                label=f"{str(types[idx])}",
                marker=Consts.PLOT_MARKERS[idx],
                color=Consts.PLOT_COLORS[idx],
            )
            plt.scatter(
                x_range,
                avgs,
                marker=Consts.PLOT_MARKERS[idx],
                color=Consts.PLOT_COLORS[idx],
                s=70,
            )
            if plot.q_max != None:
                up = np.percentile(
                    np.array(particle_lifetimes)[:, i],
                    axis=0,
                    q=coalesce(plot.q_max, 100),
                )
                plt.scatter(
                    x_range,
                    up,
                    marker=Consts.PLOT_MARKERS[idx],
                    color=Consts.PLOT_COLORS[idx],
                    s=20,
                    alpha=1,
                )
                plt.plot(
                    x_range,
                    up,
                    color=Consts.PLOT_COLORS[idx],
                    alpha=0.2,
                    linestyle="--",
                )
            if plot.q_min != None:
                bottom = np.percentile(
                    np.array(particle_lifetimes)[:, i],
                    axis=0,
                    q=coalesce(plot.q_min, 0),
                )
                plt.scatter(
                    x_range,
                    bottom,
                    marker=Consts.PLOT_MARKERS[idx],
                    color=Consts.PLOT_COLORS[idx],
                    s=20,
                    alpha=1,
                )
                plt.plot(
                    x_range,
                    bottom,
                    color=Consts.PLOT_COLORS[idx],
                    alpha=0.2,
                    linestyle="--",
                )

        plt.legend(ncol=plot.n_cols)
        plt.ylabel("Fluorescence amplitude [AU]")
        plt.xlabel(f"Fluorescence lifetime {channels[i]} [ns]")
        plt.ylim(plot.y_min, plot.y_max)
        handles, labels = plt.gca().get_legend_handles_labels()
        if plot.q_min != None or plot.q_max != None:
            blank_space = plt.Line2D([], [], color="white", linestyle="")
            average_desc = plt.Line2D([], [], color="grey", linestyle="-")

            handles.append(blank_space)
            labels.append("")
            handles.append(average_desc)
            labels.append("Average (solid line)")

            if plot.q_min or plot.q_max:
                quartiles_desc = plt.Line2D([], [], color="grey", linestyle="--")
                handles.append(quartiles_desc)
                labels.append(format_range(plot.q_min, plot.q_max, "percentile (dashed line)"))

        plt.legend(handles, labels, ncol=plot.n_cols, markerscale=2)
        plt.grid(True, linestyle='--', linewidth=0.6, alpha=0.4, color='gray')
        plt_show(plt.gcf())


def hist_lifetime(lifetimes, types):
    hist = config.lifetime.histogram
    if hist.plot == False:
        return

    logger = logging.getLogger(config.module_name)
    channels = ["350-400 nm", "420-460 nm", "511-572 nm", "672-800 nm"]
    logger.info("for idx, lifetime in enumerate(lifetimes):")

    for i in config.lifetime.channels:
        i = i - 1  # channels as first channel - 1 so enumeration decreased by 1
        logger.info(f"Channel: {channels[i]}")

        fig, axe_s = get_grid_axes(
            hist,
            types,
            xlabel=f"Fluorescence amplitude {channels[i]} [AU]",
            ylabel="Number of samples",
        )

        for idx, particle_lifetimes in enumerate(lifetimes):
            if particle_lifetimes == []:
                continue
            vals = []
            for idx_lf, particle_lifetime in enumerate(particle_lifetimes):
                if hist.operation == "max":
                    lifetime_operation = np.max(np.array(particle_lifetime[i]))
                elif hist.operation == "avg":
                    lifetime_operation = np.average(particle_lifetime[i])
                else:
                    raise ValueError(
                        "Histgoram operaion not defined, allowed: ['max', 'avg']"
                    )
                if hist.higher_than != None and lifetime_operation > hist.higher_than:
                    continue
                if hist.lower_than != None and lifetime_operation < hist.lower_than:
                    continue
                vals.append(lifetime_operation)
            plot_hist_plot(
                hist=hist,
                vals=vals,
                types=types,
                idx=idx,
                ax=axe_s,
            )
        if hist.display_mode == hist.ALL_IN_ONE_MODE:
            if not hist.is_display_as_grid():
                plt.xlabel(f"Fluorescence amplitude {channels[i]} [AU]")
                plt.ylabel("Number of samples")
                handles, labels = plt.gca().get_legend_handles_labels()
                plt.legend(handles, labels, ncol=hist.n_cols, markerscale=2)
            plt_show(plt.gcf())
            plt.close()


def hist_spectras(spectas, types):
    hist = config.spectrum.histogram
    if not hist.plot:
        return

    logger = logging.getLogger(config.module_name)
    laser_shots_range = np.arange(0, 3501, 500)
    for i in config.spectrum.channels:
        i = i - 1  # channels as first channel - 1 so enumeration decreased by 1
        logger.info(f"Channel: {laser_shots_range[i]} ms")
        xlabel = f"Fluorescence amplitude {laser_shots_range[i]} [AU]"
        ylabel = "Number of samples"

        fig, axe_s = get_grid_axes(
            hist,
            types,
            xlabel=xlabel,
            ylabel=ylabel,
        )
        for idx, particles_spectas in enumerate(spectas):
            if particles_spectas == []:
                continue
            parcitcles_cols = []
            for particle_spectas in particles_spectas:
                parcitcles_cols.append(particle_spectas[:, i])

            vals = []
            for particle_col in parcitcles_cols:
                if hist.operation == "max":
                    spectrum_operation = np.max(particle_col)
                elif hist.operation == "avg":
                    spectrum_operation = np.average(particle_col)
                else:
                    raise ValueError(
                        "Histgoram operaion not defined, allowed: ['max', 'avg']"
                    )

                if hist.higher_than != None and spectrum_operation > hist.higher_than:
                    continue
                if hist.lower_than != None and spectrum_operation < hist.lower_than:
                    continue
                vals.append(spectrum_operation)
            plot_hist_plot(
                hist=hist,
                vals=vals,
                types=types,
                idx=idx,
                ax=axe_s,
                xlabel=xlabel,
                ylabel=ylabel,
            )

        if hist.display_mode == hist.ALL_IN_ONE_MODE:
            if not hist.is_display_as_grid():
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                handles, labels = plt.gca().get_legend_handles_labels()
                plt.legend(handles, labels, ncol=hist.n_cols, markerscale=2)
            plt_show(plt.gcf())
            plt.close()


def plot_spectras(spectas, types):
    logger = logging.getLogger(config.module_name)
    x_range = np.arange(350, 800, 14)[:32]
    laser_shots_range = np.arange(0, 3501, 500)
    plot = config.spectrum.plot_combined
    for i in config.spectrum.channels:
        i = i - 1  # channels as first channel - 1 so enumeration decreased by 1
        logger.info(f"Channel: {laser_shots_range[i]} ms")

        for idx, particles_spectas in enumerate(spectas):
            if particles_spectas == []:
                continue
            parcitcles_cols = []
            for particle_spectas in particles_spectas:
                parcitcles_cols.append(particle_spectas[:, i])

            if plot.plot == True:
                avgs = np.average(np.array(parcitcles_cols), axis=0)
                avgs = np.mean(parcitcles_cols, axis=0)
                plt.plot(
                    x_range,
                    avgs,
                    label=f"{str(types[idx])}",
                    marker=Consts.PLOT_MARKERS[idx],
                    color=Consts.PLOT_COLORS[idx],
                )
                plt.scatter(
                    x_range,
                    avgs,
                    marker=Consts.PLOT_MARKERS[idx],
                    color=Consts.PLOT_COLORS[idx],
                    s=50,
                )
                if plot.q_max != None:
                    up = np.percentile(
                        np.array(parcitcles_cols), axis=0, q=coalesce(plot.q_max, 100)
                    )
                    plt.scatter(
                        x_range,
                        up,
                        marker=Consts.PLOT_MARKERS[idx],
                        color=Consts.PLOT_COLORS[idx],
                        s=20,
                        alpha=1,
                    )
                    plt.plot(
                        x_range,
                        up,
                        color=Consts.PLOT_COLORS[idx],
                        alpha=0.2,
                        linestyle="--",
                    )
                if plot.q_min != None:
                    bottom = np.percentile(
                        np.array(parcitcles_cols), axis=0, q=coalesce(plot.q_min, 0)
                    )
                    plt.scatter(
                        x_range,
                        bottom,
                        marker=Consts.PLOT_MARKERS[idx],
                        color=Consts.PLOT_COLORS[idx],
                        s=20,
                        alpha=1,
                    )
                    plt.plot(
                        x_range,
                        bottom,
                        color=Consts.PLOT_COLORS[idx],
                        alpha=0.2,
                        linestyle="--",
                    )

        if plot.plot == True:
            plt.ylabel("Fluorescence amplitude [AU]")
            plt.xlabel("Vawelenght [nm]")
            plt.title(f"Spectrum after - {laser_shots_range[i]} ns")
            # plt.ylim(-500,25000)
            handles, labels = plt.gca().get_legend_handles_labels()
            blank_space = plt.Line2D([], [], color="white", linestyle="")
            average_desc = plt.Line2D([], [], color="grey", linestyle="-")
            if plot.q_min or plot.q_max:
                quartiles_desc = plt.Line2D([], [], color="grey", linestyle="--")
            handles.append(blank_space)
            labels.append("")
            handles.append(average_desc)
            labels.append("Average (solid line)")
            if plot.q_min or plot.q_max:
                handles.append(quartiles_desc)
                labels.append(format_range(plot.q_min, plot.q_max, "percentile (dashed line)"))
            plt.legend(handles, labels, ncol=plot.n_cols)
            plt.grid(True, linestyle='--', linewidth=0.6, alpha=0.4, color='gray')
            plt_show(plt.gcf())

def format_range(start, end, suffix=""):
    parts = [str(v) for v in (start, end) if v is not None]
    if not parts:
        return ""
    return " - ".join(parts) + (f" {suffix}" if suffix else "")

def get_pollen_type_idx(pollen_types: list[str], pollenType):
    return pollen_types.index(pollenType)


def hist_scatterings(scatterings, types):
    hist = config.scattering.histogram

    fig, axe_s = get_grid_axes(
        hist,
        types,
        xlabel="Amplitude [AU]",
        ylabel="Number of samples",
    )
    for idx, particles_scattering in enumerate(scatterings):
        if particles_scattering == []:
            continue
        if hist.plot == True:
            vals = []
            for particle_scattering in particles_scattering:
                if hist.operation == "max":
                    scattering_operation = np.max(particle_scattering)
                elif hist.operation == "avg":
                    scattering_operation = np.average(particle_scattering)
                else:
                    raise ValueError(
                        "Histgoram operaion not defined, allowed: ['max', 'avg']"
                    )

                if hist.higher_than != None and scattering_operation > hist.higher_than:
                    continue
                if hist.lower_than != None and scattering_operation < hist.lower_than:
                    continue
                vals.append(scattering_operation)

            plot_hist_plot(
                hist=hist,
                vals=vals,
                types=types,
                idx=idx,
                ax=axe_s,
            )
    if hist.plot and hist.display_mode == hist.ALL_IN_ONE_MODE:
        if not hist.is_display_as_grid():
            plt.xlabel("Amplitude [AU]")
            plt.ylabel("Number of samples")
            handles, labels = plt.gca().get_legend_handles_labels()
            plt.legend(handles, labels, ncol=hist.n_cols, markerscale=2)
        plt_show(plt.gcf())
        plt.close()


def hist_sizes(sizes, types):
    hist = config.size.histogram

    fig, ax = get_grid_axes(
        hist,
        types,
        xlabel=f"Size [μm]",
        ylabel="Number of samples",
    )

    for idx, size in enumerate(sizes):
        if len(size) == 0:
            continue
        if hist.higher_than != None:
            size = [x for x in size if x < hist.higher_than]
        if hist.lower_than != None:
            size = [x for x in size if x > hist.lower_than]
        plot_hist_plot(
            hist=hist,
            vals=size,
            types=types,
            idx=idx,
            ax=ax,
        )

    if hist.plot and hist.display_mode == hist.ALL_IN_ONE_MODE:
        if not hist.is_display_as_grid():
            plt.xlabel("Size [μm]")
            plt.ylabel("Number of samples")
            handles, labels = plt.gca().get_legend_handles_labels()
            plt.legend(handles, labels, ncol=hist.n_cols, markerscale=2)
        plt_show(plt.gcf())
        plt.close()


def handle():
    setup_logger(module_name=AllParticlesAvgsConfig.module_name)
    global config
    config = Config.get(AllParticlesAvgsConfig)  # override
    pollen_types = Config.get(TypesConfig).pollen_types

    from src.common.rawData.RawDataHanlder import get_pollen_types

    logger = logging.getLogger(config.module_name)
    logger.info("Drawing aggregated summary")

    if len(pollen_types) == 0:
        logger.warning("No types to process set (general -> pollen_types). Finishing.")
        return

    filter_callback = get_filter(config.filter_path)
    raw_data_types: list[RawData] = get_pollen_types(
        single_type_count=config.single_type_count,
        test_model=None,
        should_append_callback=filter_callback,
        pollen_types=config.pollen_types
    )

    def loop(callback):
        for i, raw_data in enumerate(raw_data_types):
            pollen_idx = get_pollen_type_idx(config.pollen_types, raw_data.type)
            callback(pollen_idx, raw_data)

    logger.info(
        f"Current metric to be processed, metric='{config.metric_to_process}', (Available metrics={inputNames.PLOTTING_MODELS})"
    )

    n = len(config.pollen_types)
    pollen_types_updated = [get_name(x) for x in config.pollen_types[:]]
    if config.metric_to_process == inputNames.SCATTERING:
        scatterings = [[] for _ in range(n)]

        def callback(pollen_idx, raw_data: RawData):
            image_normalized = get_scattering_normalized(
                raw_data.scattering, scattering_cutoff=Consts.SCATTERING_CUTOFF
            )
            if image_normalized is None:
                return
            if len(scatterings[pollen_idx]) < 4000:
                scatterings[pollen_idx].append(image_normalized)

        loop(lambda pollen_idx, raw_data: callback(pollen_idx, raw_data))
        hist_scatterings(scatterings, pollen_types_updated)
    elif config.metric_to_process == inputNames.LIFETIME:
        lifetimes = [[] for _ in range(n)]
        loop(
            lambda pollen_idx, raw_data: lifetimes[pollen_idx].append(
                raw_data.lifetime.reshape(-1, 64)
            )
        )
        hist_lifetime(lifetimes, pollen_types_updated)
        plot_lifetime(lifetimes, pollen_types_updated)

    elif config.metric_to_process == inputNames.SPECTRUM:
        spectras = [[] for _ in range(n)]
        loop(
            lambda pollen_idx, raw_data: spectras[pollen_idx].append(
                raw_data.spectrometer.reshape(-1, 8)
            )
        )
        hist_spectras(spectras, pollen_types_updated)
        plot_spectras(spectras, pollen_types_updated)
    elif config.metric_to_process == inputNames.SIZE:
        sizes = [[] for _ in range(n)]
        loop(
            lambda pollen_idx, raw_data: sizes[pollen_idx].append(
                get_particle_size(raw_data.scattering)
            )
        )
        hist_sizes(sizes, pollen_types_updated)
    else:
        raise ValueError(
            f"No metric to process found. metric='{config.metric_to_process}', available_metrics={inputNames.PLOTTING_MODELS}"
        )

    logger.info("Particles mapped")


if __name__ == "__main__":
    matplotlib.use("TkAgg")
    handle()

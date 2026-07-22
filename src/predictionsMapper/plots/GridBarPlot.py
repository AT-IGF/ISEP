from datetime import datetime
import math
from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import numpy as np
from src.predictionsMapper.common import calculate_p_per_m3
from src.core.plots.plotting_utils import plt_show

from src.helpers.PlotHelper import get_name, should_be_displayed
from src.predictionsMapper.common.ThresholdHelper import get_threshold
from src.common.config.configs import PredictionsMapperConfig
from src.predictionsMapper.common.Consts import (
    FROM_TIME_KEY,
    TO_TIME_KEY,
)
from src.common import Consts
import pandas as pd


class GridBarPlot:
    def __init__(self, config: PredictionsMapperConfig):
        self.config = config
        self.bar_config = config.plot_settings.bar_plot_settings
        self.n_cols = self.bar_config.n_cols
        self.months_of_expectance = self.bar_config.get_months_of_expectance(
            pollen_types=self.config.pollen_types
        )

    def get_colors(self, frame, col, in_color):
        out_color = "gray"
        from_date: list[datetime] = frame[FROM_TIME_KEY]
        to_date: list[datetime] = frame[TO_TIME_KEY]
        cols_months = self.months_of_expectance
        colors = []
        for i in range(0, len(frame)):
            if col not in cols_months:
                return in_color, np.array([False] * len(frame))

            col_months = cols_months[col]
            if from_date[i].month in col_months or to_date[i].month in col_months:
                colors.append(in_color)
            else:
                colors.append(out_color)
        mask = np.array(colors) != out_color
        return colors, mask

    def show(self, frame_summary):
        frame_summary_original = frame_summary[:]
        data_to_show = frame_summary.drop(columns=[FROM_TIME_KEY, TO_TIME_KEY])
        
        idx_to_drop = []
        for idx, data in enumerate(data_to_show):
            if not should_be_displayed(self.config.pollen_types, data):
                idx_to_drop.append(idx)
        data_to_show = data_to_show.drop(columns=data_to_show.columns[idx_to_drop])
        data_to_show_original = data_to_show[:]

        num_groups = len(
            data_to_show.keys().tolist()
        )  # Number of groups (bars per category)
        num_categories = len(data_to_show)
        x = np.arange(num_categories)  # X positions for categories
        width = 0.8 / num_groups

        fig, axes = plt.subplots(
            nrows=math.ceil(len(data_to_show.columns) / self.n_cols),
            ncols=self.n_cols,
            figsize=(12, 4),
            sharex=True,
        )
        
        # for ax in axes.flat[len(data_to_show.columns):]:
        #     ax.set_visible(False)
            
        (data_to_show, left_label_text) = self.get_data_to_show(data_to_show_original)
        right_label_text = (
            "Particles count" if self.bar_config.show_particle_count else None
        )

        for idx, data in enumerate(data_to_show):
            col = data_to_show.columns[idx]
            current_tr = get_threshold(thresholds=self.config.thresholds, p_type=col)
            ax = axes[idx // self.n_cols, idx % self.n_cols]
            ax.grid(True, axis='y', linestyle='--', linewidth=0.6, alpha=0.4, color='gray')

            colors, mask = self.get_colors(
                frame_summary_original, col, Consts.PLOT_COLORS[idx]
            )

            ax.bar(
                (x + (width / 2)),
                data_to_show.iloc[:, idx],
                width=0.8,
                label=f"{get_name(data_to_show.keys().tolist()[idx])}, tr={current_tr}",
                color=colors,
            )
            ax.set_title(f"{get_name(col)}, tr={current_tr}")

            if self.bar_config.show_particle_count:
                ax2 = ax.twinx()
                ax2.plot(
                    (x + (width / 2)),
                    data_to_show_original.iloc[:, idx],
                    color="tab:red",
                )

            if self.bar_config.is_months_of_expectance and np.sum(mask) != 0 and len(data_to_show_original.iloc[:, idx][mask == False]) != 0:
                ax3 = ax.twinx()
                highest_not_expected_times_1 = 1 * max(
                    data_to_show_original.iloc[:, idx][mask == False]
                )
                ax3.axhline(highest_not_expected_times_1, color="tab:green")
                ax3.set_ylim(ax2.get_ylim())

                ax.bar(
                    (x + (width / 2)),
                    data_to_show.iloc[:, idx],
                    width=0.8,
                    label=f"{get_name(data_to_show.keys().tolist()[idx])}, tr={self.months_of_expectance[col]}",
                    color=colors,
                )

        plt.xticks(
            rotation=45,
            ticks=np.arange(len(frame_summary[TO_TIME_KEY])),
            labels=[
                f'{frame_summary_original[FROM_TIME_KEY][idx].strftime("%m-%d")} - {x.strftime("%m-%d")}'
                for idx, x in enumerate(frame_summary[TO_TIME_KEY])
            ],
        )
        for idx, ax in enumerate(axes.flat):
            ax.tick_params(axis="x", labelrotation=75)
            ax.grid(True, axis='y', linestyle='--', linewidth=0.6, alpha=0.4, color='gray')
            for label in ax.get_xticklabels():
                label.set_horizontalalignment("right")
                label.set_rotation_mode("anchor")

        handles = []
        plt.rcParams["figure.figsize"] = (15, 8)

        self.set_labels(fig, left_label_text, right_label_text)
        handles = self.get_handles()
        fig.legend(
            handles=handles,
            loc="lower center",
            ncol=3,
            bbox_to_anchor=(0.5, 0),
            frameon=False,
        )
        fig.subplots_adjust(hspace=0.8, wspace=0.38, bottom=0.3, top=0.95, left=0.08)
        plt.ylim()
        plt_show(plt.gcf())

    def get_data_to_show(self, data_to_show_original):
        if self.bar_config.plot_type == self.bar_config.PARTICLES_PER_METER_CUBED:
            data_to_show = calculate_p_per_m3(data_to_show_original, self.config.split_timespan)
            left_label_text = "Pollen P/m³"
        elif (
            self.bar_config.plot_type
            == self.bar_config.PERCENTAGE_SHARE_IN_TIMESPAN_PLOT
        ):
            data_to_show = (
                data_to_show_original.div(data_to_show_original.sum(axis=1), axis=0)
                * 100
            )
            left_label_text = "Share [%]"
        else:
            raise ValueError(
                f"PLot type not implemented: {self.bar_config.plot_type}. Available types: {self.bar_config.PLOT_TYPES}"
            )
        return data_to_show, left_label_text

    def set_labels(self, fig, left_label_text, right_label_text):
        left_label = fig.supylabel(left_label_text)
        x0, y0 = left_label.get_position()
        font_props = {
            "fontproperties": left_label.get_fontproperties(),
            "va": left_label.get_va(),
        }
        fig.text(
            x0,
            0.5,
            left_label_text,
            rotation=90,
            **font_props,
        )
        if right_label_text is not None:
            fig.text(1 - x0, 0.5, right_label_text, **font_props, rotation=-90)

    def get_handles(self):
        handles = []
        if self.bar_config.show_particle_count:
            count_handle = mlines.Line2D(
                [], [], color="tab:red", label="Particles detected count"
            )
            handles.append(count_handle)

        if self.bar_config.is_months_of_expectance:
            bar_handle = mpatches.Patch(color="gray", label="Pollination not expected")
            highest_count_handle = mlines.Line2D(
                [],
                [],
                color="tab:green",
                label="Highest count in 'not expected' period",
            )
            handles.extend([bar_handle, highest_count_handle])
        return handles

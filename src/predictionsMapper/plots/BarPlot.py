from matplotlib import pyplot as plt
import numpy as np
from src.predictionsMapper.plots.base.BarBase import BarBase
from src.core.plots.plotting_utils import plt_show

from src.helpers.PlotHelper import get_name, should_be_displayed
from src.common.config.configs import PredictionsMapperConfig
from src.predictionsMapper.common.Consts import FROM_TIME_KEY, TO_TIME_KEY
from src.common import Consts


class BarPlot(BarBase):
    def __init__(self, config: PredictionsMapperConfig):
        super().__init__()
        self.config = config

    def show(self, frame_summary):
        data_to_show_original = frame_summary.drop(columns=[FROM_TIME_KEY, TO_TIME_KEY])
        num_groups = len(data_to_show_original.keys().tolist())
        num_categories = len(data_to_show_original)
        x = np.arange(num_categories)
        width = 0.8 / num_groups

        (data_to_show, left_label_text) = super().get_data_to_show(
            data_to_show_original
        )

        for idx, data in enumerate(data_to_show):
            if not should_be_displayed(self.config.pollen_types, data):
                continue

            plt.bar(
                x + (idx - (num_groups - 1) / 2) * width,
                data_to_show.iloc[:, idx],
                width=width,
                label=get_name(data_to_show.keys().tolist()[idx]),
                color=Consts.PLOT_COLORS[idx],
            )

        super().set_labels(plt.gcf(), left_label_text, None)
        plt.xticks(
            rotation=45,
            ticks=np.arange(len(frame_summary[TO_TIME_KEY])),
            labels=[
                f'{frame_summary[FROM_TIME_KEY][idx].strftime("%m-%d")} - {x.strftime("%m-%d")}'
                for idx, x in enumerate(frame_summary[TO_TIME_KEY])
            ],
        )

        plt.rcParams["figure.figsize"] = (15, 8)
        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=5)
        plt.subplots_adjust(bottom=0.35, top=0.98)
        plt.ylim()
        plt_show(plt.gcf())

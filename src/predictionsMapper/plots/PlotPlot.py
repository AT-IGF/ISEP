from matplotlib import pyplot as plt
import numpy as np

from src.predictionsMapper.common.SampleHelper import calculate_p_per_m3
from src.helpers.PlotHelper import get_name, should_be_displayed
from src.core.plots.plotting_utils import plt_show
from src.common.config.configs import PredictionsMapperConfig
from src.predictionsMapper.common.Consts import FROM_TIME_KEY, TO_TIME_KEY


class PlotPlot:
    def __init__(self, config: PredictionsMapperConfig):
        self.config = config
        self.line_config = config.plot_settings.line_plot_settings

    def get_data_to_show(self, data_to_show_original):
        if self.line_config.plot_type == self.line_config.PARTICLES_PER_METER_CUBED:
            data_to_show = calculate_p_per_m3(
                data_to_show_original, span=self.config.split_timespan
            )
            left_label_text = "Pollen P/m³"
        elif self.line_config.plot_type == self.line_config.COUNT:
            data_to_show = data_to_show_original
            left_label_text = "Count"
        else:
            raise ValueError(
                f"PLot type not implemented: {self.line_config.plot_type}. Available types: {self.line_config.PLOT_TYPES}"
            )
        return data_to_show, left_label_text

    def show(self, frame_summary):
        data_to_show = frame_summary.drop(columns=[FROM_TIME_KEY, TO_TIME_KEY])
        (data_to_show, left_label_text) = self.get_data_to_show(data_to_show)

        for idx, data in enumerate(data_to_show):
            if not should_be_displayed(self.config.pollen_types, data):
                continue

            plt.plot(
                data_to_show.iloc[:, idx],
                marker="o",
                label=get_name(data_to_show.keys().tolist()[idx]),
            )

        plt.xticks(
            rotation=45,
            ticks=np.arange(len(frame_summary[TO_TIME_KEY])),
            labels=np.array(
                [
                    f'{frame_summary[FROM_TIME_KEY][idx].strftime("%m-%d")} - {x.strftime("%m-%d")}'
                    for idx, x in enumerate(frame_summary[TO_TIME_KEY])
                ]
            ),
        )
        plt.ylabel(left_label_text)
        plt.rcParams["figure.figsize"] = (15, 8)
        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=5)
        plt.subplots_adjust(bottom=0.35, top=0.98)
        plt.ylim()
        plt_show(plt.gcf())

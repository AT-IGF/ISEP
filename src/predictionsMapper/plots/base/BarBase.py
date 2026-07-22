from src.common.config import Config
from src.common.config.configs import PredictionsMapperConfig
from src.predictionsMapper.common.SampleHelper import calculate_p_per_m3


class BarBase:
    def __init__(self):
        self.config = Config.get(PredictionsMapperConfig)
        self.bar_config = self.config.plot_settings.bar_plot_settings

    def get_data_to_show(self, data_to_show_original):
        if self.bar_config.plot_type == self.bar_config.PARTICLES_PER_METER_CUBED:
            data_to_show = calculate_p_per_m3(
                data_to_show_original, span=self.config.split_timespan
            )
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

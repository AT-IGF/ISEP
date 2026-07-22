from dataclasses import dataclass, field


from src.common.config.configs.models.predictionsMapper.PlotSettings import (
    BarPlotSettingsModel,
    LinePlotSettingsModel,
)


@dataclass()
class PlotSettingsModel:
    BAR_STYLE_PLOT = "BAR_STYLE_PLOT"
    LINE_STYLE_PLOT = "LINE_STYLE_PLOT"

    plot_style: str = BAR_STYLE_PLOT
    line_plot_settings: LinePlotSettingsModel = field(
        default_factory=LinePlotSettingsModel
    )

    bar_plot_settings: BarPlotSettingsModel = field(
        default_factory=BarPlotSettingsModel
    )

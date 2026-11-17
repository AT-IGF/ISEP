from dataclasses import dataclass, field


from src.common.config.configs.models.predictionsMapper.PlotSettings import (
    BarPlotSettingsModel,
    LinePlotSettingsModel,
)


@dataclass()
class PlotSettingsModel:
    """Plot settings of the summarized predictions."""

    BAR_STYLE_PLOT = "BAR_STYLE_PLOT"
    """Bar."""

    LINE_STYLE_PLOT = "LINE_STYLE_PLOT"
    """Line."""

    plot_style: str | None = BAR_STYLE_PLOT
    """Plot style. The way in which the plot is presented: bar or line plot. ``None`` disables plotting;
    the summary is still saved to the output file."""

    line_plot_settings: LinePlotSettingsModel = field(
        default_factory=LinePlotSettingsModel
    )

    bar_plot_settings: BarPlotSettingsModel = field(
        default_factory=BarPlotSettingsModel
    )

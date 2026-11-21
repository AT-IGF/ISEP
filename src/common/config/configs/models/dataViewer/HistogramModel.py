from dataclasses import dataclass


@dataclass()
class HistogramModel:
    """Per-class histograms of the aggregated signal value. Every channel is handled separately."""

    MAX_OPERATION = "max"
    """max."""

    AVG_OPERATION = "avg"
    """average."""

    ALL_IN_ONE_MODE = "ALL_IN_ONE"
    """All in one."""

    ONE_BY_ONE_MODE = "ONE_BY_ONE"
    """One by one."""

    plot: bool = False
    """Plot histogram. Plots per class histograms. Every channel is handled separately."""

    operation: str = MAX_OPERATION
    """Aggregation function. Reduces the measurement of every particle in the given channel to a single
    value: ``max`` or ``avg``."""

    lower_than: float | None = None
    """Exclude lower than. Particles whose aggregated value is below the threshold are not included in
    the histogram."""

    higher_than: float | None = None
    """Exclude higher than. Particles whose aggregated value is above the threshold are not included in
    the histogram."""

    q_min: int | None = None
    """Lower percentile. Draws a reference line at the given percentile of the values."""

    q_max: int | None = None
    """Higher percentile. Draws a reference line at the given percentile of the values."""

    cutom_line: float | None = None
    """Custom line at. Draws a reference line at the given value."""

    display_mode: str = ALL_IN_ONE_MODE
    """Display mode. Show a single plot with all pollen types or one plot per pollen type. Available options: ``ALL_IN_ONE``, ``ONE_BY_ONE``"""

    display_as_grid: bool = False
    """Display as grid. All plots in one window, next to each other."""

    share_y_grid: bool = True
    """Share y. Common y axis for all plots in the grid."""

    n_cols: int = 3
    """Columns. Number of columns in the plot."""

    hist_bins: int = 100
    """Bins. Number of bins in the histogram."""

    def is_display_as_grid(self) -> bool:
        return self.display_as_grid and self.display_mode == self.ALL_IN_ONE_MODE

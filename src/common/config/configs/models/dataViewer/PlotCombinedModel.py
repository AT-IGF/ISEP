from dataclasses import dataclass


@dataclass()
class PlotCombinedModel:
    """Combined plot of the average signal of every class, with optional percentile curves."""

    plot: bool = False
    """Plot combined. Plot all classes in a single plot, as the average signal of every class."""

    q_min: int | None = None
    """Lower percentile. Draws the given percentile of the signal of every class as a dashed curve."""

    q_max: int | None = None
    """Higher percentile. Draws the given percentile of the signal of every class as a dashed curve."""

    n_cols: int = 4
    """Legend columns. Number of columns in the legend."""

    y_min: int | None = -500
    """Y axis min. Min value on the y axis, in arbitrary units (AU)."""

    y_max: int | None = 2220
    """Y axis max. Max value on the y axis, in arbitrary units (AU)."""

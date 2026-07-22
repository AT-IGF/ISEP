from dataclasses import dataclass


@dataclass()
class PlotCombinedModel:
    plot: bool = False
    q_min: int | None = None
    q_max: int | None = None
    n_cols: int = 4
    y_min: int | None = -500
    y_max: int | None = 2220

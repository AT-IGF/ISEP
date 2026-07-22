from dataclasses import dataclass


@dataclass()
class HistogramModel:
    MAX_OPERATION = "max"
    AVG_OPERATION = "avg"

    ALL_IN_ONE_MODE = "ALL_IN_ONE"
    ONE_BY_ONE_MODE = "ONE_BY_ONE"

    plot: bool = False
    operation: str = MAX_OPERATION
    lower_than: float | None = None
    higher_than: float | None = None
    q_min: int | None = None
    q_max: int | None = None
    cutom_line: float | None = None
    display_mode: str = ALL_IN_ONE_MODE
    display_as_grid: bool = False
    share_y_grid: bool = True
    n_cols: int = 3
    hist_bins: int = 100

    def is_display_as_grid(self) -> bool:
        return self.display_as_grid and self.display_mode == self.ALL_IN_ONE_MODE

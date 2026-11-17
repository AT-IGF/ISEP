from dataclasses import dataclass

from src.core.json import get_list_int_mapping
from src.core.path import PathHelper


@dataclass()
class BarPlotSettingsModel:
    """Bar plot settings, used with the bar plot style."""

    PARTICLES_PER_METER_CUBED = "P_PER_M_CUBE"
    """P/m³. Concentration of particles per cubic meter, assuming the Rapid-E flow rate of 2.8 l/min."""

    PERCENTAGE_SHARE_IN_TIMESPAN_PLOT = "PERCENTAGE_SHARE_IN_TIMESPAN"
    """Share (%) within split time span."""

    PLOT_TYPES = [PARTICLES_PER_METER_CUBED, PERCENTAGE_SHARE_IN_TIMESPAN_PLOT]

    is_months_of_expectance: bool = False
    """Months of expectance. Indicates which pollination periods are expected for a specific pollen type;
    non-pollination periods are greyed on the plot, and the highest count outside of the expected months is
    marked as a reference line. Used only with ``display_as_grid``."""

    months_of_expectance_mapping_path: str | None = None
    """Mapping file in JSON format containing the expected months of pollination of every pollen type,
    e.g. ``{"Alnus": [2, 3], "Corylus": [1, 2]}``. Months are numbered from 1 (January) to 12 (December).
    Keys have to be pollen types from ``pollen_types``. The file has to be created by the user."""

    plot_type: str = PERCENTAGE_SHARE_IN_TIMESPAN_PLOT
    """Display mode. Normalization in which the plot is displayed."""

    display_as_grid: bool = False
    """Display as grid. All plots in one window, with a separate plot for every pollen type next to each
    other."""

    n_cols: int = 3
    """Number of columns in the plot. Used only with ``display_as_grid``."""

    show_particle_count: bool = True
    """Show particle count. Adds the particle count line on the plot. Used only with ``display_as_grid``."""

    def get_months_of_expectance(self, pollen_types):
        if not self.is_months_of_expectance:
            return {}

        path_attr = "mapping_path_cache"
        mapping_attr = "mapping_attr"
        if (
            hasattr(self, path_attr)
            and getattr(self, path_attr) == self.months_of_expectance_mapping_path
            and hasattr(self, mapping_attr)
        ):
            return getattr(self, mapping_attr)

        mapping = get_list_int_mapping(
            mapping_path=self.months_of_expectance_mapping_path, ref_keys=pollen_types
        )
        setattr(self, path_attr, self.months_of_expectance_mapping_path)
        setattr(self, mapping_attr, mapping)
        return mapping

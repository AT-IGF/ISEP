from dataclasses import dataclass

from src.core.json import get_list_int_mapping
from src.core.path import PathHelper


@dataclass()
class BarPlotSettingsModel:
    PARTICLES_PER_METER_CUBED = "P_PER_M_CUBE"
    PERCENTAGE_SHARE_IN_TIMESPAN_PLOT = "PERCENTAGE_SHARE_IN_TIMESPAN"
    PLOT_TYPES = [PARTICLES_PER_METER_CUBED, PERCENTAGE_SHARE_IN_TIMESPAN_PLOT]

    is_months_of_expectance: bool = False
    months_of_expectance_mapping_path: str | None = None
    plot_type: str = PERCENTAGE_SHARE_IN_TIMESPAN_PLOT
    display_as_grid: bool = False
    n_cols: int = 3
    show_particle_count: bool = True

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

from dataclasses import dataclass

from src.core.json import get_list_int_mapping
from src.core.path import PathHelper


@dataclass()
class LinePlotSettingsModel:
    PARTICLES_PER_METER_CUBED = "P_PER_M_CUBE"
    COUNT = "COUNT"
    PLOT_TYPES = [PARTICLES_PER_METER_CUBED, COUNT]

    plot_type: str = PARTICLES_PER_METER_CUBED

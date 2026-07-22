from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer import SingleSamplePlotModel
from src.core import ConfigModelBase, PathHelper

from src.common import Consts


@dataclass()
class DataViewerConfig(ConfigModelBase):
    plots_save_path: str = "dataViewer/out"
    same_type_count: int = 2
    filter_path: str | None = None
    spectrum_plot: SingleSamplePlotModel = field(default_factory=SingleSamplePlotModel)
    lifetime_plot: SingleSamplePlotModel = field(default_factory=SingleSamplePlotModel)
    scattering_plot: SingleSamplePlotModel = field(
        default_factory=SingleSamplePlotModel
    )
    show_plots: bool = True
    """Randomizes particle type that will be processed.
    If '0' every particle will be taken
    If '0.5' every second
    Raises:
        TypeError: Value is not between 0-1
    """
    rand_0_1_frequency: float = 0
    pollen_types_to_show: list[str] = field(default_factory=list)
    module_name = "dataViewer"
    config_prop_name = "dataViewer"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/dataViewer/config.json"
        )

    def __post_init__(self):
        if 0 > self.rand_0_1_frequency > 1:
            raise TypeError(
                "'rand_0_1_frequency' must be between 0-1. Random number is generated, if set to 0 all numbers will be taken"
            )

    def get_save_path(self):
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.plots_save_path,
            raise_on_not_found=False,
        )
from dataclasses import dataclass, field
from src.common.config.configs.models.dataViewer import SingleSamplePlotModel
from src.core import ConfigModelBase, PathHelper

from src.common import Consts


@dataclass()
class DataViewerConfig(ConfigModelBase):
    """Configuration of single particle plots of the selected modalities."""

    plots_save_path: str = "dataViewer/out"
    """Directory in which the plots are saved, relative to the resources directory. Every modality is saved
    in its own subdirectory."""

    same_type_count: int = 2
    """Count of samples from the same type to be displayed."""

    filter_path: str | None = None
    """Filter path. Path to the file that will be used for samples filtration. Example filters are
    available in *resources/common/filters*."""

    spectrum_plot: SingleSamplePlotModel = field(default_factory=SingleSamplePlotModel)
    """Single particle fluorescence spectrum plot."""

    lifetime_plot: SingleSamplePlotModel = field(default_factory=SingleSamplePlotModel)
    """Single particle fluorescence lifetime plot."""

    scattering_plot: SingleSamplePlotModel = field(
        default_factory=SingleSamplePlotModel
    )
    """Single particle scattering image plot."""

    show_plots: bool = True
    """Shows the plots in separate windows. Plots are saved in ``plots_save_path`` regardless of this
    option."""

    rand_0_1_frequency: float = 0
    """Random frequency. Probability of plotting a particle after ``same_type_count`` is reached:
    ``0`` plots none, ``1`` plots all."""

    pollen_types_to_show: list[str] = field(default_factory=list)
    """Pollen types whose particles are plotted."""

    module_name = "dataViewer"
    config_prop_name = "dataViewer"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/dataViewer/config.json"
        )

    def __post_init__(self):
        if not 0 <= self.rand_0_1_frequency <= 1:
            raise ValueError("'rand_0_1_frequency' must be between 0 and 1.")

    def get_save_path(self):
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.plots_save_path,
            raise_on_not_found=False,
        )

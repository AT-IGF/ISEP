from dataclasses import dataclass, field
from src.common.tensorflow import InputModelNames
from src.core import ConfigModelBase, PathHelper, File

from src.common.config.configs.models.dataViewer import (
    LifetimeModel,
    SpectrumModel,
    ScatteringModel,
    SizeModel,
)
from src.common import Consts


@dataclass()
class AllParticlesAvgsConfig(ConfigModelBase):
    """Configuration of aggregated plots of a selected modality across many particles of every pollen type."""

    metric_to_process: str = InputModelNames.SPECTRUM
    """Modality to plot: ``spectrum``, ``lifetime``, ``scattering`` or ``size``."""

    single_type_count: int = 10
    """Same type count. Number of the same type pollen particles. Note: the given value describes the
    number of samples before potential filtering. Too high values can cause an out of memory error,
    especially for the scattering modality, where 10,000 samples per type require about 230 MB."""

    filter_path: str | None = None
    """Filter path. Path to the file that will be used for samples filtration. Example filters are
    available in *resources/common/filters*."""

    pollen_types: list[str] | None = field(default_factory=list)
    """Pollen types to show. Labeled samples directories whose particles are plotted. Required."""

    lifetime: LifetimeModel | None = field(default_factory=LifetimeModel)
    spectrum: SpectrumModel | None = field(default_factory=SpectrumModel)
    scattering: ScatteringModel | None = field(default_factory=ScatteringModel)
    size: SizeModel | None = field(default_factory=SizeModel)
    module_name = "allParticlesAvgs"
    config_prop_name = "allParticlesAvgs"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/dataViewer/config.json"
        )

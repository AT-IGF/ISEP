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
    metric_to_process: str = InputModelNames.SPECTRUM
    single_type_count: int = 10
    filter_path: str | None = None
    pollen_types: list[str] | None = field(default_factory=list)
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

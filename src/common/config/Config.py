from typing import TypeVar

from src.core import ConfigBaseAbstract, ConfigBase

from src.common.config.configs import (
    DataViewerConfig,
    AllParticlesAvgsConfig,
    PathsConfig,
    TypesConfig,
    ModelBuilderConfig,
    ModelBuilderScalerConfig,
    ModelRunnerConfig,
    PredictionsMapperConfig,
    ModelBuilderUnsupervisedConfig,
)

from src.common import Consts


class Config(ConfigBaseAbstract):
    T = TypeVar("T")
    configs = [
        DataViewerConfig,
        AllParticlesAvgsConfig,
        PathsConfig,
        TypesConfig,
        ModelBuilderConfig,
        ModelBuilderScalerConfig,
        ModelRunnerConfig,
        PredictionsMapperConfig,
        ModelBuilderUnsupervisedConfig,
    ]
    config_base = ConfigBase(
        configs, invalidate_cache_on_save=Consts.INVALIDATE_CONFIG_CACHE_ON_CHANGE
    )

    @staticmethod
    def get(config: T, refresh=False) -> T:
        return Config.config_base.try_get_config(config, refresh)

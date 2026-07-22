import logging
from dataclasses import dataclass, field
from src.core import ConfigModelBase, PathHelper

from src.common import Consts
from src.common.config.configs.models.modelRunner import (
    ProcessingModel,
    UnsupervisedModel,
)


@dataclass()
class ModelRunnerConfig(ConfigModelBase):
    model_rel_path: str | None = None
    pollen_types: list[str] = field(default_factory=list)
    processing: ProcessingModel = field(default_factory=ProcessingModel)
    types_to_predict_rel_dirs: list[str] = field(default_factory=list)
    filter_rel_path: str | None = None
    scaler_path: str | None = None
    unsupervised: UnsupervisedModel = field(default_factory=UnsupervisedModel)
    """
    'logging' library log level
    """
    log_level: str = "INFO"
    module_name: str = "modelRunner"
    config_prop_name: str = "modelRunner"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/modelRunner/config.json"
        )

    def get_threshold(self):
        return self.processing.threshold

    def log_info(self):
        logging.getLogger().info(
            f"Predictions threshold={self.processing.threshold} (any pred for given particle above)"
        )
        logging.getLogger().info(f"Output dir={self.processing.get_output_dir()}")
        return self

    def get_model_path(self):
        if self.model_rel_path is None:
            return None
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH, self.model_rel_path, raise_on_not_found=False
        )

    def get_scaler_path(self):
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.scaler_path,
            raise_message="Scaler path has to be set",
        )

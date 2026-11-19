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
    """Configuration of model inference on new measurements."""

    model_rel_path: str | None = None
    """Model path. Path to the trained model from the Model builder supervised section, relative to the
    resources directory. Required."""

    pollen_types: list[str] = field(default_factory=list)
    """Pollen types predicted by the model, in the same order as used during training, since predictions
    are mapped to class names by their index."""

    processing: ProcessingModel = field(default_factory=ProcessingModel)

    types_to_predict_rel_dirs: list[str] = field(default_factory=list)
    """Directories to predict. Directories list of folders with measurements. A root folder can be set,
    e.g. *Measurements* containing sub-folders with the measurements (*Measurements/Day1*,
    *Measurements/Day2*, ...). Paths are relative to the resources directory."""

    filter_rel_path: str | None = None
    """Filter path. Path to the file that will be used for samples filtration. Example filters are
    available in *resources/common/filters*. Note: for best match the same filter should be used for
    both the scaler and the trained model."""

    scaler_path: str | None = None
    """Scaler path. Fitted scaler file path, relative to the resources directory. Required."""

    unsupervised: UnsupervisedModel = field(default_factory=UnsupervisedModel)

    log_level: str = "INFO"
    """Log level of the Python ``logging`` library."""

    module_name = "modelRunner"
    config_prop_name = "modelRunner"

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

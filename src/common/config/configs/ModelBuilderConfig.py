from dataclasses import dataclass, field
from typing import Any
from src.core import ConfigModelBase, PathHelper, ListHelper, File

from src.common import Consts
from src.common.tensorflow import InputModelNames
from src.common.config.configs.models.modelBuilder import (
    SizeSummaryModel,
    SummaryModel,
    CalibrationModel,
    TrainParametersModel,
)

from pathlib import Path


@dataclass
class ModelBuilderConfig(ConfigModelBase):
    """Configuration of supervised CNN training, calibration and evaluation."""

    MODEL_SUFFIX = "model"
    MODEL_EXTENSION = "h5"
    REFS_EXTENSION = "tfrecord"
    KERAS_EXTENSION = "keras"

    model_save_name: str = "hello_world"
    """Train model name. The model is saved as ``<model_save_name>_model.h5``."""

    test_model_name: str | None = "hello_world_test_model"
    """Cache files namespace, stored as ``<namespace>_test_model``. Namespace under which cache files are
    created in cache dir. When another models are created samples will be taken from this namespace.
    Serves for comparison purposes between individual models. Files in cache dir are created in
    following convention: ``<namespace>_<pollen type>_test_reference_to_scale.tfrecord``."""

    excludeTypes: list[str] = field(default_factory=list)
    """Pollen types to exclude."""

    learningModels: list[str] = field(
        default_factory=lambda: InputModelNames.TRAIN_MODELS
    )
    """Input modalities. Model inputs used for training and further for prediction purposes. Size modality
    is calculated based on the scattering, no additional input is needed."""

    pollen_types_cache_rel_path: str | None = "supervised/cache"
    """Processed files cache dir. Place in which train, test, validation sets will be saved."""

    run_training: bool = True
    """Run training."""

    filter_rel_path: str | None = None
    """Filter path. Path to the file that will be used for samples filtration. Example filters are
    available in *resources/common/filters*. Note: for best match the same filter should be used for
    both the scaler and the trained model."""

    scaler_path: str | None = None
    """Scaler path. Fitted scaler file path from the Scaler tab."""

    summaries: SummaryModel = field(default_factory=SummaryModel)
    train_parameters: TrainParametersModel = field(default_factory=TrainParametersModel)
    calibration: CalibrationModel = field(default_factory=CalibrationModel)
    module_name = "modelBuilder"
    config_prop_name = "modelBuilder"
    train_file_extension = "tfrecord"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/modelBuilder/config.json"
        )

    def get_pollen_types_cache_file_path(self, suffix="") -> str | None:
        if self.pollen_types_cache_rel_path is None:
            return None

        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            f"{self.pollen_types_cache_rel_path.removesuffix('/')}/{self.model_save_name}{suffix}.{self.MODEL_EXTENSION}",
            raise_on_not_found=False,
        )

    def get_model_path(self, model_save_name=None, suffix=""):
        """
        for app to run do not set model_save_name it is preffered when values changes to check if model exists, e.g. in UI
        """
        model_name = self.model_save_name
        if model_save_name != None:
            model_name = model_save_name

        if model_name.endswith(f"_{self.MODEL_SUFFIX}"):
            model_name = model_name.removesuffix(f"_{self.MODEL_SUFFIX}")

        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            f"{self.module_name}/{model_name}_{self.MODEL_SUFFIX}{suffix}.{self.MODEL_EXTENSION}",
            raise_on_not_found=False,
        )

    def get_calibrated_model_path(self, model_save_name=None):
        return (
            self.get_model_path(
                model_save_name=model_save_name, suffix="_calibrated"
            ).removesuffix(self.MODEL_EXTENSION)
            + self.KERAS_EXTENSION
        )

    def get_model_ending(self):
        return f"_{self.MODEL_SUFFIX}.{self.MODEL_EXTENSION}"

    def get_pollen_types_cache_dir(self):
        if self.pollen_types_cache_rel_path is None:
            return None
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.pollen_types_cache_rel_path,
            raise_on_not_found=False,
        )

    def get_set_path(self, binary_dir_path, model_name, set_name, suffix=""):
        binary_base_dir = PathHelper.get_base_name(binary_dir_path)
        cache_dir = self.get_pollen_types_cache_dir()
        if cache_dir is None:
            return None
        return PathHelper.join_path(
            cache_dir,
            f"{model_name}_{binary_base_dir}_{set_name}{suffix}.{self.train_file_extension}",
        )

    def get_train_file_path(self, binary_dir_path, suffix=""):
        return self.get_set_path(binary_dir_path, self.model_save_name, "train", suffix)

    def get_validation_file_path(self, binary_dir_path, suffix=""):
        return self.get_set_path(
            binary_dir_path, self.model_save_name, "validation", suffix
        )

    def get_test_file_path(self, binary_dir_path, suffix=""):
        return self.get_set_path(binary_dir_path, self.model_save_name, "test", suffix)

    def get_test_reference_file_path(
        self, binary_dir_path, suffix="", test_model_name=None
    ):
        """
        for app to run do not set test_model_name it is preffered when values changes to check if model exists, e.g. in UI
        """
        if test_model_name == None:
            test_model_name = self.test_model_name
        test_model_name_cleaned = test_model_name.replace("_test_model", "")
        return self.get_set_path(
            binary_dir_path, test_model_name_cleaned, "test_reference", suffix
        )

    def get_learning_model_names(self, suffix=""):
        return [f"{x}{suffix}" for x in self.learningModels]

    def __post_init__(self):
        not_found_models = ListHelper.remove_elements(
            self.learningModels, InputModelNames.LEARNING_MODELS
        )
        if len(not_found_models) != 0:
            raise NotImplementedError(
                f"Input modalities not found={not_found_models}, available modalities={InputModelNames.LEARNING_MODELS}"
            )

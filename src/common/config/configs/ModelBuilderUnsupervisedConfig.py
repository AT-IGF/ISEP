from dataclasses import dataclass, field
from src.core import ConfigModelBase, PathHelper
from pathlib import Path

from src.common.config.configs.models.modelBuilderUnsupervised import VerifyModel
from src.common.config.configs.models.modelBuilderUnsupervised import (
    ClusterParameterModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised import (
    TrainParametersModel,
)
from src.common import Consts
import re
from src.common.config.configs.common.FiltersHelper import get_dir_with_filter


# @dataclass(frozen=True)
@dataclass()
class ModelBuilderUnsupervisedConfig(ConfigModelBase):
    MODEL_SUFFIX = "model"
    MODEL_EXTENSION = "tfrecord"

    model_save_name: str = "hello_unsupervised_world"
    train_parameters: TrainParametersModel = field(default_factory=TrainParametersModel)
    cluster_parameters: ClusterParameterModel = field(
        default_factory=ClusterParameterModel
    )
    verify_model: VerifyModel = field(default_factory=VerifyModel)
    model_save_name_extension = ".h5"
    train_file_extension = ".tfrecord"
    module_name = "modelBuilder"
    config_prop_name = "modelBuilderUnsupervised"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/modelBuilder/config.json"
        )

    module_path = PathHelper.join_rel_path(Consts.RESOURCES_PATH, module_name)

    def get_pollen_types_cache_dir(self) -> str | None:
        if self.train_parameters.pollen_types_cache_rel_path is None:
            return None
        return get_dir_with_filter(
            self.train_parameters.pollen_types_cache_rel_path,
            filter_rel_path=self.train_parameters.filter_rel_path,
        )

    @staticmethod
    def normalize_dub_dir(subdir):
        if not subdir.startswith("/"):
            return "/" + subdir
        return subdir

    def get_progress_match(self, new_model_name=None):
        model_name = self.model_save_name
        if new_model_name is not None:
            model_name = new_model_name
        return re.search(rf"_epoch(\d+)$", model_name)

    def is_progress_model(self, new_model_name=None):
        return self.get_progress_match(new_model_name=new_model_name) is not None

    def get_model_path(self, suffix="", new_model_name=None):
        model_name = self.model_save_name
        if new_model_name is not None:
            model_name = new_model_name

        if model_name.endswith(f"_{self.MODEL_SUFFIX}"):
            model_name = model_name.removesuffix(f"_{self.MODEL_SUFFIX}")

        match = self.get_progress_match(new_model_name=model_name)
        subdir = ""
        if match is not None:
            model_save_final_name = model_name.replace(match[0], "")
        is_final = match == None
        if not is_final:
            subdir = self.normalize_dub_dir(
                f"unsupervised/KerasTrainer/{model_save_final_name}"
            )
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH,
            f"{self.module_name}{subdir}",
            f"{model_name}{suffix}_{self.MODEL_SUFFIX}{self.model_save_name_extension}",
        )

    def get_cache_subdir(self, suffix, is_final=False):
        if self.model_save_name.endswith(f"_{self.MODEL_SUFFIX}"):
            self.model_save_name = self.model_save_name.removesuffix(
                f"_{self.MODEL_SUFFIX}"
            )

        match = self.get_progress_match()
        subdir = ""
        if "epoch" in suffix or match is not None:
            model_save_final_name = self.model_save_name
            if match is not None:
                model_save_final_name = self.model_save_name.replace(match[0], "")
            if is_final:
                self.model_save_name = model_save_final_name
            else:
                subdir = self.normalize_dub_dir(
                    f"unsupervised/KerasTrainer/{model_save_final_name}"
                )
        return subdir

    def get_model_ending(self):
        extension = PathHelper.normalize_extension(self.model_save_name_extension)
        return f"_{self.MODEL_SUFFIX}{extension}"

    def get_model_file_path(self, suffix="", is_final=False, new_model_name=None):
        """
        Args:
            suffix (str, optional): model name suffix . Defaults to "".
            is_final (bool, optional): whether should be saved as progress or the final model. Defaults to False.
            new_model_name (_type_, optional): replace name to get, e.g. if file exists. Defaults to None.

        Returns:
            _type_: model absolute path
        """
        model_name = self.model_save_name
        if new_model_name is not None:
            model_name = new_model_name
        subdir = self.get_cache_subdir(suffix=suffix, is_final=is_final)
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH,
            f"{self.module_name}{subdir}",
            f"{model_name}{suffix}_{self.MODEL_SUFFIX}{self.model_save_name_extension}",
        )

    def get_history_file_path(self, suffix="", is_final=False):
        subdir = self.get_cache_subdir(suffix=suffix, is_final=is_final)
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH,
            f"{self.module_name}{subdir}",
            f"{self.model_save_name}{suffix}_{self.MODEL_SUFFIX}_history.pkl",
        )

    def get_pollen_types_binaries_dirs(self) -> list[str] | None:
        if self.train_parameters.pollen_types_binaries_paths is None:
            return None
        paths = []
        for path in self.train_parameters.pollen_types_binaries_paths:
            if not path.startswith("/"):
                paths.append(PathHelper.join_path(Consts.RESOURCES_PATH, path))
            else:
                paths.append(path)
        return paths

    def get_train_file_path(self, binary_dir_path, suffix=""):
        binary_base_dir = PathHelper.get_base_name(binary_dir_path)
        return PathHelper.join_path(
            self.get_pollen_types_cache_dir(),
            f"{binary_base_dir}{suffix}{self.train_file_extension}",
        )

    def get_validation_file_path(self, binary_dir_path, suffix=""):
        binary_base_dir = PathHelper.get_base_name(binary_dir_path)
        return PathHelper.join_path(
            self.get_pollen_types_cache_dir(),
            f"{binary_base_dir}_validation{suffix}{self.train_file_extension}",
        )

    def __post_init__(self):
        self.model_save_name_extension = PathHelper.normalize_extension(
            self.model_save_name_extension
        )
        if self.model_save_name.endswith(
            f"_{self.MODEL_SUFFIX}{self.model_save_name_extension}"
        ):
            self.model_save_name = self.model_save_name.removesuffix(
                f"_{self.MODEL_SUFFIX}{self.model_save_name_extension}"
            )
        elif self.model_save_name.endswith(f"_{self.MODEL_SUFFIX}"):
            self.model_save_name = self.model_save_name.removesuffix(
                f"_{self.MODEL_SUFFIX}"
            )

        self.train_file_extension = PathHelper.normalize_extension(
            self.train_file_extension
        )
        train_file_extensions = [".tfrecord", ".h5"]
        if self.train_file_extension not in train_file_extensions:
            raise ValueError(
                f"Train file extension not supported. Supported extensions={', '.join(train_file_extensions)}. Recommended: .tfrecord"
            )

    def get_hdbscan_path(self):
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, f"unsupervised/hdbscan"
        )

    def get_umap_path(self):
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, f"unsupervised/umap"
        )

    def get_kmeans_path(self):
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, f"unsupervised/kmeans"
        )

    def get_latent_vectors_path(self):
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, f"unsupervised/latent_vectors"
        )

    def get_clusterer_path(self):
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, f"unsupervised/mini_batch_kmeans"
        )

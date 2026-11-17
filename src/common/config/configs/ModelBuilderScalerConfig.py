from dataclasses import dataclass, field
from src.core import ConfigModelBase, PathHelper, File

from src.common import Consts
from src.common.config.configs.common.FiltersHelper import get_dir_with_filter


@dataclass()
class ModelBuilderScalerConfig(ConfigModelBase):
    """Configuration of fitting the min-max scaler used to normalize Rapid-E measurements."""

    SAVE_FILE_EXTENSION = ".tfrecord"

    scaler_name: str | None = "scaler1"
    """Scaler custom name. The scaler is saved as ``<scaler_name>_scaler.pkl``. If not set, the name of
    the first directory in ``pollen_types_binaries_paths`` is taken."""

    pollen_types_binaries_paths: list[str] = field(default_factory=list)
    """Samples directories. Every subdirectory of the given paths is read and used for fitting the
    scaler."""

    rescale_existing_files: bool = False
    """Rescale existing files. When the scaler is fitted, it creates scaled files. If new files are added,
    the already scaled files can be rescaled with the updated scaler; otherwise only files that have not
    been scaled yet are processed."""

    scaler_save_path: str = "modelBuilder/scaler"
    """Scaler save path, relative to the resources directory. The scaler and the processed files are saved
    in the subdirectory named after the selected filter."""

    filter_rel_path: str | None = None
    """Filter path. Path to the file that will be used for samples filtration. Example filters are
    available in *resources/common/filters*. Note: for best match the same filter should be used for
    both the scaler and the trained model."""

    module_name = "modelBuilder"
    config_prop_name = "modelBuilderScaler"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/modelBuilder/config.json"
        )

    def get_save_path(self) -> File | None:
        return get_dir_with_filter(
            path=self.scaler_save_path, filter_rel_path=self.filter_rel_path
        )

    def get_filename(self, suffix=""):
        scaler_name = self.scaler_name
        if scaler_name is None:
            if len(self.pollen_types_binaries_paths) == 0:
                raise ValueError(
                    "Both 'scaler_name' and 'pollen_types_binaries_paths' cannot be None or empty"
                )
            scaler_name = PathHelper.get_base_name(self.pollen_types_binaries_paths[0])
        return f"{scaler_name}{suffix}"

    def get_file_path(self, binary_dir_path, suffix=""):
        binary_base_dir = PathHelper.get_base_name(binary_dir_path)
        return PathHelper.join_path(
            self.get_save_path(), f"{binary_base_dir}{suffix}{self.SAVE_FILE_EXTENSION}"
        )

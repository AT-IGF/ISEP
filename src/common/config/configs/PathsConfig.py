from dataclasses import dataclass
from src.core import ConfigModelBase, PathHelper

from src.common import Consts


@dataclass()
class PathsConfig(ConfigModelBase):
    """General paths shared by all ISEP modules."""

    zip_files_rel_path: str | None = None
    """Zip files path. Path in which labeled pollen types are located, relative to the resources directory.
    It should contain sub-folders that will be treated as labels. Every
    sub-folder should contain binary measurements from the Rapid-E."""

    config_prop_name = "paths"
    module_name = "general"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(Consts.RESOURCES_PATH, "/general.json")

    def get_zip_files_rel_path(self, raise_on_not_found=True):
        if self.zip_files_rel_path.startswith("/mnt"):  # handle wsl pointing to windows
            return self.zip_files_rel_path

        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.zip_files_rel_path,
            raise_on_not_found=raise_on_not_found,
            raise_message="Zip files path has to be set",
        )

from dataclasses import dataclass
from src.core import ConfigModelBase, PathHelper

from src.common import Consts


@dataclass(frozen=True)
class PathsConfig(ConfigModelBase):
    zip_files_rel_path: str | None = None
    config_prop_name = "paths"
    module_name = "general"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(Consts.RESOURCES_PATH, "/general.json")

    def get_zip_files_rel_path(self, raise_on_not_found=True):
        if self.zip_files_rel_path.startswith("/mnt"): # handle wsl pointing to windows
            return self.zip_files_rel_path
        
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.zip_files_rel_path,
            raise_on_not_found=raise_on_not_found,
            raise_message="Zip files path has to be set",
        )

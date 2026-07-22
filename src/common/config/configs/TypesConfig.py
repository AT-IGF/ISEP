from dataclasses import dataclass, field
import logging
from src.core import ConfigModelBase, PathHelper, ListHelper

from src.common import Consts


@dataclass(frozen=True)
class TypesConfig(ConfigModelBase):
    pollen_types: list[str] = field(default_factory=list)
    config_prop_name = "types"
    module_name = "general"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(Consts.RESOURCES_PATH, "/general.json")

    def get_pollen_types(self, types_to_exclude: list[str]):
        result = ListHelper.remove_elements(self.pollen_types, types_to_exclude)
        if len(result) != (len(self.pollen_types) - len(types_to_exclude)):
            excluded_but_not_found = ListHelper.get_differences(
                types_to_exclude, self.pollen_types
            )
            logging.getLogger().warning(
                f"Types to exclude={excluded_but_not_found} not found in 'pollen_types'={self.pollen_types}"
            )

        return result

    def __post_init__(self):
        duplicated_pollen_types = ListHelper.find_duplicates(self.pollen_types)
        if len(duplicated_pollen_types) != 0:
            raise KeyError(
                f"Pollen types ('pollen_types') list cannot contain duplicated values, duplicates={duplicated_pollen_types}"
            )

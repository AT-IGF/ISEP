from src.core.path import PathHelper
from src.common import Consts


def get_dir_with_filter(path, filter_rel_path):
    path = PathHelper.get_absolute_path(
        Consts.RESOURCES_PATH, path, raise_on_not_found=False
    )
    filter_name = "raw"
    if filter_rel_path is not None:
        filter_name = PathHelper.get_filename(filter_rel_path).replace(" ", "_")

    if path.endswith(filter_name):
        return path

    return PathHelper.join_absoulte_with_rel_path(path, f"/{filter_name}")

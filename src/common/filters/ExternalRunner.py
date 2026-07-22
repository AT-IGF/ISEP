import logging
import runpy
from src.core import PathHelper
from src.common.rawData.Signal import RawData
from src.common import Consts


class FilterRunner:
    def __init__(self, filter_path):
        self.filter_path = filter_path

    def __call__(self, sample: RawData):
        ns = runpy.run_path(
            self.filter_path, run_name="__main__", init_globals=globals()
        )
        return ns["filter"](sample)


def get_filter(filter_path, message_prefix=""):
    if filter_path is None:
        logging.getLogger().info(f"{message_prefix} filter not set.")
        return None

    filter_path = PathHelper.get_absolute_path(Consts.RESOURCES_PATH, filter_path)
    if PathHelper.is_file_exists(filter_path):
        logging.getLogger().info(
            f"{message_prefix} filter found under path:{filter_path}"
        )

    return FilterRunner(filter_path=filter_path)

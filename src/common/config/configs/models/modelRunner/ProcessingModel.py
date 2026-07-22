from dataclasses import dataclass
from src.core import PathHelper
from src.modelRunner.common.Consts import PROCESSED_OUTPUT_SUBDIR
from src.common import Consts


@dataclass
class ProcessingModel:
    output_dir: str = "modelRunner/out"
    file_dateformat_regex: str = "\d{4}\d{2}\d{2}\d{2}\d{2}"
    date_format_from_regex_mapping: str = "%Y%m%d%H%M"
    combined_files_filename: str | None = None
    """
    append processing results to one file, if not blank adds it by dates
    """
    add_batch_info_to_processed_file: bool = True
    threshold: float = 0.2

    def get_output_dir(self) -> str:
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH, self.output_dir, raise_on_not_found=False
        )

    def get_progress_dir(self):
        output_dir = self.get_output_dir().removesuffix("/")
        if PathHelper.get_base_name(output_dir) == PROCESSED_OUTPUT_SUBDIR:
            return output_dir
        return f"{output_dir}/{PROCESSED_OUTPUT_SUBDIR}"

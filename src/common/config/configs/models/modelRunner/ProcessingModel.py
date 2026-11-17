from dataclasses import dataclass
from src.core import PathHelper
from src.modelRunner.common.Consts import PROCESSED_OUTPUT_SUBDIR
from src.common import Consts


@dataclass
class ProcessingModel:
    """Input file processing and output settings of model inference."""

    output_dir: str = "modelRunner/out"
    """Save directory. Directory under which the output with 0 threshold will be saved (an input for the
    predictions mapper), relative to the resources directory."""

    file_dateformat_regex: str = r"\d{4}\d{2}\d{2}\d{2}\d{2}"
    """Filename regex date. Regex representation of the date within the file name. For example, for the
    file name ``D_001060749_202006160650`` the regex is ``\d{4}\d{2}\d{2}\d{2}\d{2}``. Every file name
    has to contain exactly one match."""

    date_format_from_regex_mapping: str = "%Y%m%d%H%M"
    """Filename regex date mapping. Python date format of the regex representation. For example, for
    ``\d{4}\d{2}\d{2}\d{2}\d{2}`` the mapping is ``%Y%m%d%H%M``."""

    combined_files_filename: str | None = None
    """Output filename. Predictions of all dates are appended to a single file
    ``tr_0_<combined_files_filename>.csv``. When not set, a separate file is created for each date."""

    add_batch_info_to_processed_file: bool = True
    """Adds the save time of every batch as a comment line to the progress file."""

    threshold: float = 0.2
    """Info threshold. Displays a live summary of the number of detected particles, i.e. particles whose
    highest class probability reaches the threshold. Just informational: files are saved with threshold 0,
    and the aggregated threshold is applied in the predictions mapper."""

    def get_output_dir(self) -> str:
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH, self.output_dir, raise_on_not_found=False
        )

    def get_progress_dir(self):
        output_dir = self.get_output_dir().removesuffix("/")
        if PathHelper.get_base_name(output_dir) == PROCESSED_OUTPUT_SUBDIR:
            return output_dir
        return f"{output_dir}/{PROCESSED_OUTPUT_SUBDIR}"

import logging
import re
from datetime import datetime

from src.common import Consts
from src.common.config import Config, ModelRunnerConfig
from src.core import PathHelper, File, read_dataset, is_blank

from src.modelRunner.dataProcessor.models import FilesToProcess
from src.modelRunner.dataProcessor.progressHandler import ProgressHandler


class DataProcessor:
    def __init__(self, progress_handler: ProgressHandler):
        self._config = Config().get(ModelRunnerConfig)
        self._dates_to_process_count = 0
        self._files_to_process_count = 0
        self._progress_handler = progress_handler
        self._logger = logging.getLogger()
        self.is_nth_file_warn_logged = False

    def get_all_files_from_dir_by_date(self) -> dict[str, File]:
        files: list[File] = []
        for dir in self._config.types_to_predict_rel_dirs:
            if dir.startswith("/mnt"):  # running windoes files from wsl
                files_path = dir
            else:
                files_path = PathHelper.join_rel_path(Consts.RESOURCES_PATH, dir)
            self._logger.info(f"Searching data under path={files_path}")
            files += read_dataset(files_path).files
        regex = re.compile(self._config.processing.file_dateformat_regex)
        files_by_date: dict[str, File] = {}
        for file in files:
            regex_result: list[str] = regex.findall(file.filename)
            if len(regex_result) != 1:
                raise IndexError(
                    "Number of results from regex is not equal to 1. "
                    + f"Regex results count={len(regex_result)}, regex={self._config.processing.file_dateformat_regex}, results={regex_result}, filename={file.filename}"
                )
            processed_date = datetime.strptime(
                regex_result[0], self._config.processing.date_format_from_regex_mapping
            )
            file_date = processed_date.strftime("%Y%m%d")
            if file_date in files_by_date.keys():
                files_by_date[file_date].append(file)
            else:
                files_by_date[file_date] = [file]

        for files in files_by_date:
            files_by_date[files] = sorted(
                files_by_date[files], key=lambda x: x.filename
            )

        self._logger.info(f"Identified dates: { files_by_date.keys()}")

        return files_by_date

    def every_nth(self, lst, n):
        return lst[n - 1 :: n]

    def get_files_to_predict(self, every_nth_file: int = None) -> list[FilesToProcess]:
        files_sets_by_date: dict[str, File] = self.get_all_files_from_dir_by_date()

        files_to_process: list[FilesToProcess] = []
        for date, files_by_date in files_sets_by_date.items():
            progress_file_path = self._progress_handler.get_progress_file(date)
            files = files_by_date
            is_partially_processed = False
            if PathHelper.is_file_exists(progress_file_path):
                is_partially_processed = True
                files = self._progress_handler.get_partially_processed_files(
                    deteced_files=files, processed_file_path=progress_file_path
                )
                if len(files) == 0:
                    self._logger.info(
                        f"All files for date={date} were processed. Date will be skipped."
                    )

            if every_nth_file is not None:
                if self.is_nth_file_warn_logged == False:
                    self._logger.warning(
                        f"Every nth file is taken due to 'every_nth_file' set. every_nth_file={every_nth_file}"
                    )
                    self.is_nth_file_warn_logged = True
                files = self.every_nth(files, every_nth_file)

            files_to_process.append(
                FilesToProcess(
                    files=files,
                    date=datetime.strptime(date, "%Y%m%d"),
                    progress_file_path=progress_file_path,
                    output_dir=self._config.processing.get_output_dir(),
                    output_file_extension=".csv",
                    is_partially_processed=is_partially_processed,
                )
            )
        self._progress_handler.update_progress_count(files_to_process)

        return sorted(files_to_process, key=lambda x: x.date)

    def handle_combined_file_processing(
        self, idx: int, files_to_process: FilesToProcess
    ):
        """If predictions are saved to combined files sets 'is_partially_processed' to true"""
        if idx != 0 and DataProcessor.is_combined_file(self._config):
            files_to_process.is_partially_processed = True

    @staticmethod
    def is_combined_file(config: ModelRunnerConfig):
        return not is_blank(config.processing.combined_files_filename)

    @staticmethod
    def get_files_to_process_save_path(
        files_to_process: FilesToProcess,
        config: ModelRunnerConfig,
        threshold: float = 0,
    ):
        """Returns save path of predicted values with specific threshold
        If 'combined_files_filename' is not None predicted values will be saved into one file
        Else predicted values will be saved into separate files based on dates
        """
        output_dir = files_to_process.output_dir
        filename_suffix = files_to_process.date.strftime("%Y%m%d")
        if DataProcessor.is_combined_file(config):
            filename_suffix = config.processing.combined_files_filename
        filename_extension = PathHelper.normalize_extension(
            files_to_process.output_file_extension
        )
        filename = f"tr_{threshold}_{filename_suffix}{filename_extension}"

        return PathHelper.join_path(output_dir, filename)

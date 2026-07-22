from datetime import datetime
import logging
from src.core import PathHelper, File, write_data_list, read_file_by_path
from src.common.config import Config, ModelRunnerConfig
from src.modelRunner.common.Consts import (
    PROCESSED_FILE_PREFIX,
    PROCESSED_FILE_EXTENSION,
    PROCESSED_FILE_COMMENT_PREFIX,
    PROCESSED_OUTPUT_SUBDIR,
)
from src.modelRunner.dataProcessor.models import FilesToProcess
from collections import defaultdict


class ProgressHandler:
    def __init__(self):
        self._config = Config.get(ModelRunnerConfig)
        self._logger = logging.getLogger()
        self._processed_files_count = 0
        self._files_to_process_count = 0
        self._dates_to_process_count = 0
        self._combined_files_filename = self._config.processing.combined_files_filename
        self._processed_file_lines = None

    @property
    def dates_to_process_count(self):
        return self._dates_to_process_count

    def get_progress_file_filename(self, processed_file_date: str):
        """
        Returns prediction save path
        If config 'combined_files_filename' is given output will be combined into one file
        Else multiple files by date will be created
        """
        processed_file_filename = processed_file_date
        if self._combined_files_filename is not None:
            processed_file_filename = self._combined_files_filename

        return f"{PROCESSED_FILE_PREFIX}{processed_file_filename}{PROCESSED_FILE_EXTENSION}"

    def get_progress_file(self, date):
        return f"{self._config.processing.get_progress_dir()}/{self.get_progress_file_filename(date)}"

    def group_file_paths(self, paths):
        groups = defaultdict(list)
        for path in paths:
            directory = PathHelper.get_dirs(path)
            groups[directory].append(path)
        return groups

    def get_partially_processed_files(
        self, deteced_files: list[File], processed_file_path: str
    ):
        files: list[File] = []
        if self._combined_files_filename is not None:
            if self._processed_file_lines is None:
                processed_file_lines: list[str] = read_file_by_path(
                    processed_file_path
                ).lines(lines_to_ignore_prefix=PROCESSED_FILE_COMMENT_PREFIX)
                self._processed_file_lines = processed_file_lines
            processed_file_lines = self._processed_file_lines
        else:
            processed_file_lines: list[str] = read_file_by_path(
                processed_file_path
            ).lines(lines_to_ignore_prefix=PROCESSED_FILE_COMMENT_PREFIX)
        file_groups = self.group_file_paths(processed_file_lines)
        for file in deteced_files:
            if file.path not in file_groups.keys():
                files.append(file)
                continue

            if file.get_file_path() in file_groups[file.path]:
                self._logger.debug(
                    f"File already processed, skipped. File={file.get_file_path()}, process saved in file='{processed_file_path}'"
                )
                continue
            files.append(file)
        return files

    def update_progress_count(self, files_to_process_list: list[FilesToProcess]):
        self._dates_to_process_count = len(files_to_process_list)
        self._files_to_process_count = sum(
            [len(x.files) for x in files_to_process_list]
        )

        logging.getLogger().info(
            f"Files to process count={self._files_to_process_count}"
        )

    def save_progress(
        self, files_to_process: FilesToProcess, processed_files: list[File]
    ):
        save_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        data_prefix = (
            f"{PROCESSED_FILE_COMMENT_PREFIX} batch saved at = {save_time} (UTC)"
        )
        if self._config.processing.add_batch_info_to_processed_file:
            data = [data_prefix]
        else:
            data = []
        data += [x.get_file_path() for x in processed_files]

        write_data_list(path=files_to_process.progress_file_path, data=data)
        files_to_process.is_partially_processed = True
        self.summary(processed_files)

    def summary(self, processed_files: list[File]):
        self._processed_files_count += len(processed_files)
        self._logger.info(
            f"Processed files count={self._processed_files_count}/{self._files_to_process_count}"
        )

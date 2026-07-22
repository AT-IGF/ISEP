import pandas as pd
from dataclasses import asdict
import logging
from src.core import PathHelper
from src.common.config import Config, ModelRunnerConfig
from src.common.pandas.DataFrameHelper import write_data_frame_to_csv
from src.modelRunner.summaries.SummaryBase import SummaryBase
from src.modelRunner.summaries.models import ParticlesCountModel

from src.modelRunner.common.Consts import (
    SUMMARY_FILENAME_PREFIX,
    PROCESSED_OUTPUT_SUBDIR,
)


class ParticlesCountSummary(SummaryBase[ParticlesCountModel]):
    def __init__(self, threshold: float):
        self._threshold = threshold
        self._particles_data_list: list[dict] = []
        self._logger = logging.getLogger()
        self._config = Config.get(ModelRunnerConfig)
        self._save_path = self.get_save_path()
        self._if_file_exists = PathHelper.is_file_exists(self._save_path)
        self._add_header = not self._if_file_exists

        self._threshold_count = 0
        self._no_threshold_count = 0
        self._total_count = 0

        self.on_init()

    def get_save_path(self):
        filename = f"{SUMMARY_FILENAME_PREFIX}{self._config.processing.combined_files_filename}_tr_{self._threshold}_{len(self._config.types_to_predict_rel_dirs)}.csv"
        return f"{self._config.processing.get_progress_dir()}/{filename}"

    def on_init(self):
        if not self._if_file_exists:
            return

        df = pd.read_csv(self._save_path)
        self._threshold_count = df[f"identified_threshold_{self._threshold}"].iloc[-1]
        self._no_threshold_count = df["identified_no_threshold"].iloc[-1]
        self._total_count = df["total"].iloc[-1]

        self._logger.info(f"Progress count restored form path={self._save_path}")
        self.print_summary()

    def on_measurement(self, model: ParticlesCountModel):
        self._threshold_count += model.with_threshold_count
        self._no_threshold_count += model.no_threshold_count
        self._total_count += model.total_count

        self.print_summary()

        write_data_frame_to_csv(
            path=self._save_path,
            data=[self.get_particles_data(model, self._threshold)],
            add_header=self._add_header,
        )
        self._add_header = False

    def print_summary(self):
        self._logger.info(
            f"Particles: identified_tr_{self._threshold}={self._threshold_count}, identified_tr_0={self._no_threshold_count}, total={self._total_count}"
        )

    def summary(self):
        pass

    def get_particles_data(self, model: ParticlesCountModel, threshold: float):
        return {
            f"identified_threshold_{threshold}": self._threshold_count,
            "identified_no_threshold": self._no_threshold_count,
            "total": self._total_count,
        }

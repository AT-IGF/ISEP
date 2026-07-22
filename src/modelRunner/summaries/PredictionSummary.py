from src.common.config import Config, ModelRunnerConfig
from src.common.pandas.DataFrameHelper import write_data_frame_to_csv
from src.modelRunner.dataProcessor import DataProcessor
from src.modelRunner.dataProcessor.models import FilesToProcess
from src.modelRunner.predictions import Prediction
from src.modelRunner.summaries.SummaryBase import SummaryBase


class PredictionSummary(SummaryBase[list[Prediction]]):
    def __init__(self, files_to_process: FilesToProcess):
        self._y_preds_count = 0
        self._files_to_process = files_to_process
        self._config = Config.get(ModelRunnerConfig)
        
    @property
    def y_preds_count(self):
        return self._y_preds_count

    def on_init(self):
        raise NotImplementedError(self._message)

    def on_measurement(self, measurement: list[Prediction], add_file_header=False):
        save_path = DataProcessor.get_files_to_process_save_path(files_to_process=self._files_to_process,
                                                                 config=self._config)
        
        write_data_frame_to_csv(path=save_path,
                data=[pred.as_dict() for pred in measurement],
                add_header=add_file_header)
        self._y_preds_count = len(measurement)

    def summary(self):
        pass
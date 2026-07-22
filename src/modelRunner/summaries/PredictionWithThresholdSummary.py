import numpy as np
import pandas as pd
from collections import Counter
import logging
from src.common.config import Config, ModelRunnerConfig
from src.common.predictions.Thresholds import is_any_pred_within_threshold
from src.modelRunner.dataProcessor.models import FilesToProcess
from src.modelRunner.predictions import Prediction
from src.modelRunner.summaries.SummaryBase import SummaryBase


class PredictionWithThresholdSummary(SummaryBase[list[Prediction]]):
    def __init__(self, files_to_process: FilesToProcess, threshold: float):
        self._files_to_process = files_to_process
        self._threshold = threshold
        self._y_preds_tr_count = 0
        self._config = Config.get(ModelRunnerConfig)
        self._logger = logging.getLogger()
        self._preds_frames = []
        

    @property
    def y_preds_tr_count(self):
        return self._y_preds_tr_count
    
    def on_init(self):
        if self._threshold == 0:
            return

    def predictions_to_types(self, y_preds_threshold: list[Prediction]):
        if len(y_preds_threshold) == 0:
            return
        
        preds_counter = Counter(np.array([x.predictions for x in y_preds_threshold]).argmax(axis=1))
        preds_fame = {}
        for idx, pollen_type in enumerate(self._config.pollen_types):
            if idx in preds_counter.keys():
                preds_fame[pollen_type] = preds_counter[idx]
            else:
                preds_fame[pollen_type] = 0
        self._preds_frames.append(preds_fame)

    def on_measurement(self, measurement: list[Prediction]):
        # if self._threshold == 0:
        #     return
        
        y_preds_threshold: list[Prediction] = [y_pred for y_pred in measurement if is_any_pred_within_threshold(y_pred.predictions, self._threshold)]
        self.predictions_to_types(y_preds_threshold)
        
        self._y_preds_tr_count = len(y_preds_threshold)

    def summary(self):
        # if self._threshold == 0:
        #     return
        
        if len(self._preds_frames) == 0:
            return
        
        self._logger.info(f"tr={self._threshold} preds (for processed date): \n{pd.DataFrame(self._preds_frames).sum().to_frame().transpose()}")
    
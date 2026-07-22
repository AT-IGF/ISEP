import pickle
import tensorflow as tf
from src.common.config import Config, ModelBuilderUnsupervisedConfig
import logging
from src.core import PathHelper
import re


class CustomCheckpointWithHistory(tf.keras.callbacks.Callback):
    def __init__(self, initial_history=None, save_every=5):
        super().__init__()
        self._config = Config.get(ModelBuilderUnsupervisedConfig)
        self.history = initial_history.copy() if initial_history else {}
        self.save_every = save_every
        self.logger = logging.getLogger()
        self._epoch_suffix = "_epoch"
        self._metrics_initialized = False

    def _ensure_metrics_initialized(self, logs):
        if not self._metrics_initialized:
            for metric in logs.keys():
                if metric not in self.history:
                    self.history[metric] = []
            self._metrics_initialized = True

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self._ensure_metrics_initialized(logs)

        for metric, value in logs.items():
            self.history[metric].append(value)

        if (epoch + 1) % self.save_every == 0:
            model_path = self._config.get_model_file_path(
                suffix=f"{self._epoch_suffix}{epoch+1}"
            )
            self.model.save(model_path)

            history_path = self._config.get_history_file_path(
                suffix=f"{self._epoch_suffix}{epoch+1}"
            )
            with open(history_path, "wb") as f:
                pickle.dump(self.history, f)

            self.logger.info(
                f"Saved model and history at epoch {epoch+1}. model_path={model_path}, history_path={history_path}"
            )

    def save_fully_trained_model(self, final_model, final_history=None):
        """Manual save method to persist final model and merged history"""
        # Merge with final history if provided
        try:
            if final_history:
                full_history_len = len(final_history["learning_rate"])
                loaded_history_len = len(self.history)
                epochs_to_add = full_history_len - loaded_history_len
                if epochs_to_add == 0:
                    return
                else:
                    for metric, values in {
                        key: value[-epochs_to_add:]
                        for key, value in final_history.items()
                    }.items():
                        self.history.setdefault(metric, []).extend(values)
        except Exception as e:
            self.logger.error("Final plot not saved", e)

        try:
            model_path = self._config.get_model_file_path(is_final=True)
            history_path = self._config.get_history_file_path(is_final=True)
            final_model.save(model_path)
        except Exception as e:
            self.logger.error("Final model issue while saving", e)
            self.logger.warning("trying to save in root as 'backup_model.h5'", e)
            final_model.save("backup_model.h5")

        try:
            import pandas as pd

            history_df = pd.DataFrame(self.history)
            history_df.to_csv(history_path + ".csv", index=False)
        except Exception:
            print("NOT SAVED")

        with open(history_path, "wb") as f:
            pickle.dump(self.history, f)

    def get_last_epoch(self):
        match = re.search(rf"_epoch(\d+)$", self._config.model_save_name)
        last_epoch = 0
        if match is not None:
            last_epoch = int(match.group(1))
            self.logger.info(
                f"Last epoch retrieved from model_save_name={self._config.model_save_name}. Initial epoch={last_epoch} will be set"
            )
        return last_epoch

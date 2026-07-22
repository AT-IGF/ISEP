import logging
import joblib
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import tensorflow as tf
from collections import Counter

from src.core.plots.plotting_utils import plt_show
from src.modelBuilder.keras.callbacks import LogCallback

from src.modelBuilder.keras.KerasInputModelsCombiner import create_model
from src.modelBuilder.keras.models import TrainedModel
from src.common.config import Config, ModelBuilderConfig
from src.modelBuilder.keras.helpers import SupervisedTfParser, TfrecordGenerator
from src.modelBuilder.keras.helpers import get_batch_size


class KerasTrainer:
    def __init__(
        self,
        pollen_types: list[str],
        binary_dir_paths: list[str],
        batch_size: int | None = None,
    ):
        self._pollen_types = pollen_types
        self._config = Config.get(ModelBuilderConfig)
        self._generator = TfrecordGenerator(
            parser=SupervisedTfParser(self._config.learningModels),
            get_train_file_path=self._config.get_train_file_path,
            get_validation_file_path=self._config.get_validation_file_path,
            get_test_file_path=self._config.get_test_file_path,
            binary_dir_paths=binary_dir_paths,
            batch_size=batch_size,
        )
        self._batch_size = self._generator._batch_size
        self._logger = logging.getLogger()

    @staticmethod
    def show_history_plot(history):
        pd.DataFrame(history.history).plot()
        plt.title(f"Loss curves")
        plt_show(plt.gcf())
        plt.close()

    def get_steps_per_epoch(self, batch_size, total_samples):
        if batch_size is None:
            batch_size = get_batch_size(batch_size)

        steps_per_epoch = total_samples // batch_size
        # If there are leftover samples, add 1 step to include them:
        if total_samples % batch_size != 0:
            steps_per_epoch += 1
        return steps_per_epoch

    def get_samples_count_and_weights(self):
        counter = Counter()
        total_samples = 0
        for _, labels in self._generator.get_train_dataset(
            repeat=False
        ).as_numpy_iterator():
            counter.update(np.argmax(labels, axis=-1))
            total_samples += len(labels)

        class_count = len(self._pollen_types)
        t_params = self._config.train_parameters
        class_weights = {
            cls: (
                total_samples / (class_count * count)
                if t_params.sampling_strategy == t_params.ALING_WEIGHTS_STRATEGY
                else 1
            )
            for cls, count in counter.items()
        }
        self._logger.info(f"Total samples to train: {total_samples}")
        self._logger.info(f"Sampling strategy: {t_params.sampling_strategy}")
        self._logger.info(f"Class weights: {class_weights}")
        return total_samples, class_weights

    def train_model(self, espochs: int, verbose: int = 1) -> TrainedModel:
        newModel = create_model(self._pollen_types)

        t_params = self._config.train_parameters

        total_samples, class_weights = self.get_samples_count_and_weights()
        if total_samples == 0:
            self._logger.warning(f"No samples to train. Training skipped.")
            return
        callbacks = [LogCallback(self._batch_size, espochs, total_samples)]
        if t_params.lr_reducer.enabled:
            lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_accuracy",
                factor=t_params.lr_reducer.factor,
                patience=t_params.lr_reducer.patience,
                min_lr=t_params.lr_reducer.min_lr,
                min_delta=t_params.lr_reducer.min_delta,
            )
            callbacks.append(lr_reducer)

        if t_params.early_stopping.enabled:
            early_stopping = tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                min_delta=t_params.early_stopping.min_delta,
                patience=t_params.early_stopping.patience,
                restore_best_weights=True,
            )
            callbacks.append(early_stopping)
        train_dataset = self._generator.get_train_dataset()

        if t_params.buffer_size_mode == t_params.ALL_SAMPLES_BUFFER_MODE:
            self._logger.info(
                f"Buffer size mode is set to {t_params.ALL_SAMPLES_BUFFER_MODE}, new buffer_size={total_samples}."
            )
            self._generator.set_buffer_size(
                total_samples
            )  # take all dataset at once for better training, cons: RAM consumption
            # elif t_params.custom_buffer_size == t_params.CUSTOM_BUFFER_MODE:
        elif t_params.buffer_size_mode == t_params.CUSTOM_BUFFER_MODE:
            self._logger.info(
                f"Buffer size mode is set to {t_params.CUSTOM_BUFFER_MODE}, new buffer_size={t_params.custom_buffer_size}."
            )
            self._generator.set_buffer_size(t_params.custom_buffer_size)
        history = newModel.fit(
            train_dataset,
            epochs=espochs,
            verbose=verbose,
            validation_data=self._generator.get_validation_dataset(),
            callbacks=callbacks,
            steps_per_epoch=self.get_steps_per_epoch(
                self._batch_size, total_samples=total_samples
            ),
            class_weight=class_weights,
        )

        config = Config.get(ModelBuilderConfig)

        model_path = config.get_model_path()
        logging.getLogger().info(f"Saving trained model under path: {model_path}")
        newModel.save(model_path)

        if config.summaries.run_summaries == True:
            self.show_history_plot(history)

        return TrainedModel(model=newModel, dataset=self._generator)

    def read_model(self):
        config = Config.get(ModelBuilderConfig)
        model_path = config.get_model_path()
        logging.getLogger().info(f"Loading model from path: {model_path}")
        model = tf.keras.models.load_model(model_path)
        return TrainedModel(model, dataset=self._generator)

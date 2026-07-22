from collections import Counter
import logging
from matplotlib import pyplot as plt
import tensorflow as tf
import h5py
import pickle

from src.core.plots.plotting_utils import plt_show
from src.modelBuilder.keras.callbacks import LogCallback
from src.core import PathHelper

from src.common.config import Config, ModelBuilderUnsupervisedConfig
from src.modelBuilder.keras.models import TrainedModel
from src.modelBuilder.keras.helpers import (
    CustomCheckpointWithHistory,
    DataGenerator,
    Hdf5Generator,
    TfrecordGenerator,
    UnsupervisedTfParser,
)
from src.modelBuilder.keras.KerasUnsupervisedModelsCombiner import create_model
from src.modelBuilder.keras.helpers import get_batch_size


class KerasUnsupervisedTrainer:
    def __init__(self, binary_dir_paths, batch_size=None):
        self._config = Config.get(ModelBuilderUnsupervisedConfig)
        self._dataset = []
        self._divider = 1
        self._binary_dir_paths = binary_dir_paths
        self._logger = logging.getLogger()
        self._batch_size = batch_size
        self._generators: list[DataGenerator] = [
            TfrecordGenerator(
                parser=UnsupervisedTfParser(
                    self._config.train_parameters.learningModels
                ),
                get_train_file_path=self._config.get_train_file_path,
                get_validation_file_path=self._config.get_train_file_path,
                binary_dir_paths=binary_dir_paths,
                batch_size=batch_size,
            ),
            Hdf5Generator(binary_dir_paths=binary_dir_paths, batch_size=batch_size),
        ]
        self.trained_model = None

    def show_history_plot(self, history=None):
        if history == None or self._config.verify_model.show_history_plot == False:
            return
        logging.getLogger().info(
            "Plotting history plot. To turn it off set 'verify_model.show_history_plot to false."
        )
        import matplotlib

        matplotlib.use("TkAgg")

        epochs = range(1, len(history["learning_rate"]) + 1)
        for key, values in history.items():
            if "size" in key:
                continue
            linestyle = "-"
            linewidth = 2
            if key.endswith("_mse"):
                linestyle = "--"
            elif key.endswith("_mae"):
                linestyle = ":"
            elif key.startswith("val"):
                linewidth = 3
            plt.plot(
                epochs, values, label=key, linestyle=linestyle, linewidth=linewidth
            )

        plt.legend()
        plt.grid(True)
        plt.xlabel("Epochs")
        plt.ylabel("Metric Value")
        plt_show(plt.gcf())
        # plt.close()

    def get_trained_model(self):
        model, history, is_loaded = self.get_keras_model()
        return model

    def get_keras_model(self):
        custom_objects = {
            # For losses (if any MSE-based losses are used)
            "mse": tf.keras.losses.mse,
            # For metrics (critical for your model)
            "lifetime_unsup_decoder_mse": tf.keras.metrics.MeanSquaredError,
            "scattering_unsup_decoder_mse": tf.keras.metrics.MeanSquaredError,
            "size_decoder_mse": tf.keras.metrics.MeanSquaredError,
            "spectrum_unsup_decoder_mse": tf.keras.metrics.MeanSquaredError,
        }
        logger = logging.getLogger()
        history = None
        is_loaded = False
        if PathHelper.is_file_exists(self._config.get_model_file_path()):
            logger.info(
                f"Training model found. Retrieving..., file path={self._config.get_model_file_path()}"
            )
            model: tf.keras.Sequential = tf.keras.models.load_model(
                self._config.get_model_file_path(), custom_objects=custom_objects
            )
            with open(self._config.get_history_file_path(), "rb") as f:
                history = pickle.load(f)
            is_loaded = True
            self.trained_model = model
        else:
            logger.info(f"Training model NOT found. Creating a new one...")
            model = create_model(self._config)
        return model, history, is_loaded

    # def get_total_training_samples(self):
    #     total = 0
    #     for path in self._binary_dir_paths:
    #         train_path = self._config.get_train_file_path(binary_dir_path=path)
    #         with h5py.File(train_path, "r") as f:
    #             total += len(f[0])
    #     self._logger.info(f"Total samples to train: {total}")
    #     return total

    def get_total_training_samples(self):
        generator = self._generators[0]
        self._logger.info(f"Calculating total training samples count")
        total_samples = 0
        for _, labels in generator.get_train_dataset(repeat=False).as_numpy_iterator():
            total_samples += len(next(iter(labels.values())))

        self._logger.info(f"Total samples to train: {total_samples}")
        # self._logger.warning(f"Total samples to train: 298973")
        return total_samples

    def get_steps_per_epoch(self, batch_size, total_samples):
        if batch_size is None:
            self._batch_size = get_batch_size(batch_size)

        steps_per_epoch = total_samples // self._batch_size
        # If there are leftover samples, add 1 step to include them:
        if total_samples % self._batch_size != 0:
            steps_per_epoch += 1
        return steps_per_epoch

    def yield_dataset_from_path(
        self, path, batch_size, suffixes=["_input", "_decoder"], column_names=None
    ):
        if not PathHelper.is_file_exists(path):
            raise ValueError(f"File under path does not exists', path='{path}'")
        if PathHelper.get_extension(path) != self._config.train_file_extension:
            raise ValueError(
                f"Path extension is not equal to 'train_file_extension', path='{path}', 'train_file_extension'='{self._config.train_file_extension}'"
            )
        for data_generator in self._generators:
            if self._config.train_file_extension in data_generator.extension:
                for data in data_generator.yield_dataset_from_path(
                    path, batch_size, suffixes, column_names=None
                ):
                    yield {
                        k: v.numpy() for k, v in data.items()
                    }  # .numpy() - load to RAM once, problem with GPU spikes during dataset iteration

    def get_datasets(self) -> list[tf.data.TFRecordDataset]:
        train_dataset = []
        validation_dataset = []
        is_generator_implemented = False
        for data_generator in self._generators:
            if self._config.train_file_extension in data_generator.extension:
                data_generator.verify_validation_set_leaks_if_enabled()
                train_dataset = data_generator.get_train_dataset()
                validation_dataset = data_generator.get_validation_dataset()
                is_generator_implemented = True
                break

        if not is_generator_implemented:
            raise ValueError(
                f"Unknown 'train_file_extension' extension. Current={self._config.train_file_extension}. Expected={', '.join([x.extension for x in self._generators])}"
            )

        return train_dataset, validation_dataset

    def get_samples_count(self):
        total_samples = 0
        for _, labels in self._generator.get_train_dataset(
            repeat=False
        ).as_numpy_iterator():
            total_samples += len(labels)

        return total_samples

    def get_callbacks(self, epochs, total_samples):
        t_params = self._config.train_parameters
        callbacks = [LogCallback(self._batch_size, epochs, total_samples)]
        if t_params.lr_reducer.enabled:
            lr_reducer = tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
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

        return callbacks

    def train_model(self, epochs: int, verbose: int = 1) -> TrainedModel:
        t_params = self._config.train_parameters

        model, loaded_history, is_loaded = self.get_keras_model()
        checkpoint_callback = CustomCheckpointWithHistory(
            initial_history=loaded_history
        )

        initial_epoch = checkpoint_callback.get_last_epoch()
        if is_loaded and initial_epoch == 0:
            self._logger.warning(
                f"Model is already fully trained. Training skipped. If you want to continue training specify model start epoch in your filename. Convention: <model_name>_epoch<initial_epoch>_model"
            )
            return

        total_samples = self.get_total_training_samples()
        if total_samples == 0:
            self._logger.warning(f"No samples to train. Training skipped.")
            return
        steps_per_epoch = self.get_steps_per_epoch(
            self._batch_size, total_samples=total_samples
        )

        callbacks = self.get_callbacks(epochs=epochs, total_samples=total_samples)
        callbacks.append(checkpoint_callback)

        train_dataset, validation_dataset = self.get_datasets()
        history = model.fit(
            train_dataset,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
            initial_epoch=initial_epoch,
            verbose=verbose,
            validation_data=validation_dataset,
            callbacks=callbacks,
        )

        checkpoint_callback.save_fully_trained_model(
            final_model=model, final_history=history.history
        )

        self.show_history_plot(checkpoint_callback.history)

        self.trained_model = TrainedModel(model=model, dataset=self._dataset)

        return self.trained_model

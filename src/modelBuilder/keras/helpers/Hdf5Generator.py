import h5py
import logging
from src.common.config import Config, ModelBuilderUnsupervisedConfig
import tensorflow as tf
from src.common.tensorflow import InputModelNames
from src.modelBuilder.keras.helpers import get_buffer_size
from src.modelBuilder.keras.helpers.abstractions import DataGenerator


class Hdf5Generator(DataGenerator):
    def __init__(self, binary_dir_paths, batch_size=None):
        self._config = Config.get(ModelBuilderUnsupervisedConfig)
        self._logger = logging.getLogger()
        self._batch_size = batch_size
        self._binary_dir_paths = binary_dir_paths
        self.with_validation_dataset_yieldoutput_signature = (
            self.get_shapes(suffix="_input"),
            self.get_shapes(suffix="_decoder"),
        )

    @property
    def extension(self) -> str:
        return [".h5"]

    @staticmethod
    def to_decoder_name(name, suffix=""):
        return name + suffix

    def get_shapes(self, suffix=""):
        input_shapes = {
            self.to_decoder_name(InputModelNames.SPECTRUM_UNSUP, suffix): tf.TensorSpec(
                shape=(None, 32, 8)
            ),
            self.to_decoder_name(
                InputModelNames.SCATTERING_UNSUP, suffix
            ): tf.TensorSpec(shape=(None, 120, 24)),
            self.to_decoder_name(InputModelNames.LIFETIME_UNSUP, suffix): tf.TensorSpec(
                shape=(None, 64, 4)
            ),
            self.to_decoder_name(InputModelNames.SIZE, suffix): tf.TensorSpec(
                shape=(None,)
            ),
            self.to_decoder_name(InputModelNames.TIME_UNSUP, suffix): tf.TensorSpec(
                shape=(None,)
            ),
        }

        ordered_input_shapes = {
            self.to_decoder_name(key, suffix): input_shapes[
                self.to_decoder_name(key, suffix)
            ]
            for key in self._config.train_parameters.learningModels
        }
        return ordered_input_shapes

    def get_batch_size(self):
        batch_size = 256
        if self._batch_size is not None:
            batch_size = self._batch_size
            return batch_size

    def yield_column_from_path(self, path, batch_size, column_name):
        with h5py.File(path, "r") as f:
            # print(len(f["type_idx"]))
            for i in range(0, len(f["type_idx"]), batch_size):
                dataset = f[column_name]
                batch = dataset[i : i + batch_size]
                yield batch

    def with_train_dataset_yield(self, batch_size=None):
        if batch_size is None:
            batch_size = self.get_batch_size()

        for binary_dir_path in self._binary_dir_paths:
            train_path = self._config.get_train_file_path(
                binary_dir_path=binary_dir_path
            )
            for batch in self.yield_dataset_from_path(train_path, 256):
                yield batch

    def with_validation_dataset_yield(self, batch_size=None):
        if batch_size is None:
            batch_size = self.get_batch_size()

        validation_path = self._config.get_validation_file_path()
        for batch in self.yield_dataset_from_path(validation_path, batch_size):
            yield batch

    def yield_dataset_from_path(
        self, path, batch_size, suffixes=["_input", "_decoder"], column_names=None
    ):
        if column_names is None:
            column_names = self._config.train_parameters.learningModels

        with h5py.File(path, "r") as f:
            # print(len(f["type_idx"]))
            for i in range(0, len(f["type_idx"]), batch_size):
                dictionaries = [{} for _ in suffixes]
                for learn_model in column_names:
                    dataset = f[learn_model]
                    batch = dataset[i : i + batch_size]
                    for dictionary_idx, dictionary in enumerate(dictionaries):
                        dictionary[
                            self.to_decoder_name(
                                learn_model, suffix=suffixes[dictionary_idx]
                            )
                        ] = batch
                yield tuple(dictionaries)

    def verify_validation_set_leaks(self):
        validation_set_total = []
        for val_set in self.yield_column_from_path(
            self._config.get_validation_file_path(), 256, "time"
        ):
            validation_set_total += val_set.tolist()

        repeats = []
        repeats_paths = []
        for binary_dir_path in self._binary_dir_paths:
            train_path = self._config.get_train_file_path(
                binary_dir_path=binary_dir_path
            )
            for batch in self.yield_column_from_path(train_path, 256, "time"):
                for value in batch:
                    if value in validation_set_total:
                        repeats.append(value)
        if len(repeats) > 0:
            raise ValueError(
                f"Train set leaks into validation found. Leaks count={len(repeats)} in paths={', '.join(repeats_paths)}"
            )
        else:
            self._logger.info(f"Train set leaks into validation not found")

    def get_train_dataset(self):
        return (
            tf.data.Dataset.from_generator(
                self.with_train_dataset_yield, output_signature=self._output_signature
            )
            .shuffle(buffer_size=get_buffer_size())
            .prefetch(tf.data.AUTOTUNE)
            .repeat()
        )

    def get_validation_dataset(self):
        return tf.data.Dataset.from_generator(
            self.with_validation_dataset_yield, output_signature=self._output_signature
        )

    def verify_validation_set_leaks_if_enabled(self):
        if self._config.verify_model.verify_validation_set_leaks:
            self._logger.info(
                "Verifying validation set leaks. To disable set 'verify_validation_set_leaks' to false"
            )
            self.verify_validation_set_leaks()
        else:
            self._logger.info(
                "Verifying validation set leaks DISABLED. To enable set 'verify_validation_set_leaks' to true"
            )

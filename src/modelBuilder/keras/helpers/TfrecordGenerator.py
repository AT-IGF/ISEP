import logging
import tensorflow as tf
from src.core import PathHelper
from src.common.tensorflow import InputModelNames
from src.modelBuilder.keras.helpers import get_buffer_size, get_batch_size
from src.modelBuilder.keras.helpers.abstractions import DataGenerator
import numpy as np
from .TfRecordParsers import TfParserBase


class TfrecordGenerator(DataGenerator):
    def __init__(
        self,
        parser: TfParserBase,
        get_train_file_path,
        get_validation_file_path,
        get_test_file_path=None,
        binary_dir_paths=[],
        batch_size=None,
        buffer_size=None,
    ):
        self._logger = logging.getLogger()
        self._binary_dir_paths = binary_dir_paths
        self._batch_size = get_batch_size(batch_size)
        self._buffer_size = get_buffer_size(buffer_size)
        if parser == None:
            raise ValueError("Parser has to be definied")
        self._parser: TfParserBase = parser
        self._get_train_file_path = get_train_file_path
        self._get_validation_file_path = get_validation_file_path
        self._get_test_file_path = get_test_file_path

    def set_buffer_size(self, buffer_size):
        logging.getLogger().info(
            f"Buffer size overridden to buffer_size={buffer_size}. To high values can cause out of memory error."
        )
        self._buffer_size = buffer_size

    @property
    def extension(self) -> str:
        return [".tfrecord"]

    def create_tfrecord_dataset(
        self, tfrecord_files, repeat, shuffle, batch_size, parse_function
    ) -> tf.data.TFRecordDataset:
        dataset = tf.data.TFRecordDataset(
            tfrecord_files, num_parallel_reads=tf.data.AUTOTUNE
        )
        dataset = dataset.map(parse_function, num_parallel_calls=tf.data.AUTOTUNE)
        if shuffle:
            dataset = dataset.shuffle(
                buffer_size=self._buffer_size
            )  # should be before batching
        dataset = dataset.batch(batch_size=batch_size).prefetch(tf.data.AUTOTUNE)
        if repeat:
            dataset = dataset.repeat()
        return dataset

    def get_train_val_paths(self, callback):
        train_paths = []
        for binary_dir_path in self._binary_dir_paths:
            train_path = callback(binary_dir_path=binary_dir_path)
            train_paths.append(train_path)
        return train_paths

    def validate(self, paths, set_name=""):
        count = 0
        for idx, path in enumerate(paths):
            print(idx, len(paths), path)
            dataset = tf.data.TFRecordDataset(path)
            try:
                count += len(list(dataset.as_numpy_iterator()))
                for raw_record in dataset.take(1):
                    example = tf.train.Example()
                    example.ParseFromString(raw_record.numpy())
            except Exception as e:
                self._logger.error(f"Corrupted file:", e)
                self._logger.error("File is INVALID.", path)
        self._logger.info(f"Total count for {set_name} count={count}")

    def get_train_dataset(self, repeat=True, parse_function=None):
        train_paths = self.get_train_val_paths(callback=self._get_train_file_path)
        # self.validate(train_paths, set_name="train set")
        if parse_function != None:
            return self.create_tfrecord_dataset(
                train_paths,
                repeat=repeat,
                shuffle=True,
                batch_size=self._batch_size,
                parse_function=parse_function,
            )
        else:
            return self.create_tfrecord_dataset(
                train_paths,
                repeat=repeat,
                shuffle=True,
                batch_size=self._batch_size,
                parse_function=self._parser._parse_function,
            )

    def get_validation_dataset(self):
        validation_paths = self.get_train_val_paths(
            callback=self._get_validation_file_path
        )
        self.validate(validation_paths, set_name="validation set")
        return self.create_tfrecord_dataset(
            validation_paths,
            repeat=False,
            shuffle=False,
            batch_size=self._batch_size,
            parse_function=self._parser._parse_function,
        )

    def unpack_dataset(self, dataset, input_name, label_name=None):
        from types import SimpleNamespace

        X, y = {}, []
        for x_val, y_val in dataset.as_numpy_iterator():  # Iterate once
            for key, value in x_val.items():
                X.setdefault(key, []).extend(value)
            y.extend(y_val)

        for key, value in X.items():
            X[key] = np.array(value)
        if label_name is None:
            return SimpleNamespace(**{input_name: X})
        return SimpleNamespace(
            **{
                input_name: X,
                label_name: np.array(y),
                f"{label_name}_max": np.array(y).argmax(axis=1),
            }
        )

    def get_test_dataset(self):
        test_paths = self.get_train_val_paths(callback=self._get_test_file_path)
        self.validate(test_paths, set_name="test set")
        return self.create_tfrecord_dataset(
            test_paths,
            repeat=False,
            shuffle=False,
            batch_size=self._batch_size,
            parse_function=self._parser._parse_function,
        )

    def verify_validation_set_leaks_if_enabled(self):
        self._logger.warning("Verification for .tfrecord not implemented")

    def _parse_function_old(self, proto):
        X_train, X_test = self._parser._parse_function(proto=proto)
        return X_train

    def yield_dataset_from_path(
        self, path, batch_size, suffixes: list[str], column_names=None
    ):
        dataset = self.create_tfrecord_dataset(
            [path],
            repeat=False,
            shuffle=False,
            batch_size=batch_size,
            parse_function=self._parse_function_old,
        )
        for raw_records in dataset.take(batch_size):
            yield raw_records

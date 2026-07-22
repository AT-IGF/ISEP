import os
import glob
import pickle
import logging
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

from src.core import PathHelper
from src.common.config import Config, ModelBuilderUnsupervisedConfig
from src.modelBuilder.keras.helpers.abstractions import DataGenerator
from src.modelBuilder.keras.helpers import (
    generators,
    UnsupervisedTfParser,
    TfrecordGenerator,
)
from src.modelBuilder.datasetHandler import (
    save_dict,
    create_scaled_example_from_record_no_types,
)
from src.core import get_file_lines, write_data


class DatasetScaler:
    scaler_file_suffix = "_scaler"
    file_to_scale_suffix = "_to_scale"

    def __init__(
        self,
        scaler_save_name: str,
        scaler_names: list[str],
        scaler_path: str,
        binaries_dirs: list[str],
    ):
        if scaler_save_name.endswith(self.scaler_file_suffix):
            self.scaler_save_name = scaler_save_name
        else:
            self.scaler_save_name = scaler_save_name + "_scaler"
        self._scaler_names = scaler_names
        self._scaler_save_path = PathHelper.join_path(
            scaler_path, f"{self.scaler_save_name}.pkl"
        )
        self._scaler_path = scaler_path
        self._scaler_progress_path = PathHelper.join_path(
            scaler_path, f"{self.scaler_save_name}_PROGRESS.txt"
        )
        self._config = Config().get(ModelBuilderUnsupervisedConfig)
        self._logger = logging.getLogger()
        self._scaled_paths = self.get_scaled_paths()
        self._scaled_paths_init_len = len(self._scaled_paths)
        self._scalers = self.load_scaners_or_new()
        self._logger.info(
            f"Scaler currently trained on samples count={self.get_number_of_samples()}"
        )
        samples_count = self.get_number_of_samples()
        self.was_not_trained = samples_count == 0
        self._binaries_dirs = binaries_dirs

    def incremental_scaler_fit(self, arrays_dict: dict[str, list]):
        for name in self._scaler_names:
            values_reshaped = self.reshape_to_n_samples(
                arrays_dict[name], single_sample=True
            )
            values_flatten = np.array(values_reshaped).flatten().reshape(-1, 1)
            self._scalers[name].partial_fit(values_flatten)

    @staticmethod
    def incremental_scaler_transform(
        scalers, arrays_dict: dict[str, list], shapes: dict = None
    ):
        scaled_values = {}
        shapes_keys = shapes.keys()
        for scaler_name, scaler in scalers.items():
            values_reshaped = DatasetScaler.reshape_to_n_samples(
                np.array(arrays_dict[scaler_name]), single_sample=True
            )
            n_samples = len(values_reshaped)
            n_features = len(values_reshaped[0])

            scaled_value = scaler.transform(
                np.array(values_reshaped).flatten().reshape(-1, 1)
            )
            scaled_value = scaled_value.reshape(n_samples, n_features)
            if shapes != None and scaler_name in shapes_keys:
                scaled_value = scaled_value.reshape(shapes[scaler_name])
            scaled_values.setdefault(scaler_name, []).append(scaled_value)
        return scaled_values

    @staticmethod
    def transform_dataset(
        scalers: dict[MinMaxScaler],
        list_of_arrays_dict: list[dict[str, list]],
        key_suffix="",
        shapes: dict = None,
    ):
        result = {}
        for arrays_dict in list_of_arrays_dict:
            transofmed_dict = DatasetScaler.incremental_scaler_transform(
                scalers=scalers, arrays_dict=arrays_dict, shapes=shapes
            )
            for key, value in transofmed_dict.items():
                result.setdefault(f"{key}{key_suffix}", []).extend(value)
        return result

    @staticmethod
    def transform_dict_dataset(
        scalers: dict[MinMaxScaler],
        to_scale_dict: dict[str, list],
        key_suffix="",
        shapes: dict = None,
    ):
        scaled_values = {}
        scalers_keys = scalers.keys()
        if not any(element in to_scale_dict.keys() for element in scalers_keys):
            ValueError("Elements to scalen not found in scalers names")
        for key, values in to_scale_dict.items():
            if key in scalers_keys:
                if values[0].ndim > 1:
                    values = DatasetScaler.reshape_multiple_to_n_samples(values)
                if values[0].ndim == 0:
                    values = DatasetScaler.reshape_multiple_to_n_samples(
                        values, single_sample=True
                    )

                n_samples = len(values)
                n_features = len(values[0])

                # for value in values:
                scaled_value = scalers[key].transform(
                    np.array(values).flatten().reshape(-1, 1)
                )
                scaled_value = scaled_value.reshape(n_samples, n_features)
                reshaped_value = [x.reshape(shapes[key]) for x in scaled_value]
                scaled_values.setdefault(key, []).extend(reshaped_value)
            else:
                scaled_values[key] = values
        return scaled_values

    @staticmethod
    def reshape_to_n_samples(arr, single_sample=False):
        if single_sample:
            arr = np.array([arr])
        return arr.reshape(len(arr), -1)

    @staticmethod
    def reshape_multiple_to_n_samples(arr, single_sample=False):
        lists = []
        for lts in arr:
            lists.append(np.array(lts).reshape(-1))
        return lists

    def get_scaled_paths(self):
        scaled_paths = []
        if PathHelper.is_file_exists(self._scaler_progress_path):
            scaled_paths = get_file_lines(self._scaler_progress_path)
        return scaled_paths

    def is_file_fitted(self, path):
        if path in self._scaled_paths or not self.is_to_scale_file(path):
            return True

        return False

    def save_path_as_scaled(self, path):
        try:
            self._scaled_paths.append(path)
            write_data(self._scaler_progress_path, path, append_none_or_empty=False)
        except Exception as e:
            self._logger.error(
                f"Path not added to PROGRESS file but scaled, add them manually. Progress_path={self._scaler_progress_path}, paths to add={', '.join(path)}"
            )
            raise e

    def partial_fit_dataset(self, paths, suffix=""):
        is_any_fit = False
        for path in paths:
            if not self.is_file_fitted(path):
                self._logger.info(
                    f"Fitting scaler with given data due to not found in progress file, path={path}"
                )
                default_generator = self.get_generator_based_on_extension(path)
                for data in default_generator.yield_dataset_from_path(
                    path=path, batch_size=100000, suffixes=[suffix], column_names=None
                ):
                    for name in self._scaler_names:
                        samples = data[f"{name}{suffix}"].numpy()
                        values_reshaped = self.reshape_to_n_samples(samples)
                        self._scalers[name].partial_fit(
                            np.array(values_reshaped).flatten().reshape(-1, 1)
                        )
                self.save_scaler()
                is_any_fit = True
            else:
                if self.get_number_of_samples() == 0 and not self.is_to_scale_file(
                    path
                ):
                    raise ValueError(
                        "Path in scales files, but scales was not trained at all."
                    )
        return is_any_fit

    def scale_data(self, data_batch: list[dict]):
        scaled_dict = {key.replace("_input", ""): [] for key in data_batch.keys()}
        for key, values in data_batch.items():
            key = key.replace("_input", "")
            if values[0].ndim > 1:
                values = DatasetScaler.reshape_multiple_to_n_samples(values)
            if values[0].ndim == 0:
                values = DatasetScaler.reshape_multiple_to_n_samples(
                    values, single_sample=True
                )

            n_samples = len(values)
            n_features = len(values[0])

            scaled_value = self._scalers[key].transform(
                np.array(values).flatten().reshape(-1, 1)
            )
            scaled_data = scaled_value.reshape(n_samples, n_features)
            scaled_dict[key].extend(scaled_data)
        sale_info = {
            key: f"min={np.min(value):.4f}, max={np.max(value):.4f}"
            for key, value in scaled_dict.items()
        }
        self._logger.info(f"Scaler boundaries after creation: {sale_info}")
        return scaled_dict

    def save_scaler(self):
        min_max_info = {
            key: f"min={scaler.data_min_[0]:.4f}, max={scaler.data_max_[0]:.4f}"
            for key, scaler in self._scalers.items()
        }
        self._logger.info(
            f"Saving scaler under path='{self._scaler_save_path}', Samples count={self.get_number_of_samples()}, {min_max_info}"
        )
        with open(self._scaler_save_path, "wb") as f:
            pickle.dump(self._scalers, f)

    @staticmethod
    def load_scanners(path):
        with open(path, "rb") as f:
            return pickle.load(f)

    def load_scaners_or_new(self):
        if not PathHelper.is_file_exists(self._scaler_save_path):
            if self._scaled_paths != []:
                raise ValueError(
                    f"Scaler does not exist put paths are added in progress, path={self._scaler_progress_path}"
                )
            self._logger.info(
                f"No scaler found a new one will be created, path'={self._scaler_save_path}'"
            )
            return {
                scaler_name: MinMaxScaler(feature_range=(0, 1))
                for scaler_name in self._scaler_names
            }

        self._logger.info(
            f"Scaler found under the path. Retriving..., path'={self._scaler_save_path}'"
        )
        return self.load_scanners(self._scaler_save_path)

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

    @staticmethod
    def is_to_scale_file(path):
        extension = PathHelper.get_extension(path)
        base_name_no_ext = PathHelper.get_base_name(path).replace(extension, "")
        if base_name_no_ext.endswith(DatasetScaler.file_to_scale_suffix):
            return True
        return False

    @staticmethod
    def get_save_path_no_scale_suffix(path):
        base_path = PathHelper.get_dirs(path)
        extension = PathHelper.get_extension(path)
        base_name_no_ext = PathHelper.get_base_name(path).replace(extension, "")
        if DatasetScaler.is_to_scale_file(path):
            base_name_no_ext = base_name_no_ext.removesuffix(
                DatasetScaler.file_to_scale_suffix
            )
        else:
            raise ValueError(
                f"File does not contain {DatasetScaler.file_to_scale_suffix}. Are you trying to rescale already scaled file?"
            )
        return PathHelper.join_path(base_path, base_name_no_ext + extension)

    def get_n_samples_or_0(self, scaler):
        if not hasattr(scaler, "n_samples_seen_"):
            return 0
        return scaler.n_samples_seen_

    def get_number_of_samples(self):
        samples_count = []
        for key, value in self._scalers.items():
            samples_count.append(self.get_n_samples_or_0(value))
        return max(samples_count)

    def print_summary(self):
        message = "Scalers samples seen for each scaler summary:"
        for key, value in self._scalers.items():
            message += f" {key}_count={self.get_n_samples_or_0(value)}"
        self._logger.info(message)

    def get_generator_based_on_extension(self, path):
        # default_generator = None
        file_extension = PathHelper.get_extension(path)
        # for generator in generators:
        # if file_extension in generator().extension:
        default_generator: DataGenerator = TfrecordGenerator(
            parser=UnsupervisedTfParser(all_models=True),
            get_train_file_path=self._config.get_train_file_path,
            get_validation_file_path=self._config.get_validation_file_path,
            binary_dir_paths=self._binaries_dirs,
        )
        if default_generator is None:
            raise ValueError(
                f"Generator with extension not found. Allowed extensions {[generator.extension for generator in generators]}"
            )

        return default_generator

    def is_scaled_file_exitst(self, to_scale_file_path):
        suffix_len = len(self.file_to_scale_suffix)
        filename = PathHelper.get_filename(to_scale_file_path)
        if filename.endswith(self.file_to_scale_suffix):
            filename = filename[:-suffix_len]

        extension = PathHelper.get_extension(to_scale_file_path)
        base_path = PathHelper.get_dirs(to_scale_file_path)

        file_path = PathHelper.join_path(base_path, filename + extension)
        return PathHelper.is_file_exists(file_path)

    def scale_files(self, rescale_existing_files=False):
        self._logger.info("Starting files scaling...")
        paths: list[str] = []
        paths_to_save: list[str] = []
        scaler_path = self._scaler_path
        if scaler_path.endswith("/*") == False:
            scaler_path = scaler_path + "/*"
        if scaler_path.endswith("/") == True:
            scaler_path = scaler_path + "*"
        for f in glob.glob(scaler_path):
            filename = PathHelper.get_filename(f)
            if os.path.isfile(f) and filename.endswith(self.file_to_scale_suffix):
                if not self.is_scaled_file_exitst(f) or rescale_existing_files:
                    paths_to_save.append(f.replace(self.file_to_scale_suffix, ""))
                    paths.append(f)

        paths_len = len(paths)
        for idx, path in enumerate(paths):
            step_log = f"({idx + 1}/{paths_len})"
            self._logger.info(f"{step_log} Scaling file, path='{path}'")
            default_generator = self.get_generator_based_on_extension(path)
            scaled_data_to_save = {}

            for data in default_generator.yield_dataset_from_path(
                path=path, batch_size=100000, suffixes=["_input"], column_names=None
            ):
                data_scaled = self.scale_data(data)
                for key, values in data_scaled.items():
                    scaled_data_to_save.setdefault(key, []).extend(values)
            save_path = self.get_save_path_no_scale_suffix(path)
            save_dict(
                features_dict=scaled_data_to_save,
                file_path=save_path,
                parse_callback=create_scaled_example_from_record_no_types,
            )
            self.save_path_as_scaled(path=path)
            self._logger.info(
                f"{step_log} Scaled file saved under path path'={save_path}'"
            )

        self.print_summary()

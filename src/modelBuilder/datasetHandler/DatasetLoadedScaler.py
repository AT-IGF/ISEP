from src.core import PathHelper


class DatasetLoadedScaler:
    file_to_scale_suffix = "_to_scale"

    @staticmethod
    def is_to_scale_file(path):
        extension = PathHelper.get_extension(path)
        base_name_no_ext = PathHelper.get_base_name(path).replace(extension, "")
        if base_name_no_ext.endswith(DatasetLoadedScaler.file_to_scale_suffix):
            return True
        return False

    def transform_tfrecord_dataset(self, paths, suffix=""):
        for path in paths:
            if not self.is_to_scale_file(path):
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
                        self._scalers[name].partial_fit(values_reshaped)
                self.save_scaler(paths=[path])
            else:
                if self.get_number_of_samples() == 0 and not self.is_to_scale_file(
                    path
                ):
                    raise ValueError(
                        "Path in scales files, but scales was not trained at all."
                    )

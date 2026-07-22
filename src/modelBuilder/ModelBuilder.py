from src.common import Consts
from src.common.rawData.Signal.RawDataAdapter import get_pollen_type_from_path
from src.common.filters.ExternalRunner import get_filter
from src.modelBuilder.optimizers.TemperatureScaling import TemperatureScaler
from src.modelBuilder.models.LearnModel import LearnModel
from src.common.config import Config, ModelBuilderConfig, TypesConfig, PathsConfig
from src.common.tensorflow.Settings import set_tf_settings

import matplotlib

# matplotlib.use('Agg')  # Use a non-GUI backend

import os
from typing import Callable
from src.common.rawData.features.FeaturesHandler import FeaturesHandler
from src.common.rawData import RawData
import src.common.filters as filters
from src.core import PathHelper
import pandas as pd
import logging
from src.modelBuilder.keras.models.TrainedModel import TrainedModel
import numpy as np
from src.common.rawData.features.models.FeatureModel import FeatureModel
from src.common.tensorflow import InputModelNames
from src.modelBuilder.datasetHandler import (
    DatasetScaler,
    save_feature_model,
    save_dict,
    create_example_from_record,
)
from sklearn.preprocessing import MinMaxScaler
from src.common import Consts
from itertools import chain
from src.common.rawData.RawDataHanlder import (
    get_raw_data_list_multithread,
    remove_duplicates_by_timestamp,
    extend_list,
    remove_test_samples,
)
from sklearn.model_selection import train_test_split
import tensorflow as tf


def get_raw_data_types() -> list[str] | str:
    config = Config.get(ModelBuilderConfig)
    config_types = Config.get(TypesConfig)
    raw_data_path = PathHelper.join_rel_path(
        Consts.RESOURCES_PATH, Config.get(PathsConfig).zip_files_rel_path
    )
    logging.getLogger().info(
        f"Searching for files under path='{raw_data_path}', types that will be excluded=[{','.join(config.excludeTypes)}]"
    )

    pollen_types = config_types.get_pollen_types(config.excludeTypes)
    raw_data_dirs = [
        x[0]
        for x in os.walk(raw_data_path)
        if get_pollen_type_from_path(x[0]) in pollen_types
    ]

    if len(raw_data_dirs) == 0:
        logging.getLogger().info(
            f"No subfolders found: {raw_data_path} will be processed"
        )
        return raw_data_path

    if len(raw_data_dirs) != len(config_types.pollen_types):
        logging.getLogger().warning(
            f"Number of found dictionaries does not match selected pollen types. Some directory or pollen type is missing, pollen_types={config_types.pollen_types}, dictionaries={raw_data_dirs}"
        )

    return raw_data_dirs


SHAPES = {
    InputModelNames.SCATTERING_UNSUP: [120, 24],
    InputModelNames.SPECTRUM_UNSUP: [32, 8],
    InputModelNames.LIFETIME_UNSUP: [64, 4],
    InputModelNames.SIZE: [],
}


def load_scalers():
    config = Config().get(ModelBuilderConfig)
    path = PathHelper.get_absolute_path(
        Consts.RESOURCES_PATH,
        config.scaler_path,
        raise_message="Scaler path has to be set",
    )
    min_max_scalers: dict[MinMaxScaler] = DatasetScaler.load_scanners(path)
    return min_max_scalers


def is_all_exist(path1, path2, path3):
    return (
        PathHelper.is_file_exists(file_path=path1)
        and PathHelper.is_file_exists(file_path=path2)
        and PathHelper.is_file_exists(file_path=path3)
    )


def randomly_select(
    single_type_count, raw_data_all, oversample, path, reference_test_set=None
):
    logger = logging.getLogger()
    random_state = np.random.RandomState(seed=42)
    raw_data = remove_duplicates_by_timestamp(raw_data_all)
    if reference_test_set is not None:
        times = [np.datetime64(int(x["time"]), "us") for x in reference_test_set]
        raw_data = remove_test_samples(raw_data_all, times)

    raw_data_count = len(raw_data)
    logger.info(
        f"{raw_data_all[0].type}: count={raw_data_count}, to select={single_type_count}"
    )

    random_count = (
        single_type_count
        if single_type_count != None and single_type_count < len(raw_data)
        else len(raw_data)
    )
    raw_data = random_state.choice(raw_data, size=random_count, replace=False)
    if single_type_count != None and random_count < single_type_count:
        if oversample == True:
            count_diff = single_type_count - random_count
            logger.warning(
                f"'oversample' flag is true. Samples will be duplicated to fit single_type_count. Type:{raw_data_all[0].type}, missing count={count_diff}"
            )
            raw_data = extend_list(raw_data, single_type_count)
        else:
            logger.warning(
                f"Single type count is lower than particles in given type by {100 - round(100*len(raw_data)/single_type_count,0)} %. Set will not be balanced. "
                f"Current count={len(raw_data)}, expected count={single_type_count}, path={path}"
            )
            logger.info(
                "To balance set by duplicated list set 'oversample' flag to 'true'"
            )
    return raw_data


def get_dataset_columns(path, columns: list):
    def _parse_function(example_proto):
        feature_description = {}
        if "time" in columns:
            feature_description["time"] = tf.io.FixedLenFeature([], tf.int64)
        if "type_idx" in columns:
            feature_description["type_idx"] = tf.io.FixedLenFeature([], tf.int64)
        if "type" in columns:
            feature_description["type"] = tf.io.FixedLenFeature([], tf.string)
        if InputModelNames.LIFETIME_UNSUP in columns:
            feature_description[InputModelNames.LIFETIME_UNSUP] = tf.io.FixedLenFeature(
                [64 * 4], tf.int64
            )
        if InputModelNames.SCATTERING_UNSUP in columns:
            feature_description[InputModelNames.SCATTERING_UNSUP] = (
                tf.io.FixedLenFeature([120 * 24], tf.int64)
            )
        if InputModelNames.SPECTRUM_UNSUP in columns:
            feature_description[InputModelNames.SPECTRUM_UNSUP] = tf.io.FixedLenFeature(
                [32 * 8], tf.int64
            )
        if InputModelNames.SIZE in columns:
            feature_description[InputModelNames.SIZE] = tf.io.FixedLenFeature(
                [], tf.float32
            )

        parsed_features = tf.io.parse_single_example(example_proto, feature_description)
        features = {column: parsed_features[column] for column in columns}
        return features

    dataset = tf.data.TFRecordDataset(path)
    dataset = dataset.map(_parse_function, num_parallel_calls=tf.data.AUTOTUNE)

    return dataset


def get_reference_test_set(path, is_reference_set, columns, read_all=False):
    if is_reference_set or not PathHelper.is_file_exists(path):
        return None

    dataset_column = get_dataset_columns(path, columns)

    if read_all:
        return list(dataset_column.as_numpy_iterator())

    return dataset_column


def remove_reference_test_samples(
    feature_models: list[FeatureModel], reference_test_set
):
    reference_times = np.array([x["time"] for x in reference_test_set])
    reference_times = sorted(reference_times)
    feature_models_sorted = sorted(feature_models, key=lambda item: item["time"])
    features_times = [x.time for x in feature_models_sorted]
    for reference_time in reference_times:
        if reference_time in features_times:
            feature_indx = features_times.index(reference_time)
            feature_models_sorted.pop(feature_indx)
            features_times.pop(feature_indx)

            time_idx = reference_times.index(reference_time)
            reference_times.pop(time_idx)
    logging.getLogger().info(
        f"Filtered test samples {len(feature_models_sorted)}/{len(feature_models)}"
    )
    return feature_models_sorted


def get_models_to_learn(
    binary_dirs,
    single_type_count: int,
    filter_callback: Callable[[RawData], bool],
    test_filter_callback: Callable[[RawData], bool] | None = None,
) -> LearnModel:
    logger = logging.getLogger()
    config = Config().get(ModelBuilderConfig)
    types_config = Config().get(TypesConfig)
    binary_dirs_len = len(binary_dirs)
    scalers: DatasetScaler = load_scalers()
    train_ratio = 0.70
    test_ratio = 0.15
    validation_ratio = 0.15

    is_reference_set = config.test_model_name == f"{config.model_save_name}_test_model"
    features_to_save = [
        InputModelNames.LIFETIME_UNSUP,
        InputModelNames.SCATTERING_UNSUP,
        InputModelNames.SPECTRUM_UNSUP,
        InputModelNames.SIZE,
        InputModelNames.TIME_UNSUP,
        "type",
        "type_idx",
    ]

    for idx, binary_dir_path in enumerate(binary_dirs):
        file_path_train = config.get_train_file_path(binary_dir_path=binary_dir_path)
        file_path_validation = config.get_validation_file_path(
            binary_dir_path=binary_dir_path
        )
        file_path_test = config.get_test_file_path(binary_dir_path=binary_dir_path)
        file_path_test_not_scaled = config.get_test_reference_file_path(
            binary_dir_path=binary_dir_path, suffix=DatasetScaler.file_to_scale_suffix
        )
        is_reference_file_exists = PathHelper.is_file_exists(file_path_test_not_scaled)

        if (
            is_all_exist(file_path_train, file_path_validation, file_path_test)
            and is_reference_file_exists
        ):
            logger.info(
                f"({idx+1}/{binary_dirs_len}) Cached pollen types file found. Skipping. Path={file_path_train}"
            )
            continue
        logger.info(
            f"({idx+1}/{binary_dirs_len}) Cached pollen types subdir NOT found. Path='{file_path_train}'. Retrieving..."
        )

        raw_data_types, files = list(
            chain.from_iterable(
                get_raw_data_list_multithread(
                    path=binary_dir_path, should_append_callback=filter_callback
                )
            )
        )
        # TODO handle test set filtering
        reference_test_set = None
        if not is_reference_set:
            reference_test_set = get_reference_test_set(
                path=file_path_test_not_scaled,
                columns=features_to_save,
                is_reference_set=is_reference_set,
                read_all=True,
            )
        raw_data_types = randomly_select(
            single_type_count=single_type_count,
            raw_data_all=raw_data_types,
            oversample=config.train_parameters.sampling_strategy
            == config.train_parameters.OVERSAMPLE_STRATEGY,
            path=binary_dir_path,
            reference_test_set=reference_test_set,
        )
        feature_models: list[FeatureModel] = FeaturesHandler(
            pollen_types=types_config.pollen_types,
            scattering_cutoff=Consts.SCATTERING_CUTOFF,
        ).get_feature_models_unsupervised(raw_data=raw_data_types)
        generic_info = f"files count={len(files)}, samples count={len(feature_models)}"

        if is_reference_set:
            feature_models_train, feature_models_val = train_test_split(
                feature_models, test_size=1 - train_ratio, random_state=42
            )
            feature_models_val, feature_models_test = train_test_split(
                feature_models_val,
                test_size=test_ratio / (test_ratio + validation_ratio),
                random_state=42,
            )
            feature_models_test_not_scaled = feature_models_test[:]
        else:
            if not is_reference_file_exists:
                raise FileNotFoundError(
                    f"Test reference file does not exists, path='{file_path_test_not_scaled}'"
                )
            reference_test_set = get_reference_test_set(
                path=file_path_test_not_scaled,
                columns=features_to_save,
                is_reference_set=is_reference_set,
                read_all=True,
            )
            feature_models = remove_reference_test_samples(
                feature_models, reference_test_set
            )
            feature_models_train, feature_models_val = train_test_split(
                feature_models, test_size=validation_ratio, random_state=42
            )
            _test_filter_callback = filter_callback
            if test_filter_callback != None:
                logging.getLogger().info("Test filter not set train will be used.")
                _test_filter_callback = test_filter_callback
            feature_models_test = filter_feature_model_test(
                feature_models=reference_test_set,
                filter_callback=_test_filter_callback,
                config=config,
                types_config=types_config,
            )

        feature_models_train = DatasetScaler.transform_dict_dataset(
            scalers=scalers,
            to_scale_dict=LearnModel.features_model_as_dict(
                feature_models_train, features_to_save=features_to_save
            ),
            shapes=SHAPES,
        )
        feature_models_val = DatasetScaler.transform_dict_dataset(
            scalers=scalers,
            to_scale_dict=LearnModel.features_model_as_dict(
                feature_models_val, features_to_save=features_to_save
            ),
            shapes=SHAPES,
        )
        feature_models_test = DatasetScaler.transform_dict_dataset(
            scalers=scalers,
            to_scale_dict=LearnModel.features_model_as_dict(
                feature_models_test, features_to_save=features_to_save
            ),
            shapes=SHAPES,
        )

        logger.info(f"({idx+1}/{binary_dirs_len}) Saving progress..., {generic_info}")
        logger.info(
            f"({idx+1}/{binary_dirs_len}) Saving train set, path_train={file_path_train} count={len(feature_models_train)}"
        )
        save_dict(feature_models_train, file_path_train, raise_on_precision_lost=False)
        logger.info(
            f"({idx+1}/{binary_dirs_len}) Saving validation set, path_validation={file_path_validation} count={len(feature_models_val)}"
        )
        save_dict(
            feature_models_val, file_path_validation, raise_on_precision_lost=False
        )
        logger.info(
            f"({idx+1}/{binary_dirs_len}) Saving test set, path_test={file_path_test}, count={len(feature_models_test)}"
        )
        save_dict(feature_models_test, file_path_test, raise_on_precision_lost=False)
        if is_reference_set:
            logger.info(
                f"({idx+1}/{binary_dirs_len}) Saving reference set, path_reference={file_path_test_not_scaled} count={len(feature_models_test_not_scaled)}"
            )
            save_feature_model(
                feature_models_test_not_scaled,
                file_path_test_not_scaled,
                features_to_save,
                raise_on_precision_lost=False,
                parse_callback=create_example_from_record,
            )


def save_list_to_hdf(logger, path, l1=[], l2=[]):
    frame = pd.DataFrame(l1)
    logger.info(f"Saving test file under the path={path}")
    frame.to_hdf(path, key="data", data_columns=True, index=False, mode="w")


def filter_feature_model_test(
    feature_models: list[FeatureModel],
    filter_callback: Callable[[RawData], bool] | None,
    config: ModelBuilderConfig,
    types_config: TypesConfig,
):
    logging.getLogger().info(
        f"Filtering test samples from the dataset, ones that does not fit restrictions."
    )
    feature_models_len = len(feature_models)
    raw_data_types = []
    for feature_model in feature_models:
        raw_data = RawData(
            scattering=feature_model[InputModelNames.SCATTERING_UNSUP],
            spectrometer=feature_model[InputModelNames.SPECTRUM_UNSUP],
            lifetime=feature_model[InputModelNames.LIFETIME_UNSUP],
            time=feature_model[InputModelNames.TIME_UNSUP],
            file=None,
            type=feature_model["type"].decode("utf-8"),
            size=feature_model[InputModelNames.SIZE],
        )
        should_add = True
        if filter_callback != None:
            should_add = filter_callback(raw_data)
        if should_add:
            raw_data_types.append(raw_data)

    feature_models_filtered = FeaturesHandler(
        pollen_types=types_config.pollen_types,
        scattering_cutoff=Consts.SCATTERING_CUTOFF,
    ).get_feature_models_unsupervised(raw_data=raw_data_types)

    feature_models_filtered_len = len(feature_models_filtered)
    logging.getLogger().info(
        f"Test reference samples after filtration left count={feature_models_filtered_len}/{feature_models_len}"
    )
    return feature_models_filtered


def train_model(
    learn_model: LearnModel, epochs: int, verbose: int, binary_dirs: str = []
) -> TrainedModel:
    from src.modelBuilder.keras import KerasTrainer

    types_config = Config().get(TypesConfig)
    config = Config().get(ModelBuilderConfig)

    keras_trainer = KerasTrainer(
        pollen_types=types_config.pollen_types,
        binary_dir_paths=binary_dirs,
        batch_size=config.train_parameters.batch_size,
    )
    if config.run_training == True:
        return keras_trainer.train_model(epochs, verbose)
    else:
        logging.getLogger().warning(
            f"Training not run due to proeprty 'run_training: false'. Change it to 'true' to process with the training."
        )
        return keras_trainer.read_model()


def train_test_split_dict(
    X, y, test_size: float = 0.2, random_state: int = None, shuffle: bool = True
):
    """
    Splits X (a dict of lists) and y (a list) into train/test.

    Returns:
        X_train (dict), X_test (dict), y_train (list), y_test (list)
    """
    # ensure all X values have same length as y
    n = len(y)
    if any(len(v) != n for v in X.values()):
        raise ValueError("All feature lists in X must have the same length as y")

    # create a list of indices
    indices = list(range(n))
    train_idx, test_idx = train_test_split(
        indices, test_size=test_size, random_state=random_state, shuffle=shuffle
    )
    y_train = y[train_idx]
    y_test = y[test_idx]

    X_train = {key: values[train_idx] for key, values in X.items()}
    X_test = {key: values[test_idx] for key, values in X.items()}

    return X_train, X_test, y_train, y_test


def calibrate_model(trained_model: TrainedModel):
    config = Config().get(ModelBuilderConfig).calibration
    if config.run_calibration == False:
        logging.getLogger().info(
            "Calibration is turned off to enable it set: 'calibration.run_calibration' to true"
        )
        return
    if config.run_calibration == True:
        logging.getLogger().info(
            "Calibration is turned on to disable it set: 'calibration.run_calibration' to false"
        )

    mb_config = Config().get(ModelBuilderConfig)
    val_set = trained_model.get_validation_dataset()
    X_val, y_val = val_set.X_val, val_set.y_val
    test_set = trained_model.get_test_dataset()
    X_test, y_test = test_set.X_test, test_set.y_test
    X_test, X_cal, y_test, y_cal = train_test_split_dict(
        X_test, y_test, 0.5, random_state=42
    )

    orig_probs = trained_model.model.predict(X_test)
    test_acc = np.mean(np.argmax(orig_probs, axis=1) == np.argmax(y_test, axis=-1))
    avg_conf = orig_probs.max(axis=1).mean()
    logging.getLogger().info(
        f"Accuracy: {test_acc:.3f}, Avg Confidence: {avg_conf:.3f}"
    )

    merged_x = {k: np.concatenate([X_val[k], X_cal[k]]) for k in X_val.keys()}
    merged_y = np.array(y_val.tolist() + y_cal.tolist())
    pollen_types = Config.get(TypesConfig).pollen_types
    calibrator = TemperatureScaler(
        trained_model.model,
        merged_x,
        merged_y,
        classes_count=len(pollen_types) - len(mb_config.excludeTypes),
    )

    calibrator_path = mb_config.get_calibrated_model_path()
    if (
        not PathHelper.is_file_exists(calibrator_path)
        or mb_config.calibration.overwrite_model == True
    ):
        logging.getLogger().info("Calibrating model")
        calibrator.fit(
            epochs=config.epochs, learning_rate=config.lr, batch_size=len(merged_y)
        )
        logging.getLogger().info(f"Saving calibrated model, path={calibrator_path}")
        calibrator.save_model(mb_config.get_calibrated_model_path())
    else:
        logging.getLogger().info(f"Loading calibrated model, path={calibrator_path}")
        calibrator.calibrated_model = tf.keras.models.load_model(calibrator_path)

    if config.evaluate_calibration:
        logging.getLogger().info("Evaluating calibration")
        calibrator.evaluate_calibration(
            X_test,
            y_test,
            model=trained_model.model,
            mode=mb_config.calibration.evaluation_mode,
            name="True model",
        )
        calibrator.evaluate_calibration(
            X_test,
            y_test,
            model=calibrator.calibrated_model,
            mode=mb_config.calibration.evaluation_mode,
            name="Calibrated model",
        )
    if config.plot_reliability_curves:
        logging.getLogger().info("Plotting reliability curves")
        calibrator.plot_reliability_curves(
            X_test, y_test, mode=mb_config.calibration.reliability_mode
        )
    if config.plot_temp_changes:
        logging.getLogger().info("Plotting temperature changes")
        calibrator.plot_temp_changes()
    if config.plot_probability_distributions:
        logging.getLogger().info("Plotting probability distributions")
        calibrator.plot_probability_distributions(X_test, y_test)
    logging.getLogger().info("Replacng oryginal model with caled one")
    trained_model.model = calibrator.get_model()


def verify_model(trained_model: TrainedModel, summary: str):
    from src.modelBuilder.keras.KerasVerifier import KerasVerifier

    KerasVerifier.verify_model(trained_model, summary, scalers=load_scalers())


def handle(summary: str = "", verbose: int = 0):
    set_tf_settings(module_name=ModelBuilderConfig.config_prop_name)
    config = Config().get(ModelBuilderConfig)
    binary_dirs = get_raw_data_types()
    filter_callback = get_filter(config.filter_rel_path, message_prefix="Train")
    test_filter_callback = get_filter(config.summaries.test_filter_rel_path, "Test")
    learn_model = get_models_to_learn(
        binary_dirs=binary_dirs,
        single_type_count=config.train_parameters.single_type_count,
        filter_callback=filter_callback,
        test_filter_callback=test_filter_callback,
    )
    trained_model = None
    trained_model: TrainedModel = train_model(
        learn_model, config.train_parameters.epochs, verbose, binary_dirs=binary_dirs
    )
    calibrate_model(trained_model)
    verify_model(trained_model, summary)


if __name__ == "__main__":
    matplotlib.use("TkAgg")  # Use a non-GUI backend (good for servers)
    handle()

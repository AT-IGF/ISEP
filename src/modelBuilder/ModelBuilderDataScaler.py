from glob import glob
from itertools import chain
import logging
from typing import Callable
from src.common.tensorflow.Settings import setup_logger


from src.common import Consts
from src.common.filters.ExternalRunner import get_filter
from src.common.config import Config, ModelBuilderScalerConfig
from src.common.rawData.RawDataHanlder import get_raw_data_list_multithread
from src.common.rawData.features import FeaturesHandler
from src.common.rawData.Signal import RawData
from src.common.tensorflow import InputModelNames
from src.modelBuilder.datasetHandler import (
    save_feature_model,
    DatasetScaler,
    create_scaled_example_from_record_no_types,
)
from src.core import PathHelper


def process_available_data(binaries_dirs, filter_callback: Callable[[RawData], bool]):
    config = Config().get(ModelBuilderScalerConfig)
    logger = logging.getLogger()
    binaries_dirs_len = len(binaries_dirs)
    if binaries_dirs_len == 0:
        logger.info(
            f"No subdirs with measurements found under given directory. Directories='{config.get_pollen_types_binaries_dirs()}'"
        )

    features_to_save = [
        InputModelNames.LIFETIME_UNSUP,
        InputModelNames.SCATTERING_UNSUP,
        InputModelNames.SPECTRUM_UNSUP,
        InputModelNames.SIZE,
        InputModelNames.TIME_UNSUP,
    ]
    features_to_scale = [
        InputModelNames.LIFETIME_UNSUP,
        InputModelNames.SCATTERING_UNSUP,
        InputModelNames.SPECTRUM_UNSUP,
        InputModelNames.SIZE,
    ]
    scaler = DatasetScaler(
        scaler_save_name=config.get_filename(),
        scaler_names=features_to_scale,
        scaler_path=config.get_save_path(),
        binaries_dirs=binaries_dirs,
    )
    for idx, binary_dir_path in enumerate(binaries_dirs):
        file_path = config.get_file_path(
            binary_dir_path=binary_dir_path, suffix=scaler.file_to_scale_suffix
        )

        if not PathHelper.is_file_exists(file_path):
            logger.info(
                f"({idx+1}/{binaries_dirs_len}) Cached pollen types subdir NOT found. Path='{file_path}'. Retrieving..."
            )
            raw_data_types, files = list(
                chain.from_iterable(
                    get_raw_data_list_multithread(
                        path=binary_dir_path, should_append_callback=filter_callback
                    )
                )
            )
            feature_models = FeaturesHandler(
                pollen_types=None, scattering_cutoff=Consts.SCATTERING_CUTOFF
            ).get_feature_models_unsupervised(raw_data=raw_data_types, scaler=None)
            logger.info(
                f"({idx+1}/{binaries_dirs_len}) processed files count={len(files)}, samples count={len(feature_models)}"
            )
            save_feature_model(
                feature_models,
                file_path,
                features_to_save,
                mode="w",
                parse_callback=create_scaled_example_from_record_no_types,
            )
        else:
            logger.info(
                f"({idx+1}/{binaries_dirs_len}) Cached subdir found. Path='{file_path}'. Retrieving..."
            )

        is_any_fit = scaler.partial_fit_dataset(paths=[file_path], suffix="_input")
        if not is_any_fit:
            logger.info(f"({idx+1}/{binaries_dirs_len}) Nothing to fit, skipping.")
            continue

        logger.info(
            f"({idx+1}/{binaries_dirs_len}) Cached pollen types subdir NOT found. Path='{file_path}'. Retrieving..."
        )

        scaler.save_scaler()

    scaler.scale_files(rescale_existing_files=config.rescale_existing_files)


def get_learn_dirs(dirs):
    paths_list = []
    for dir in dirs:
        paths_list += glob(f"{dir}/*", recursive=True)
    return paths_list


def handle():
    setup_logger(ModelBuilderScalerConfig.config_prop_name)
    logging.getLogger().info("Started - scaler")
    config = Config().get(ModelBuilderScalerConfig)
    subdirs = get_learn_dirs(config.pollen_types_binaries_paths)
    filter_callback = get_filter(config.filter_rel_path)
    process_available_data(binaries_dirs=subdirs, filter_callback=filter_callback)
    logging.getLogger().info("Finished - scaler")


if __name__ == "__main__":
    handle()

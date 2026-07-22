import logging

import os
from typing import Callable
import zipfile

from src.common.sampler import convert

from src.core import PathHelper, read_dataset, File

from src.common.config import PathsConfig, Config
from src.common.rawData.Signal import to_raw_data_model, map_to_raw_data
from src.common.rawData.Signal import RawData
from src.common.rawData.Signal.RawDataAdapter import get_pollen_type_from_path
from src.common.config.configs import TypesConfig, TypesConfig
import numpy as np
from collections import Counter
from . import SingleTypeCountMode


def get_raw_data_types() -> list[str] | str:
    general_config = Config.get(PathsConfig)
    raw_data_path = general_config.get_zip_files_rel_path()
    logging.getLogger().info(f"Searching for files under path='{raw_data_path}'")

    raw_data_dirs = [x[0] for x in os.walk(raw_data_path)][
        1:
    ]  # [0] - take only dirs, [1:] exclude root path

    if len(raw_data_dirs) == 0:
        if not PathHelper.is_dir_exists(raw_data_path):
            raise ValueError(f"Dir to process does not exists, dir={raw_data_path}")
        raise ValueError(f"No sub-folders found for path: {raw_data_path}")
        return raw_data_path
    return raw_data_dirs


def to_raw_data_callback(
    callback_raw: Callable[[RawData], bool] | None, file: File
) -> Callable[[dict], tuple[bool, RawData]]:
    def callback(dict):
        return True, dict

    if callback_raw is None:
        return callback

    def callback(dict):
        data = map_to_raw_data(dict, file)
        return callback_raw(data), data

    return callback


def get_raw_data(
    file: File,
    raw_data_models_from_file_count: int | None = None,
    should_append_callback: Callable[[RawData], bool] = None,
) -> list[RawData]:
    
    try:
        raw_data: list[RawData] = convert(
            path=file.get_file_path(),
            should_append_callback=to_raw_data_callback(should_append_callback, file),
            raw_data_models_from_file_count=raw_data_models_from_file_count,
        )
    except Exception as ex:
        logging.getLogger().warn(
            f"Unable to convert file or file is corrupted, skipped. File={file.get_file_path()}, error={ex}"
        )
        return []

    return raw_data


def init_worker(callback):
    """Initialize each worker with the callback"""
    global _worker_callback
    _worker_callback = callback


def process_file_wrapper(file):
    global _worker_callback
    return file, get_raw_data(file=file, should_append_callback=_worker_callback)


import multiprocessing


def get_raw_data_in_batches(
    files: list[File],
    raw_data_models_from_files_count: int,
    should_append_callback: Callable[[RawData], bool] = None,
) -> (list[RawData], list[File]):
    raw_data_models: list[RawData] = []
    raw_data_models_from_files_count_buffer = 0
    processed_files = []
    processes_count = os.cpu_count()
    with multiprocessing.Pool(
        processes=processes_count,
        initializer=init_worker,
        initargs=(should_append_callback,),
    ) as pool:
        results = pool.map(process_file_wrapper, files)

        for idx, val in enumerate(results):
            file = val[0]
            raw_data_model = val[1]
            raw_data_models += raw_data_model

            raw_data_models_from_files_count_buffer += len(raw_data_model)
            processed_files.append(file)
    return raw_data_models, processed_files


def get_raw_data_list_multithread(
    path: str | None = None,
    files: list[File] | None = None,
    batch_size: int = 20000,
    should_append_callback: Callable[[RawData], bool] = None,
) -> (list[RawData], list[File]):
    if path is not None and files is not None:
        raise ValueError("Path and files cannot be given at the same time")
    if path is not None:
        files = read_dataset(path).files
    elif files is not None:
        files = files
    else:
        raise ValueError("Path or files have to be definied")

    raw_data: list[RawData] = []
    if len(files) == 0:
        return []
    batch_list = np.array_split(files, np.ceil(len(files) / batch_size))
    processed_files_count = 0
    for files_batch in batch_list:
        raw_data_models, processed_files = get_raw_data_in_batches(
            files_batch, None, should_append_callback
        )
        processed_files_count += len(processed_files)
        if processed_files_count > batch_size:
            logging.getLogger().info(
                f"{PathHelper.get_base_name(path)}: processed files count={processed_files_count}/{len(files)}"
            )
        raw_data += raw_data_models
        raw_data = remove_duplicates_by_timestamp(raw_data)
        yield raw_data, files_batch


def get_raw_data_list(
    path: str | None,
    raw_data_models_from_file_count=None,
    should_append_callback: Callable[[RawData], bool] = None,
) -> list[RawData]:
    if path is None:
        path = get_raw_data_types()
    files: list[File] = read_dataset(path).files
    files_len = len(files)
    raw_data_models: list[RawData] = []
    for idx, file in enumerate(files):
        if raw_data_models_from_file_count == 0:
            break
        raw_data_model = get_raw_data(
            file=file,
            raw_data_models_from_file_count=raw_data_models_from_file_count,
            should_append_callback=should_append_callback,
        )
        raw_data_models += raw_data_model

        if raw_data_models_from_file_count is not None:
            raw_data_models_from_file_count -= len(raw_data_model)

        if idx == 0:
            logging.getLogger().info(
                f"{PathHelper.get_base_name(path)}: Started to process count={files_len}"
            )
        elif files_len > 2000 and idx % 1000 == 0:
            logging.getLogger().info(
                f"{PathHelper.get_base_name(path)}: {idx}/{files_len}"
            )

    if len(raw_data_models) > 0:
        logging.getLogger().info(
            f"{raw_data_models[0].type}: processed, count={len(raw_data_models)}"
        )
    else:
        logging.getLogger().warning(
            f"{raw_data_models[0].type}: processed, count={len(raw_data_models)}"
        )

    if (
        raw_data_models_from_file_count is not None
        and raw_data_models_from_file_count > 0
        and len(raw_data_models) / raw_data_models_from_file_count < 0.5
    ):
        logging.getLogger().warning(
            f"Low count of {raw_data_models[0].type} type, count={len(raw_data_models)}, threshold={raw_data_models_from_file_count}. "
            + "This type can be set as less significant during train process (if applyable)."
        )

    return raw_data_models


def remove_test_samples(raw_data: list[RawData], times_test):
    times = [x.time for x in raw_data]
    duplicates = [dt for dt, count in Counter(times).items() if count > 1]
    if len(duplicates) > 0:
        raise ValueError(f"Duplicates in test model found, duplicates={duplicates}")

    raw_data_init_len = len(raw_data)
    particle_type = raw_data[0].type  # type same for all of the particles in collection

    times_test_set = set(times_test)
    filtered = []
    for data in raw_data:
        if np.datetime64(data.time) not in times_test_set:
            filtered.append(data)

    logging.getLogger().info(
        f"{particle_type}: filtered test samples form dataset left count={len(filtered)}/{raw_data_init_len}"
    )
    return filtered


def remove_duplicates_by_timestamp(raw_data_all):
    logger = logging.getLogger()
    raw_data = list({model.time: model for model in raw_data_all}.values())
    num_duplicates_removed = len(raw_data_all) - len(raw_data)
    if num_duplicates_removed > 0:
        logger.info(
            f"{raw_data_all[0].type}: number of duplicates removed count={num_duplicates_removed}"
        )
    return raw_data


def prioritize_paths(paths, fragments):
    matching = [p for p in paths if any(frag in p for frag in fragments)]
    non_matching = [p for p in paths if not any(frag in p for frag in fragments)]
    return matching + non_matching


def extend_list(lst, target_length):
    new_list = lst[:].tolist()
    lst_len = len(lst)
    diff = target_length - lst_len
    for i in range(0, diff):
        new_list.append(lst[i % len(lst)])
    return np.array(new_list)


def get_pollen_types(
    single_type_count=None,
    types_to_exclude=None,
    test_model=None,
    should_append_callback: Callable[[RawData], bool] = None,
    count_mode: None | SingleTypeCountMode = SingleTypeCountMode.STOP_ON_COUNT,
    oversample=False,
    pollen_types=None
) -> list[RawData]:
    logger = logging.getLogger()
    if types_to_exclude is None:
        types_to_exclude = []
    if should_append_callback is None:
        logger.info(
            f"should append callback is None, all types will read from raw files without filtering it"
        )
    logger.info(
        f"Same type particles count is set to={single_type_count} with mode={count_mode.name}. If set to 'None' all particles will be taken"
    )

    raw_data_by_type: list[str] = get_raw_data_types()
    types_counts: list[int] = []
    raw_data_types: list[RawData] = []
    random_state = np.random.RandomState(seed=42)

    is_test_model = test_model is not None
    if is_test_model:
        logger.info(
            "Predefined test set found. Test samples will be excluded from selection set."
        )
    else:
        logger.warning(
            "Predefined test set NOT found. Samples will be taken from available data."
        )

    # raw_data_by_type = prioritize_paths(
    #     raw_data_by_type, []
    # )
    for path in raw_data_by_type:
        if pollen_types is not None and get_pollen_type_from_path(path) not in pollen_types:
            continue
        
        if get_pollen_type_from_path(path) in types_to_exclude:
            logger.info(f"Path skipped due to be in types_to_exclude. Path={path}")
            continue
        if count_mode == SingleTypeCountMode.RANDOM_FROM_ALL:
            raw_data_all: list[RawData] = get_raw_data_list(
                path, None, should_append_callback
            )
        else:
            raw_data_all: list[RawData] = get_raw_data_list(
                path, single_type_count, should_append_callback
            )
        raw_data = remove_duplicates_by_timestamp(raw_data_all)

        if is_test_model:
            raw_data = remove_test_samples(raw_data, test_model["time"].iloc)

        raw_data_count = len(raw_data)
        logger.info(f"{raw_data_all[0].type}: left count={raw_data_count}")

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

        raw_data_count = len(raw_data)
        types_counts.append(raw_data_count)
        raw_data_types = np.concatenate((raw_data_types, raw_data))

    if len(types_counts) == 0:
        logger.warning(f"No particles found")
        return []

    min_length = min(types_counts)
    if single_type_count is not None and min_length > single_type_count:
        logger.warning(
            f"Lowest pollen type samples count={min_length}. 'single_type_count' could be higher. single_type_count={single_type_count}"
        )
    logger.info(f"Pollen types processing finished, excluded = {types_to_exclude}")
    return raw_data_types


def get_pollen_type_idx_or_default(pollen_types: list[str], pollen_type, default=-1):
    if pollen_type in pollen_types:
        return pollen_types.index(pollen_type)
    return default


def get_pollen_type_idx(pollen_types: list[str], pollenType):
    return pollen_types.index(pollenType)

from multiprocessing import Pool
from typing import Callable
from src.modelBuilder.models.LearnModel import LearnModel
import h5py
import numpy as np
from src.modelBuilder.models import FeatureModel
from src.common.tensorflow import InputModelNames
import tensorflow as tf
import os
from src.common.config import Config, ModelBuilderUnsupervisedConfig
import pandas as pd
import logging
from src.core import PathHelper
from concurrent.futures import ProcessPoolExecutor
from functools import partial

def get_data_maxshape(data, resizable_axes=(0,)):
    maxshape = list(data.shape)
    for axis in resizable_axes:
        maxshape[axis] = None
    return tuple(maxshape)


def save_file_h5(features_dict: dict, file_path: str, mode: str = "w"):
    with h5py.File(file_path, mode) as f:
        for key, values in features_dict.items():
            values = np.array(values)
            if key in f:
                dataset = f[key]
                current_size = dataset.shape[0]
                num_new_entries = values.shape[0]
                new_shape = (current_size + num_new_entries,) + dataset.shape[1:]
                dataset.resize(new_shape)
                dataset[current_size:] = values
            else:
                maxshape = values.shape
                if mode == "a":
                    maxshape = get_data_maxshape(values)
                f.create_dataset(key, data=values, chunks=True, maxshape=maxshape)


def is_precision_preserved(value: int) -> bool:
    original = np.array(value)
    orig_dtype = original.dtype
    converted = original.astype(np.float32).astype(orig_dtype)

    return np.array_equal(original, converted)


def to_float32_bytes(value, raise_on_precision_lost, key=None):
    if not is_precision_preserved(value) and raise_on_precision_lost:
        raise ValueError(f"Value to high to convert: {value}, name={key}")
    if isinstance(value, list):
        value = tf.convert_to_tensor(value, dtype=tf.float32)
    float32 = tf.reshape(tf.cast(value, tf.float32), [-1]).numpy().tolist()
    return float32


def create_scaled_example_from_record(record, raise_on_precision_lost):
    feature = {
        "lifetime_unsup": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    record["lifetime_unsup"], raise_on_precision_lost, "lifetime_unsup"
                )
            )
        ),
        "scattering_unsup": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    record["scattering_unsup"],
                    raise_on_precision_lost,
                    "scattering_unsup",
                )
            )
        ),
        "spectrum_unsup": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    record["spectrum_unsup"], raise_on_precision_lost, "spectrum_unsup"
                )
            )
        ),
        "size": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    [record["size"]], raise_on_precision_lost, "size"
                )
            )
        ),
        "type": tf.train.Feature(bytes_list=tf.train.BytesList(value=[record["type"]])),
        "type_idx": tf.train.Feature(
            int64_list=tf.train.Int64List(value=[record["type_idx"]])
        ),
        "time": tf.train.Feature(int64_list=tf.train.Int64List(value=[record["time"]])),
    }
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    return example.SerializeToString()


def create_scaled_example_from_record_no_types(record, raise_on_precision_lost):
    feature = {
        "lifetime_unsup": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    record["lifetime_unsup"], raise_on_precision_lost, "lifetime_unsup"
                )
            )
        ),
        "scattering_unsup": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    record["scattering_unsup"],
                    raise_on_precision_lost,
                    "scattering_unsup",
                )
            )
        ),
        "spectrum_unsup": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    record["spectrum_unsup"], raise_on_precision_lost, "spectrum_unsup"
                )
            )
        ),
        "size": tf.train.Feature(
            float_list=tf.train.FloatList(
                value=to_float32_bytes(
                    [record["size"]], raise_on_precision_lost, "size"
                )
            )
        ),
    }
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    return example.SerializeToString()


def create_example_from_record(record, raise_on_precision_lost):
    assert (
        len(record["scattering_unsup"]) == 2880
    ), f"Invalid length: {len(record['scattering_unsup'])}"
    feature = {
        "lifetime_unsup": tf.train.Feature(
            int64_list=tf.train.Int64List(value=record["lifetime_unsup"])
        ),
        "scattering_unsup": tf.train.Feature(
            int64_list=tf.train.Int64List(value=record["scattering_unsup"])
        ),
        "spectrum_unsup": tf.train.Feature(
            int64_list=tf.train.Int64List(value=record["spectrum_unsup"])
        ),
        "size": tf.train.Feature(float_list=tf.train.FloatList(value=[record["size"]])),
        "type": tf.train.Feature(bytes_list=tf.train.BytesList(value=[record["type"]])),
        "type_idx": tf.train.Feature(
            int64_list=tf.train.Int64List(value=[record["type_idx"]])
        ),
        "time": tf.train.Feature(int64_list=tf.train.Int64List(value=[record["time"]])),
    }
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    return example.SerializeToString()


def mkdirs_if_not_exists(path):
    os.makedirs(path, exist_ok=True)


def save_feature_model_tfrecord(
    features_dict,
    file_path,
    raise_on_precision_lost,
    parse_callback: Callable[[dict], bytes],
):
    PathHelper.make_dirs(path=file_path)

    columns = list(features_dict.keys())
    rows = [dict(zip(columns, row)) for row in zip(*features_dict.values())]
    try:
        with tf.io.TFRecordWriter(file_path) as writer:
            for row_dict in rows:
                example = parse_callback(row_dict, raise_on_precision_lost)
                writer.write(example)
    except Exception as e:
        if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
            os.remove(file_path)
        raise e


def save_dict(
    features_dict,
    file_path,
    raise_on_precision_lost=True,
    mode="w",
    parse_callback: Callable[[dict], bytes] = create_scaled_example_from_record,
):
    config = Config().get(ModelBuilderUnsupervisedConfig)
    if config.train_file_extension == ".h5":
        save_file_h5(features_dict=features_dict, file_path=file_path, mode=mode)
    elif config.train_file_extension == ".tfrecord":
        save_feature_model_tfrecord(
            features_dict=features_dict,
            file_path=file_path,
            raise_on_precision_lost=raise_on_precision_lost,
            parse_callback=parse_callback,
        )
    else:
        raise ValueError(
            f"Model save name extension not supported. Current={config.model_save_name_extension}, Exprected:'.tfrecord', '.5h'"
        )


def save_feature_model(
    feature_models: list[FeatureModel],
    file_path,
    features_to_save,
    raise_on_precision_lost=True,
    mode="w",
    parse_callback: Callable[[dict], bytes] = create_scaled_example_from_record,
):
    learn_model = LearnModel(feature_models=feature_models, pollen_types=None)
    features_dict = learn_model.get_feature_models_as_dict(include=features_to_save)

    save_dict(
        features_dict=features_dict,
        file_path=file_path,
        raise_on_precision_lost=raise_on_precision_lost,
        mode=mode,
        parse_callback=parse_callback,
    )

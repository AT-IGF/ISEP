import logging
import os
import h5py
import numpy as np
import json
from src.core import PathHelper
from src.common.config import Config, ModelBuilderUnsupervisedConfig

IS_LIST_ATTR = "is_list"
STRING_ENCODING = "utf-8"


def get_latent_vector_file_path(binary_paths_len: int):
    config = Config().get(ModelBuilderUnsupervisedConfig)
    anomaly = (
        ""
        if config.cluster_parameters.anomaly_detector.run_anomaly_detector is False
        else "-no_anomalies"
    )
    filename = (
        config.model_save_name
        + f"-_reg{anomaly}-{binary_paths_len}dirs_latent_vectors.h5"
    )
    filename = "unsupervised_model_scaled-size-best-weights-buffer30k_Conv2D_relu_512_2-_reg-57dirs_latent_vectors.h5"

    return PathHelper.join_path(config.get_latent_vectors_path(), filename)


def is_latent_vectors_file_exists(binary_paths_len):
    file_path = get_latent_vector_file_path(binary_paths_len)
    return PathHelper.is_file_exists(file_path)


def save_latent_vectors(latent_vectors, metadata, dataset_name="latent_vectors"):
    file_path = get_latent_vector_file_path(
        binary_paths_len=len(metadata["binary_paths"])
    )
    logging.getLogger().info(f"Saving latent vectors under path={file_path}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with h5py.File(file_path, "w") as h5f:
        h5f.create_dataset(dataset_name, data=latent_vectors)
        for key, value in metadata.items():
            try:
                if isinstance(value, (list, np.ndarray)):
                    data_to_store = np.array(value)
                    dset = h5f.create_dataset(key, data=data_to_store)
                    dset.attrs[IS_LIST_ATTR] = True
                    continue
            except Exception as e:
                pass
            serialized = json.dumps(value)
            dt = h5py.string_dtype(encoding=STRING_ENCODING)
            dset = h5f.create_dataset(key, data=np.array(serialized, dtype=dt))
            dset.attrs[IS_LIST_ATTR] = False
    norms = np.linalg.norm(latent_vectors, axis=1, ord=2)
    logging.getLogger().info(f"Emeeddings normalization status")
    logging.getLogger().info(f"Min norm: {np.min(norms):.2f}")
    logging.getLogger().info(f"Max norm: {np.max(norms):.2f}")
    logging.getLogger().info(f"Mean norm: {np.mean(norms):.2f}")


def load_latent_vectors(binary_paths_len, dataset_name="latent_vectors"):
    file_path = get_latent_vector_file_path(binary_paths_len=binary_paths_len)
    logging.getLogger().info(
        f"Latent vectors file found. Retriving..., path={file_path}"
    )
    with h5py.File(file_path, "r") as h5f:
        latent_vectors = h5f[dataset_name][()]
        metadata = {}

        for key in h5f.keys():
            if key == dataset_name:
                continue
            dset = h5f[key]
            is_list = dset.attrs.get(IS_LIST_ATTR, False)
            if is_list:
                # Convert the stored numpy array to a Python list.
                metadata[key] = dset[()].tolist()
            else:
                # Load the stored JSON string and deserialize it.
                raw = dset[()]
                # If the raw data is bytes, decode it.
                if isinstance(raw, bytes):
                    raw = raw.decode(STRING_ENCODING)
                metadata[key] = json.loads(raw)

    return latent_vectors, metadata

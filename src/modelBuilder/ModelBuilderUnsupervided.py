import logging
import time

from src.modelBuilder.keras.callbacks import LogCallback
from src.common import Consts
from src.common.filters.ExternalRunner import get_filter
from src.modelBuilder.models import LearnModel
from src.common.filters import AnomalyDetector
from src.common.config import Config, ModelBuilderUnsupervisedConfig
from src.common.tensorflow.Settings import set_tf_settings

import matplotlib

import numpy as np

from enum import Enum
from typing import Callable
from glob import glob
from itertools import chain
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import Model
from src.core import PathHelper

from src.common import filters
from src.common.rawData.RawDataHanlder import (
    get_raw_data_list_multithread,
    get_pollen_type_idx_or_default,
    get_pollen_type_from_path,
)
from src.common.rawData.features.FeaturesHandler import FeaturesHandler
from src.common.rawData.Signal import RawData
from src.modelBuilder.keras import KerasUnsupervisedTrainer
from src.modelBuilder.datasetHandler import (
    save_dict,
    DatasetScaler,
    create_scaled_example_from_record_no_types,
)
from src.modelBuilder.datasetHandler.models import DatasetSplitModel
from src.modelBuilder import dataInspectors as inspectors
from src.modelBuilder import clusterers
from src.common.tensorflow import InputModelNames
from src.modelBuilder.dataInspectors.helpers import (
    load_latent_vectors,
    save_latent_vectors,
    is_latent_vectors_file_exists,
)
from src.common import Consts
from sklearn.preprocessing import MinMaxScaler


def get_learn_dirs(dirs):
    paths_list = []
    for dir in dirs:
        paths_list += glob(f"{dir}/*", recursive=True)
    return paths_list


def get_data_from_cached_file(file_path, logger):
    my_data = pd.read_hdf(file_path)
    raw_data_types = [RawData(**kwargs) for kwargs in my_data.to_dict(orient="records")]
    logger.info(f"Particles count = {len(raw_data_types)}")
    return raw_data_types


class DataRetirevalMode(Enum):
    SAVING = 0
    SCALING = 1


def is_files_exists(path1, path2):
    if PathHelper.is_file_exists(file_path=path1):
        return True
    if PathHelper.is_file_exists(file_path=path2):
        return True
    return False


def load_scalers():
    config = Config().get(ModelBuilderUnsupervisedConfig)
    path = PathHelper.get_absolute_path(
        Consts.RESOURCES_PATH,
        config.train_parameters.scaler_path,
        raise_message="Scaler path  has to be set",
    )
    min_max_scalers: dict[MinMaxScaler] = DatasetScaler.load_scanners(path)
    return min_max_scalers


SHAPES = {
    InputModelNames.SCATTERING_UNSUP: [120, 24],
    InputModelNames.SPECTRUM_UNSUP: [32, 8],
    InputModelNames.LIFETIME_UNSUP: [64, 4],
    InputModelNames.SIZE: [],
}


def process_available_data(binaries_dirs, filter_callback: Callable[[RawData], bool]):
    config = Config().get(ModelBuilderUnsupervisedConfig)
    logger = logging.getLogger()
    binaries_dirs_len = len(binaries_dirs)
    if binaries_dirs_len == 0:
        logger.info(
            f"No subdirs with measurements found under given directory. Directories='{config.get_pollen_types_binaries_dirs()}'"
        )

    scalers: DatasetScaler = load_scalers()

    features_to_save = [
        InputModelNames.LIFETIME_UNSUP,
        InputModelNames.SCATTERING_UNSUP,
        InputModelNames.SPECTRUM_UNSUP,
        InputModelNames.SIZE,
        InputModelNames.TIME_UNSUP,
    ]
    for idx, binary_dir_path in enumerate(binaries_dirs):
        file_path_train = config.get_train_file_path(
            binary_dir_path=binary_dir_path, suffix=DatasetScaler.file_to_scale_suffix
        )
        file_path_validation = config.get_validation_file_path(
            binary_dir_path=binary_dir_path, suffix=DatasetScaler.file_to_scale_suffix
        )

        scaled_file_path_train = config.get_train_file_path(
            binary_dir_path=binary_dir_path
        )
        scaled_file_path_validation = config.get_validation_file_path(
            binary_dir_path=binary_dir_path
        )
        if is_files_exists(scaled_file_path_train, scaled_file_path_validation):
            logger.info(
                f"({idx+1}/{binaries_dirs_len}) Cached pollen types file found. Skipping"
            )
            continue

        logger.info(
            f"({idx+1}/{binaries_dirs_len}) Cached pollen types subdir NOT found. Path='{file_path_train}'. Retrieving..."
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
        ).get_feature_models_unsupervised(raw_data=raw_data_types)
        generic_info = f"files count={len(files)}, samples count={len(feature_models)}"

        if config.train_parameters.validation_set_size > 0:
            feature_models_train, feature_models_val = train_test_split(
                feature_models,
                train_size=1 - config.train_parameters.validation_set_size,
                random_state=42,
            )
            logger.info(
                f"({idx+1}/{binaries_dirs_len}) Saving progress in path_train={scaled_file_path_train} count={len(feature_models_train)}, path_validation={scaled_file_path_validation} count={len(feature_models_val)}, {generic_info}"
            )

            feature_models_train_scaled = DatasetScaler.transform_dict_dataset(
                scalers=scalers,
                to_scale_dict=LearnModel.features_model_as_dict(
                    feature_models_train, features_to_save=features_to_save
                ),
                shapes=SHAPES,
            )
            save_dict(
                feature_models_train_scaled,
                scaled_file_path_train,
                False,
                mode="w",
                parse_callback=create_scaled_example_from_record_no_types,
            )

            feature_models_val_scaled = DatasetScaler.transform_dict_dataset(
                scalers=scalers,
                to_scale_dict=LearnModel.features_model_as_dict(
                    feature_models_val, features_to_save=features_to_save
                ),
                shapes=SHAPES,
            )
            save_dict(
                feature_models_val_scaled,
                scaled_file_path_validation,
                False,
                mode="a",
                parse_callback=create_scaled_example_from_record_no_types,
            )
        else:
            logger.info(
                f"({idx+1}/{binaries_dirs_len}) Saving progress in path={file_path_train}, {generic_info}"
            )
            feature_models = DatasetScaler.transform_dict_dataset(
                scalers=scalers,
                to_scale_dict=LearnModel.features_model_as_dict(
                    feature_models, features_to_save=features_to_save
                ),
                shapes=SHAPES,
            )
            save_dict(
                feature_models,
                scaled_file_path_train,
                False,
                mode="w",
                parse_callback=create_scaled_example_from_record_no_types,
            )


def get_pollen_type_index_or_default_from_path(path, pollen_types, with_labeled_samples):
    if with_labeled_samples:
        pollen_type = get_pollen_type_from_path(path=path)
        pollen_type_idx = get_pollen_type_idx_or_default(
            pollen_types=pollen_types, pollen_type=pollen_type
        )
    else:
        pollen_type_idx = -1
    if pollen_type_idx == -1:
        pollen_type = "Unknown"
    return pollen_type, pollen_type_idx


def is_any_dataset_prediction_required(binary_paths_len):
    config = Config().get(ModelBuilderUnsupervisedConfig)
    is_umap_trained = inspectors.UmapInspetor.is_umap_trained(config.model_save_name)
    if config.cluster_parameters.run_clustering:
        return (
            config.cluster_parameters.run_umap()
            and not is_umap_trained
            and not is_latent_vectors_file_exists(binary_paths_len=binary_paths_len)
        )
    elif config.verify_model.verify_model:
        return (
            config.verify_model.is_plot_reconstructions() == True
            or config.verify_model.is_calc_recon_errors() == True
        )
    else:
        return False


def select_random_subset(lst, percentage=10):
    num_rows = lst.shape[0]
    sample_size = max(
        1, num_rows * percentage // 100
    )  # Ensure at least one row is selected
    indices = np.random.choice(
        num_rows, sample_size, replace=False
    )  # Randomly select row indices
    mask = np.zeros(num_rows, dtype=bool)
    mask[indices] = True
    return mask


def get_encoder(model):
    latent_output = model.get_layer(Consts.AUTOENCODER_LATENT_LAYER_NAME).output
    return Model(inputs=model.input, outputs=latent_output)


def verify_model(keras_trainer: KerasUnsupervisedTrainer):
    config = Config().get(ModelBuilderUnsupervisedConfig)

    run_latent_prediction = (
        config.verify_model.is_plot_pca()
        or config.cluster_parameters.run_clusterer()
        or config.cluster_parameters.run_umap()
        or config.cluster_parameters.run_kmeans()
        or config.cluster_parameters.run_hdbscan()
    )

    run_compressed_prediction = (
        config.verify_model.is_plot_reconstructions()
        or config.verify_model.is_calc_recon_errors()
    )
    binary_paths = keras_trainer._binary_dir_paths
    binary_paths_len = len(binary_paths)
    # binary_paths_len = 57

    model, history = None, None
    encoder = None
    if (
        run_compressed_prediction == True
        or is_latent_vectors_file_exists(binary_paths_len=binary_paths_len) == False
        or config.verify_model.is_show_history_plot() == True
    ):
        model, history, is_loaded = keras_trainer.get_keras_model()
        if is_loaded == False:
            logging.getLogger().info(
                f"Verification skipped because model is not trained"
            )
            return
        model.summary(print_fn=logging.getLogger().info)
        encoder = get_encoder(model)

    if config.verify_model.is_show_history_plot() == True:
        keras_trainer.show_history_plot(history=history)

    anomaly_detector = None
    if (
        config.cluster_parameters.run_anomaly_detector()
        and config.cluster_parameters.anomaly_detector.anomaly_detector_path is not None
    ):
        anomaly_detector = AnomalyDetector(
            config.cluster_parameters.anomaly_detector.anomaly_detector_path
        )

    clusterer = clusterers.MiniBatchKMeansClusterer()
    latent_vectors_x = []
    latent_vectors_y = []
    latent_vectors_paths = []
    pollen_indexes_dict = {}
    paths_indexes_dict = {}

    reconstruction_errors, reconstruction_keys = None, []
    for path_idx, path in enumerate(binary_paths):
        pollen_type, pollen_type_idx = get_pollen_type_index_or_default_from_path(
            path=path, pollen_types=config.train_parameters.pollen_types, with_labeled_samples=config.train_parameters.with_labeled_samples
        )
        train_path = config.get_train_file_path(path)
        logging.getLogger().info(
            f"{path_idx+1}/{binary_paths_len} Processing path={train_path}"
        )
        dataset_generator = keras_trainer.yield_dataset_from_path(
            path=train_path,
            batch_size=100000,
            suffixes=["_input"],
            column_names=config.train_parameters.learningModels,
        )
        if is_any_dataset_prediction_required(
            binary_paths_len=binary_paths_len
        ) or not is_latent_vectors_file_exists(binary_paths_len=binary_paths_len):
            paths_indexes_dict[path] = path_idx
            for train_set_idx, train_set in enumerate(dataset_generator):
                if anomaly_detector is not None:
                    train_set, is_any_left = anomaly_detector.filter_anomalies(
                        train_set
                    )
                    if not is_any_left:
                        continue
                if run_latent_prediction and not is_latent_vectors_file_exists(
                    binary_paths_len=binary_paths_len
                ):
                    latent_vectors = encoder.predict(
                        train_set, callbacks=[LogCallback()]
                    )
                    latent_vectors_x.extend(latent_vectors)
                    labels_len = len(latent_vectors)
                    latent_vectors_y.extend([pollen_type_idx] * labels_len)
                    pollen_indexes_dict[pollen_type] = pollen_type_idx
                    latent_vectors_paths.extend([path_idx] * labels_len)

                    logging.getLogger().info(
                        f"{path_idx+1}/{binary_paths_len} latent_vectors_x subset extended, current count={len(latent_vectors)}, total={len(latent_vectors_x)}, idx={pollen_type_idx}"
                    )
                if run_compressed_prediction:
                    X_valid_compressed = model.predict(
                        train_set, callbacks=[LogCallback()]
                    )
                    
                    # quick fix to align result with dict order, it would be better to have X_valid_compressed as key: value
                    def prefix(name):
                        return name.rsplit("_", 1)[0]
                    preds = dict(zip(model.output_names, X_valid_compressed))
                    preds_by_prefix = {prefix(k): v for k, v in preds.items()}
                    X_valid_compressed = [preds_by_prefix[prefix(k)] for k in train_set.keys()]
                if config.verify_model.is_plot_reconstructions() == True:
                    inspectors.ReconstructionInspector.plot_reconstruction(
                        train_set, X_valid_compressed
                    )
                if config.verify_model.is_calc_recon_errors() == True:
                    reconstruction_errors, reconstruction_keys = (
                        inspectors.ReconstructionInspector.calculate_reconstruction_error(
                            dataset=train_set,
                            reconstructed=X_valid_compressed,
                            errors=reconstruction_errors,
                        )
                    )
    if config.verify_model.is_calc_recon_errors() == True:
        inspectors.ReconstructionInspector.calculate_reconstrucion_thresholds(
            reconstruction_errors, reconstruction_keys
        )

    if run_latent_prediction:
        if is_latent_vectors_file_exists(binary_paths_len=binary_paths_len):
            latent_vectors_x, metadata = load_latent_vectors(
                binary_paths_len=binary_paths_len
            )
            # PCA_VARIANCE = 0.95
            # pca = PCA(n_components=PCA_VARIANCE)  # or n_components='mle' for automatic
            # latent_mean = latent_vectors_x.mean(axis=0)
            # latent_centered = latent_vectors_x - latent_mean
            # latent_vectors_x = pca.fit_transform(latent_centered)
            # logging.getLogger().info(f"Running PCA before UMAP - components left after PCA, count={len(latent_vectors_x[0])}, variance={PCA_VARIANCE}")

            # mask = select_random_subset(latent_vectors_x, 90)
            # latent_vectors_x = latent_vectors_x[mask]

        else:
            metadata = {
                "labels": latent_vectors_y,
                "pollen_indexes_dict": pollen_indexes_dict,
                "binary_paths": binary_paths,
                "id": int(time.time()),
                "paths": latent_vectors_paths,
                "paths_indexes_dict": paths_indexes_dict,
            }
            save_latent_vectors(latent_vectors=latent_vectors_x, metadata=metadata)
        latent_vectors_x = np.array(latent_vectors_x)
        umap_embeddings = None
        umap_metadata = None
        if config.verify_model.is_plot_pca() == True:
            inspectors.TsneInspector.plot_pca(
                latent_vectors_x,
                metadata["pollen_indexes_dict"],
                labels=metadata["labels"],
            )
        if config.cluster_parameters.run_umap() == True:
            umap_data = inspectors.UmapInspetor.run_umap_options(
                latent_vectors=latent_vectors_x,
                #   labels=np.array(metadata['labels'])[mask].tolist(),
                labels=metadata["labels"],
                name=config.model_save_name,
                color_label_map=metadata["pollen_indexes_dict"],
                plot=config.cluster_parameters.umap.plot,
                latent_id=metadata["id"] if "id" in metadata.keys() else None,
            )
            for umap_embeddings, umap_metadata in umap_data:
                if config.cluster_parameters.run_hdbscan():
                    inspectors.HdbscanInspector.run_dhbscan_options2(
                        umap_embeddings=umap_embeddings,
                        umap_metadata=umap_metadata,
                        model_save_name=config.model_save_name,
                        color_label_map=metadata["pollen_indexes_dict"],
                        with_umap=True,
                    )
        if (
            config.cluster_parameters.run_hdbscan() == True
            and config.cluster_parameters.run_umap() == False
        ):
            inspectors.HdbscanInspector.run_dhbscan_options2(
                umap_embeddings=latent_vectors_x,
                umap_metadata=metadata,
                model_save_name=config.model_save_name,
                color_label_map=metadata["pollen_indexes_dict"],
            )
        if config.cluster_parameters.run_clusterer() == True:
            clusterer.run(
                latent_vectors=latent_vectors_x,
                paths=metadata["paths"],
                paths_indexes_dict=metadata["paths_indexes_dict"],
            )
        if config.cluster_parameters.run_kmeans() == True:
            inspectors.KmeansInspector.run_kmeans(
                latent_vectors=latent_vectors_x,
                labels=metadata["labels"],
                name=config.model_save_name,
                color_label_map=metadata["pollen_indexes_dict"],
            )


def handle(verbose: int = 0):
    set_tf_settings(module_name=ModelBuilderUnsupervisedConfig.config_prop_name)

    config = Config().get(ModelBuilderUnsupervisedConfig)
    binaries_dirs = get_learn_dirs(config.get_pollen_types_binaries_dirs())
    input_filter = get_filter(config.train_parameters.filter_rel_path)
    process_available_data(
        binaries_dirs,
        input_filter,
    )

    keras_trainer = KerasUnsupervisedTrainer(binaries_dirs)

    if config.train_parameters.train_model:
        logging.getLogger().info(
            f"Training model enabled. To disable set 'train_parameters.train_model' to false"
        )
        keras_trainer.train_model(
            epochs=config.train_parameters.epochs, verbose=verbose
        )
    else:
        logging.getLogger().info(
            f"Training model DISABLED. To disable set 'train_parameters.train_model' to true"
        )

    if config.verify_model.verify_model:
        logging.getLogger().info(
            f"Veryfying model enabled. To disable set 'verify_model.verify_model' to false"
        )
        verify_model(keras_trainer)
    else:
        logging.getLogger().info(
            f"Veryfying model DISABLED. To disable set 'verify_model.verify_model' to true"
        )

    if config.cluster_parameters.run_clustering:
        logging.getLogger().info(
            f"Clustering enabled. To disable set 'cluster_parameters.run_clustering' to false"
        )
        verify_model(keras_trainer)
    else:
        logging.getLogger().info(
            f"Clustering DISABLED. To disable set 'cluster_parameters.run_clustering' to true"
        )


if __name__ == "__main__":
    matplotlib.use("TkAgg")  # Use a non-GUI backend (good for servers)
    # matplotlib.use('Agg')  # Use a non-GUI backend (good for servers)
    handle()

import logging

import json
import joblib
import pickle
from functools import partial
from sklearn.decomposition import PCA
import tensorflow as tf
from src.core.json import get_list_int_mapping
from src.core import File, PathHelper
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelRunnerConfig, TypesConfig
from src.modelBuilder.optimizers.TemperatureScaling import (
    TemperatureScalingLayer,
)  # TODO: REF
from src.common.tensorflow import InputModelNames
from src.common.rawData.Signal import RawData
from src.common.rawData.features.FeaturesHandler import FeaturesHandler
from src.modelRunner.predictions.Prediction import Prediction
from src.modelRunner.predictions.datasetHandler import get_unlabeled_dataset
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from src.modelBuilder.datasetHandler import DatasetScaler
import numpy as np
from hdbscan import approximate_predict
import umap
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
import warnings


class KerasPredictor:
    CLUSTERS = {
        4: [0],
        9: [0],
        5: [2],
        6: [2],
        16: [3],
        8: [5],
        10: [6],
        2: [7],
        12: [7],
        0: [8],
        1: [8],
        7: [10],
        46: [11],
        19: [12],
        11: [13],
    }

    def __init__(self, model_path: File, classes: list[str]) -> None:
        self.config = Config.get(ModelRunnerConfig)
        self.pollen_types = Config.get(TypesConfig).pollen_types
        self.custom_objects = {
            "mse": tf.keras.losses.mse,
            "lifetime_unsup_decoder_mse": tf.keras.metrics.MeanSquaredError,
            "scattering_unsup_decoder_mse": tf.keras.metrics.MeanSquaredError,
            "size_decoder_mse": tf.keras.metrics.MeanSquaredError,
            "spectrum_unsup_decoder_mse": tf.keras.metrics.MeanSquaredError,
        }
        self._logger = logging.getLogger()

        self._keras_model = self.get_keras_model(
            model_path,
            custom_objects={
                "TemperatureScalingLayer": partial(
                    TemperatureScalingLayer, classes_count=15
                )
            },
        )

        self._min_max_scalers: dict[MinMaxScaler] = DatasetScaler.load_scanners(
            self.config.get_scaler_path()
        )

        self._knn: KNeighborsClassifier | None = None
        self._kmeans: KMeans | None = None
        self._classes = classes
        self._features_handler = FeaturesHandler(
            pollen_types=None, scattering_cutoff=Consts.SCATTERING_CUTOFF
        )
        self._hdbscan = None
        self._clusterer = None
        self._autoencoder = None
        self._encoder = None
        self._umap: umap.UMAP = None

    def get_keras_model(self, model_path: str, custom_objects=None):
        with tf.device("/GPU:0"):
            if custom_objects is not None:
                try:
                    model = tf.keras.models.load_model(
                        model_path, custom_objects=custom_objects
                    )
                    self._logger.info(f"Running model: {model_path}")
                    return model
                except TypeError as te:
                    if "Could not locate function" in str(te):
                        logging.getLogger().warning(f"Custom function missing during model load: {te}. Trying to load without custom functions.")
                    else:
                        raise
                    
            model = tf.keras.models.load_model(model_path, compile=False)
            self._logger.info(f"Running model: {model_path}")
            return model

    def cluster_filter(self, y_preds, clusters):
        y_preds_filtered = []
        for idx, y_pred in enumerate(y_preds):
            particle_idex = y_pred.argmax()
            particle_name = self.pollen_types[particle_idex]
            allowed_clusters = self.clusters[particle_name]
            cluster = clusters[idx]
            if cluster in allowed_clusters:
                y_preds_filtered.append(y_preds)

        self._logger.info(
            f"Left after cluster filtering count={len(y_preds_filtered)}/{len(y_preds)}"
        )
        return y_preds_filtered

    def lazy_load_attr(self, attr, path):
        value = getattr(self, attr, None)
        if value == None and value != "Error":
            if PathHelper.is_file_exists(path):
                self._logger.info(f"Lazy loading {attr} from the path: {path}")
                value = joblib.load(path)  #
                if value == "Error":
                    raise ValueError(
                        f"{attr} under the path does not exists, path={path}"
                    )
        setattr(self, attr, value)

    def is_valid(self, value):
        if value == None or value == "Error":
            return False
        return True

    def reduce_dimensions_when_reducer_set(self, raw_data_scaled):
        def run_predict():
            model = self.get_keras_model(
                self.config.unsupervised.autoencoder_path, self.custom_objects
            )

            self._encoder = tf.keras.models.Model(
                inputs=model.input,
                outputs=model.get_layer(Consts.AUTOENCODER_LATENT_LAYER_NAME).output,
            )

            return self._encoder.predict(raw_data_scaled)

        latent_vectors = run_predict()
        dim_reducer = self.config.unsupervised.dim_reducer
        if dim_reducer.dim_reducer_to_use == dim_reducer.UMAP_REDUCTOR:
            self.lazy_load_attr("_umap", dim_reducer.umap.path)
            if self.is_valid(self._umap):
                return self._umap.transform(latent_vectors)
        if dim_reducer.dim_reducer_to_use == dim_reducer.PCA_REDUCTOR:
            pca = PCA(n_components=dim_reducer.pca.components, random_state=42)
            return pca.fit_transform(latent_vectors)

        return latent_vectors

    def load_cluster_mapping(self, mapping_path):
        if hasattr(self, "clusters"):
            return
        mapping = get_list_int_mapping(
            mapping_path=mapping_path, ref_keys=self.pollen_types
        )
        self.clusters = mapping

    def scale_data(self, raw_data_set: list[RawData]):
        input_suffix = "_input"
        shapes = {
            InputModelNames.SCATTERING_UNSUP: [120, 24],
            InputModelNames.SPECTRUM_UNSUP: [32, 8],
            InputModelNames.LIFETIME_UNSUP: [64, 4],
            InputModelNames.SIZE: [],
        }

        raw_data_set_dict = [
            x.to_unsup_input_name_dict(scattering_cutoff=Consts.SCATTERING_CUTOFF)
            for x in raw_data_set
        ]
        raw_data_scaled = DatasetScaler.transform_dataset(
            scalers=self._min_max_scalers,
            list_of_arrays_dict=raw_data_set_dict,
            key_suffix=input_suffix,
            shapes=shapes,
        )
        for key in raw_data_scaled:
            raw_data_scaled[key] = np.expand_dims(
                raw_data_scaled[key], axis=-1
            )  # Shape becomes (100, 120, 24, 1)

        return raw_data_scaled

    def cluster_data(self, raw_data_scaled):
        clusters = None
        if self.config.unsupervised.run_unsupervised == True:
            latent_vectors = self.reduce_dimensions_when_reducer_set(raw_data_scaled)
            clusterer = self.config.unsupervised.clusterer
            if clusterer.clusterer_to_use == clusterer.KNN_CLUSTERER:
                self.lazy_load_attr("_knn", clusterer.knn.path)
                self.load_cluster_mapping(clusterer.knn.mapping_path)
                if self.is_valid(self._knn):
                    clusters = self._knn.predict(latent_vectors)
            elif clusterer.clusterer_to_use == clusterer.KMEANS_CLUSTERER:
                self.lazy_load_attr("_kmeans", clusterer.kmeans.path)
                self.load_cluster_mapping(clusterer.kmeans.mapping_path)
                if self.is_valid(self._kmeans):
                    clusters = self._kmeans.predict(latent_vectors)
            elif clusterer.clusterer_to_use == clusterer.HDBSCAN_CLUSTERER:
                self.lazy_load_attr("_hdbscan", clusterer.hdbscan.path)
                self.load_cluster_mapping(clusterer.hdbscan.mapping_path)
                if self.is_valid(self._hdbscan):
                    clusters, _ = approximate_predict(self._hdbscan, latent_vectors)
            elif clusterer.clusterer_to_use == clusterer.MINI_BATCH_KMEANS_CLUSTERER:
                self.lazy_load_attr("_clusterer", clusterer.mini_batch_kmeans.path)
                self.load_cluster_mapping(clusterer.mini_batch_kmeans.mapping_path)
                if self.is_valid(self._clusterer):
                    clusters = self._clusterer.predict(latent_vectors)
            else:
                self._logger.debug("Clustering skipped not clusters set")
                return clusters

            counter = Counter(clusters)
            self._logger.info(f"Clusters found\n: {dict(counter)}")

        return clusters

    def scale_callback(self, raw_data_set: list[RawData]):
        shapes = {
            InputModelNames.SCATTERING_UNSUP: [120, 24],
            InputModelNames.SPECTRUM_UNSUP: [32, 8],
            InputModelNames.LIFETIME_UNSUP: [64, 4],
            InputModelNames.SIZE: [],
        }

        raw_data_set_dict = [
            x.to_unsup_input_name_dict(scattering_cutoff=Consts.SCATTERING_CUTOFF)
            for x in raw_data_set
        ]
        raw_data_scaled = DatasetScaler.transform_dataset(
            scalers=self._min_max_scalers,
            list_of_arrays_dict=raw_data_set_dict,
            shapes=shapes,
        )
        props = np.array(
            [
                (x.type, np.datetime64(x.time, "us").astype(np.int64))
                for x in raw_data_set
            ]
        )
        raw_data_updated = {
            InputModelNames.SCATTERING: np.array(
                raw_data_scaled[InputModelNames.SCATTERING_UNSUP], dtype=np.float32
            ),
            InputModelNames.SPECTRUM: np.array(
                raw_data_scaled[InputModelNames.SPECTRUM_UNSUP], dtype=np.float32
            ),
            InputModelNames.LIFETIME: np.array(
                raw_data_scaled[InputModelNames.LIFETIME_UNSUP], dtype=np.float32
            ),
            InputModelNames.SIZE: np.array(
                raw_data_scaled[InputModelNames.SIZE], dtype=np.float32
            ),
            "time": props[:, 1],
        }
        return raw_data_updated

    def map_preds_to_model(self, y_preds, raw_data_set):
        preds: list[Prediction] = []
        for idx, y_pred in enumerate(y_preds):
            preds.append(
                Prediction(
                    predictions=y_pred,
                    timestamp=raw_data_set[idx].time,
                    classes=self._classes,
                )
            )
        return preds

    def predict(self, raw_data_set: list[RawData]) -> list[Prediction]:
        raw_data_scaled = self.scale_data(raw_data_set)

        clusters = self.cluster_data(raw_data_scaled)
        y_preds = self._keras_model.predict(raw_data_scaled, verbose=0)

        if clusters is not None:
            y_preds = self.cluster_filter(y_preds, clusters)

        preds: list[Prediction] = self.map_preds_to_model(y_preds, raw_data_set)

        return preds

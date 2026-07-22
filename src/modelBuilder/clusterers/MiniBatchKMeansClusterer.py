import logging
from src.core import PathHelper
from src.common.config import Config, ModelBuilderUnsupervisedConfig
import joblib
from sklearn.cluster import MiniBatchKMeans
from collections import Counter
import os
from src.core.files.FileWriter import write_data, AccessType
import pandas as pd
from warnings import simplefilter

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


class MiniBatchKMeansClusterer:
    def __init__(self):
        self._config = Config.get(ModelBuilderUnsupervisedConfig)
        self._logger = logging.getLogger()
        self._clusterer_dir = (
            f"{self._config.get_clusterer_path()}/{self._config.model_save_name}"
        )

    def run(self, latent_vectors, paths, paths_indexes_dict):
        self._logger.info(
            f"Running 'MiniBatchKMeansClusterer', save path={self._clusterer_dir}"
        )
        for cluster_size in self._config.cluster_parameters.clusterer.cluster_sizes:
            self.run_clusterer(latent_vectors, cluster_size, paths, paths_indexes_dict)

    def run_clusterer(
        self,
        latent_vectors,
        cluster_size,
        paths,
        paths_indexes_dict,
    ):

        clusterer = None
        clusters_count = cluster_size
        file_path = PathHelper.join_rel_path(
            self._clusterer_dir, f"mini_batch_kmeans_clusterer_{clusters_count}"
        )
        os.makedirs(self._clusterer_dir, exist_ok=True)
        clusterer_path = f"{file_path}.pk1"
        if PathHelper.is_file_exists(clusterer_path):
            message = f"Clusterer found under path will be used for training, path='{clusterer_path}.pk1'"
            logging.getLogger().info(message)

            clusterer = joblib.load(clusterer_path)

        if clusterer is None:
            logging.getLogger().info(
                f"Clusterer NOT found. A new one will be created..., clusters_count={clusters_count}"
            )
            clusterer = MiniBatchKMeans(
                n_clusters=clusters_count, batch_size=100, n_init=10
            )
        clusterer.fit(latent_vectors)  # Update with new data
        if not PathHelper.is_file_exists(clusterer_path):
            logging.getLogger().info(
                f"Saving clusteler under path, path='{clusterer_path}'"
            )
            joblib.dump(clusterer, clusterer_path)

        labels = clusterer.predict(latent_vectors)
        result = {}

        paths_indexes_dict_inverted = {v: k for k, v in paths_indexes_dict.items()}
        for v, l in zip(labels, paths):
            result.setdefault(paths_indexes_dict_inverted[l], []).append(v)

        counted_clusters = {
            path: self.get_full_counter(clusters, clusters_count)
            for path, clusters in result.items()
        }
        logging.getLogger().info(
            f"Counted particles within clusters {counted_clusters}"
        )

        df_s = []
        for path, clusters in counted_clusters.items():
            df_s.append(
                self.save_progress(
                    processed_file_name=PathHelper.get_base_name(path),
                    counter=clusters,
                )
            )
        df = pd.concat(df_s, ignore_index=True)
        logging.getLogger().info(f"Clusters saved under the path: {file_path}")
        write_data(
            f"{file_path}_PROGRESS.csv",
            df.to_csv(header=True, index=False),
            access_type=AccessType.Write,
            new_line_on_access=False,
        )

    def get_full_counter(self, clusters, clusters_count):
        counter = Counter(clusters)
        return {
            i: counter.get(i, 0) for i in range(clusters_count)
        }  # adds missing clusters

    def save_progress(self, processed_file_name, counter: Counter):
        df = pd.DataFrame.from_dict(dict(sorted(counter.items())), orient="index").T
        total_sum = df[list(counter.keys())].sum(axis=1)
        df = df.add_prefix("Cluster_")
        df.insert(0, "File(s)", processed_file_name)
        df["Sum"] = total_sum
        df["File(s)_2"] = processed_file_name
        for key, value in counter.items():  # Exclude 'Sum' column
            df[f"{key}_pct"] = value / df["Sum"]

        sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        total_items = len(sorted_items)
        for percentile in self._config.cluster_parameters.clusterer.cluster_percentiles:
            percentile_value = total_sum[0] * percentile
            aggregated_sum = 0
            for i in range(total_items):
                row_value = None
                if aggregated_sum < percentile_value:
                    row_value = sorted_items[i][0]
                    aggregated_sum += sorted_items[i][1]
                df[f"{percentile}_perentile{i+1}"] = row_value
        return df

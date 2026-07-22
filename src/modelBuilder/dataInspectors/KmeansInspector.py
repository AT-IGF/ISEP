import logging
from pathlib import Path
from sklearn.decomposition import PCA, TruncatedSVD

from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.core.plots.plotting_utils import plt_show
from src.modelBuilder.dataInspectors.UmapInspetor import plot_embeddings
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import (
    davies_bouldin_score,
    normalized_mutual_info_score,
)
from sklearn.preprocessing import QuantileTransformer, normalize
from joblib import dump
from src.core import PathHelper


def run_kmeans(latent_vectors, labels, name, color_label_map={}):
    config = Config.get(ModelBuilderUnsupervisedConfig).cluster_parameters.kmeans
    logging.getLogger().info("KMeans started")
    if sum(np.array(labels) != -1) == 0:
        logging.getLogger().info("Kmeans requires known samples to be set. Skipping.")
        return

    initial_centroids, known_mask, n_clusters, labels = get_centroids(
        labels, latent_vectors
    )

    kmeans = KMeans(
        n_clusters=n_clusters, init=initial_centroids, n_init=1, random_state=0
    )
    logging.getLogger().info("Kmeans fitting")

    if config.centroids_mode == config.CENTROIDS_BY_KNOWN_AND_UNKOWN:
        mask = ~np.isnan(latent_vectors).any(axis=1)

        latent_vectors = latent_vectors[mask]
        labels = labels[mask]

    kmeans.fit(latent_vectors)
    predicted_labels = kmeans.labels_
    print_summary_n_clusters(labels=labels, predicted_labels=kmeans.labels_)

    save(
        kmeans=kmeans,
        dir=Config.get(ModelBuilderUnsupervisedConfig).get_kmeans_path(),
        file=f"{name}-2cl-kmeans.joblib",
    )

    davies_bouldin = davies_bouldin_score(latent_vectors, predicted_labels)
    logging.getLogger().info(f"Davies-Bouldin score: {davies_bouldin}")

    plot(latent_vectors, kmeans, known_mask, labels, color_label_map)


def save(kmeans, dir, file):
    Path(dir).mkdir(parents=True, exist_ok=True)
    save_path = PathHelper.join_path(dir, file)
    logging.getLogger().info(f"Saving KMeans under the path={save_path}")
    dump(kmeans, save_path)


def print_summary_n_clusters(predicted_labels, labels):
    import pandas as pd

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    cluster_df = pd.DataFrame({"Cluster": predicted_labels, "Original Class": labels})

    cluster_class_ct = pd.crosstab(
        index=cluster_df["Cluster"],
        columns=cluster_df["Original Class"],
        margins=True,
        margins_name="Total",
    )

    percentage_ct = cluster_class_ct.div(cluster_class_ct["Total"], axis=0) * 100
    percentage_ct = percentage_ct.round(2).astype(str) + "%"

    full_report = cluster_class_ct.astype(str) + " (" + percentage_ct + ")"

    cluster_class_ct["Majority Class"] = cluster_class_ct.drop("Total", axis=1).idxmax(
        axis=1
    )
    cluster_class_ct["Majority Count"] = cluster_class_ct.drop("Total", axis=1).max(
        axis=1
    )

    logging.getLogger().info("Cluster-Class Distribution (Counts with Percentages):")
    logging.getLogger().info("\n" + str(full_report))
    logging.getLogger().info("\nCluster Majority Class Summary:")
    logging.getLogger().info(
        "\n" + str(cluster_class_ct[["Majority Class", "Majority Count", "Total"]])
    )


def get_centroids(labels, latent_vectors):
    config = Config.get(ModelBuilderUnsupervisedConfig).cluster_parameters.kmeans
    if config.CENTROIDS_BY_CLASS:
        logging.getLogger().info("Kmeans centroids by class")
        labels = np.array(labels)
        known_mask = labels != -1
        known_labels = labels[known_mask]
        unique_classes = np.unique(known_labels)
        n_clusters = len(unique_classes)

        initial_centroids = np.array(
            [latent_vectors[(labels == cls)].mean(axis=0) for cls in unique_classes]
        )
        return initial_centroids, known_mask, n_clusters, labels
    else:
        logging.getLogger().info(
            "Kmeans centroids by known (1) and unknown (-1) samples"
        )
        labels_common = []
        for label in labels:
            if label != -1:
                labels_common.append(1)
            else:
                labels_common.append(-1)

        logging.getLogger().info(
            f"labels min={min(labels_common)}, max={max(labels_common)}"
        )
        labels = np.array(labels_common)
        known_mask = labels == 1
        unknown_mask = labels == -1

        logging.getLogger().info("Kmeans centroids")
        centroid_known = latent_vectors[known_mask].mean(axis=0)
        centroid_unknown = latent_vectors[unknown_mask].mean(axis=0)

        initial_centroids = np.array([centroid_known, centroid_unknown])
        return initial_centroids, known_mask, 2, np.array(labels_common)


def plot(latent_vectors, kmeans, known_mask, labels, color_label_map):
    predicted_labels = kmeans.labels_
    pca = TruncatedSVD(n_components=3, random_state=0)
    latent_3d = pca.fit_transform(latent_vectors)
    centroids_3d = pca.transform(kmeans.cluster_centers_)
    logging.getLogger().info("Plotting...")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(
        latent_3d[:, 0],
        latent_3d[:, 1],
        latent_3d[:, 2],
        c=predicted_labels,
        cmap="viridis",
        alpha=0.6,
        s=0.5,
        label="Data Points",
    )
    ax.scatter(
        latent_3d[known_mask, 0],
        latent_3d[known_mask, 1],
        latent_3d[known_mask, 2],
        c="red",
        marker="x",
        s=0.3,
        label="Known Samples",
    )
    ax.scatter(
        centroids_3d[:, 0],
        centroids_3d[:, 1],
        centroids_3d[:, 2],
        c="black",
        marker="D",
        s=0.3,
        label="K-Means Centroids",
    )

    ax.set_title("3D PCA Projection of K-Means Clustering with Partial Labels")
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    ax.set_zlabel("Principal Component 3")
    ax.legend()
    plt_show(plt.gcf())

    plot_embeddings(
        embeddings=latent_3d,
        components_count=3,
        color_label_map=color_label_map,
        labels=labels,
        path="",
    )

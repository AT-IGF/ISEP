from contextlib import contextmanager
import io
import logging
import os
import numpy as np
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.core import PathHelper
from src.core.plots.plotting_utils import plt_show
import joblib
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import pairwise_distances
from src.modelBuilder.dataInspectors.helpers.Normalization import normalize_data
import umap
from src.modelBuilder.dataInspectors.helpers import save_embeddings, load_embeddings
from matplotlib.colors import ListedColormap
import time
import matplotlib
from sklearn.manifold import trustworthiness
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from src.common import Consts


def plot_embeddings(
    embeddings,
    components_count,
    color_label_map,
    labels,
    path="",
    alpha=None,
    remove_noise=False,
    cbar_alpha=None,
):
    if components_count > 3:
        logging.getLogger().info(
            f"Ploting 3 dimensions due to unability to plot >3 dimensions, dimensions_count={components_count}, plotter=TruncatedSVD"
        )
        svd = TruncatedSVD(n_components=3)
        embeddings = svd.fit_transform(embeddings)
        components_count = 3
    labels = np.array(labels)

    logger = logging.getLogger()
    logger.info(f"Plotting...")

    desc = ", ".join(
        [
            f"{key}: {value} ({Consts.PLOT_COLORS[value + 1]})"
            for key, value in sorted(color_label_map.items(), key=lambda x: x[1])
        ]
    )  # +1 due to cmap
    logging.getLogger().info(f"Labels: {desc}")

    colors_for_map = Consts.PLOT_COLORS[: len(color_label_map.values())]
    if remove_noise:
        logger.info(f"Unknown label will not be visible, unkown_label=-1")
        # mask = labels != -1
        # embeddings = embeddings[mask]
        # labels = labels[mask]
        colors_for_map = [
            matplotlib.colors.to_rgba(color)
            for color in Consts.PLOT_COLORS[: len(color_label_map.values())]
        ]
        for idx, color in enumerate(colors_for_map):
            if color[3] != 0:
                colors_for_map[idx] = (*colors_for_map[idx][:3], alpha)

    if alpha == None:
        alpha = 1
    marker_size = 0.5

    cmap = ListedColormap(colors_for_map)
    fig = plt.figure(figsize=(15, 9))
    fig.canvas.manager.set_window_title(path)
    if components_count == 3:
        ax = fig.add_subplot(111, projection="3d")
        sc = ax.scatter(
            embeddings[:, 0],
            embeddings[:, 1],
            embeddings[:, 2],
            c=labels,
            cmap=cmap,
            s=marker_size,
            alpha=None if remove_noise else alpha,
        )
    elif components_count == 2:
        ax = fig.add_subplot(111)
        sc = ax.scatter(
            embeddings[:, 0],
            embeddings[:, 1],
            c=labels,
            cmap=cmap,
            s=marker_size,
            alpha=alpha,
        )
    elif components_count == 1:
        jitter = np.random.normal(0, 0.05, size=embeddings[:, 0].shape)
        sc = ax.scatter(
            embeddings[:, 0], jitter, c=labels, cmap=cmap, s=marker_size, alpha=alpha
        )
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
    else:
        logger.info(
            f"Unable to plot, components_count={components_count} is not between 1-3. Skipping."
        )

    ax.set_xlabel("Feature 1", labelpad=10)
    ax.set_ylabel("Feature 2" if components_count >= 2 else "", labelpad=10)
    if components_count == 3:
        ax.set_zlabel("Feature 3", labelpad=10)
    plt.subplots_adjust(bottom=0.1, top=1)
    if labels is not None:
        print(np.array(list(color_label_map.values())) + 0.5)
        label_labs = np.array(list(color_label_map.values()))
        cbar = plt.colorbar(
            sc,
            ax=ax,
            ticks=np.linspace(
                min(label_labs) + 0.5, max(label_labs) - 0.5, num=len(label_labs)
            ),
            orientation="horizontal",
            shrink=0.5,
            pad=-0.000005,
        )
        if cbar_alpha != None:
            cbar.solids.set_alpha(cbar_alpha)  # colorbar alpha
        colorbar_labels = sorted(color_label_map.keys(), key=color_label_map.get)
        colorbar_labels_naming_fixed = [
            Consts.FOLDER_NAME_MAPPING.get(item, item) for item in colorbar_labels
        ]
        cbar.set_ticklabels(colorbar_labels_naming_fixed, rotation=70, fontsize=16)

    vmin = min(color_label_map.values())
    vmax = max(color_label_map.values())
    if vmax == 0:
        vmax = 1  # avoid division by zero

    handles = []
    for label, val in color_label_map.items():

        handle = plt.Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markersize=5,
            markerfacecolor=Consts.PLOT_COLORS[val],
            markeredgecolor="black",
            label=label,
        )
        handles.append(handle)

    # plt.legend(handles=handles, title="Categories", ncol=3)
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, dpi=800)
    # plt.legend()
    plt_show(plt.gcf())


def continuity_score(X_high: np.ndarray, X_low: np.ndarray, k: int = 10) -> float:
    n = X_high.shape[0]
    D_high = pairwise_distances(X_high)
    D_low = pairwise_distances(X_low)
    rank_high = np.argsort(np.argsort(D_high, axis=1), axis=1)
    rank_low = np.argsort(np.argsort(D_low, axis=1), axis=1)

    C = 0.0
    for i in range(n):
        neigh_low = np.where(rank_low[i] <= k)[0]
        for j in neigh_low:
            if rank_high[i, j] > k:
                C += rank_high[i, j] - k

    denom = n * k * (2 * n - 3 * k - 1) / 2.0
    cont = 1.0 - (2.0 * C) / denom
    return float(cont)


N_NEIGHBORS = 500
N_COMPONENTS = 3
MIN_DIST = 0.1
SPREAD = 1
TARGET_WEIGHT = 0.1
METRIC = "cosine"  # euclidean, cosine
TARGET_METRIC = "categorical"
OUTPUT_METRIC = None
SAMPLE_RATIO = 0.5
PRE_UMAP_NORMALIZATION = "l2"  # l2, z_score
LATENT_ID = None
TARGET_ENABLED = False


def get_paths(name):
    config = Config().get(ModelBuilderUnsupervisedConfig)

    umap_file_path = config.get_umap_path()
    csv_path = f"{umap_file_path}/{name}-umap.csv"
    latent_id = ""
    if LATENT_ID is not None:
        latent_id = f"-{LATENT_ID}_latent_id"
    output_metric = ""
    if OUTPUT_METRIC is not None:
        output_metric = f"-{OUTPUT_METRIC}_out_m"
    target_enabled = ""
    if TARGET_ENABLED == True:
        target_enabled = f"-{str(TARGET_ENABLED)}te"

    recuder_prefix = f"{umap_file_path}{latent_id}-{PRE_UMAP_NORMALIZATION}_pre_norm-{str(SAMPLE_RATIO).replace('.', '_')}sr-{METRIC}_m-{TARGET_METRIC}_tm{output_metric}{target_enabled}-{str(TARGET_WEIGHT).replace('.', '_')}tw-{str(MIN_DIST).replace('.', '_')}md-{str(SPREAD).replace('.', '_')}_sp-{N_NEIGHBORS}n-{N_COMPONENTS}D"
    reducer_path = f"{recuder_prefix}-umap.pk1"
    embeddings_path = f"{recuder_prefix}-umap-embeddings.h5"
    plot_path = f"{recuder_prefix}-umap-plot.png"
    return {
        "reducer_path": reducer_path,
        "embeddings_path": embeddings_path,
        "plot_path": plot_path,
    }


def calculate_metrics(reducer, latent_vectors_test):
    try:
        logging.getLogger().info(
            f"UMAP calculating test emebddings, samples count={len(latent_vectors_test)}"
        )
        latent_vectors_test_embedded = reducer.transform(latent_vectors_test)
        logging.getLogger().info(f"UMAP calculating trustworthiness")
        trust_val = trustworthiness(
            latent_vectors_test, latent_vectors_test_embedded, n_neighbors=N_NEIGHBORS
        )
        logging.getLogger().info(f"UMAP trustworthiness={trust_val * 100:.2f}")
        c_score = continuity_score(
            X_high=latent_vectors_test,
            X_low=latent_vectors_test_embedded,
            k=N_NEIGHBORS,
        )
        logging.getLogger().info(f"UMAP continuity_score={c_score * 100:.2f}")
    except Exception as e:
        logging.getLogger().warning("An error ocurred during metrics calcualtion")


def downsample_set(embeddings, labels):
    labels = np.array(labels)
    n_samples = int(len(embeddings) * SAMPLE_RATIO)
    np.random.seed(42)
    indices = np.random.choice(len(embeddings), n_samples, replace=False)
    np.random.seed(None)

    logging.getLogger().info(
        f"UMAP set downsampled with ratio={SAMPLE_RATIO}, samples left count={n_samples}/{len(embeddings)}"
    )
    X_downsampled = embeddings[indices]
    y_downsampled = labels[indices]

    return X_downsampled, y_downsampled.tolist()


class LogStream(io.TextIOBase):
    def __init__(self):
        self.msg = ""

    def write(self, msg):
        if msg != "\n":
            self.msg += msg
        else:
            logging.getLogger("umap").info(self.msg)
            self.msg = ""


@contextmanager
def capture_umap_output():
    import sys

    stream = LogStream()
    old = sys.stdout
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = old


def run_umap(latent_vectors, labels, name, color_label_map={}, plot=True):
    latent_vectors = normalize_data(
        embeddings=latent_vectors, normaliation=PRE_UMAP_NORMALIZATION
    )
    latent_vectors, labels = downsample_set(latent_vectors, labels)
    latent_vectors_train, latent_vectors_test, labels_train, labels_test = (
        train_test_split(
            latent_vectors,
            labels,
            random_state=42,
            train_size=1 - 2500 / len(latent_vectors),
        )
    )
    paths = get_paths(name=name)
    reducer_path = paths["reducer_path"]
    embeddings_path = paths["embeddings_path"]

    # if PathHelper.is_file_exists(reducer_path):
    #     return None, None

    metadata = None
    if not PathHelper.is_file_exists(reducer_path):
        logging.getLogger().info(f"Fitting umap, path={reducer_path}")
        with capture_umap_output():
            reducer = umap.UMAP(
                n_components=N_COMPONENTS,
                n_neighbors=N_NEIGHBORS,
                metric=METRIC,
                min_dist=MIN_DIST,
                spread=SPREAD,
                target_weight=TARGET_WEIGHT,  # Balance between data structure and labels
                target_metric=TARGET_METRIC,
                output_metric=OUTPUT_METRIC,
                verbose=True,
            )
            config = (
                Config().get(ModelBuilderUnsupervisedConfig).cluster_parameters.umap
            )
            if TARGET_ENABLED == True:
                reducer.fit(X=latent_vectors_train, y=labels_train)
            else:
                reducer.fit(X=latent_vectors_train)

            logging.getLogger().info(f"Saving umap")
            joblib.dump(reducer, reducer_path)
            logging.getLogger().info(f"Umap saved under path={reducer_path}")
            metadata = {
                "map": color_label_map,
                "labels": labels_train,
                "n_neighbors": N_NEIGHBORS,
                "umap_components": N_COMPONENTS,
                "id": int(time.time()),
                "sample_ratio": SAMPLE_RATIO,
            }
            save_embeddings(
                path=embeddings_path, embeddings=reducer.embedding_, params=metadata
            )
            calculate_metrics(reducer, latent_vectors_test)
    else:
        logging.getLogger().info(f"File already exists. Skipping, path={reducer_path}")
        reducer: umap.UMAP = joblib.load(reducer_path)
        _, metadata = load_embeddings(path=embeddings_path)

    if not PathHelper.is_file_exists(reducer_path):
        logging.getLogger().warning(
            f"File NOT found, umap must be trained first. Path={reducer_path}"
        )
        return

    embeddings = reducer.embedding_

    if metadata is not None:
        color_label_map = metadata["map"]
        labels = metadata["labels"]
        if "umap_components" in metadata:
            umap_components = metadata["umap_components"]
        if "n_neighbors" in metadata:
            n_neighbors = ["n_neighbors"]

    if plot == True:
        # embeddings_for_plot = embeddings
        # if N_COMPONENTS > 3:
        #     X_pca_plot = PCA(n_components=3)
        #     embeddings_for_plot = X_pca_plot.fit_transform(embeddings)
        plot_embeddings(
            embeddings=latent_vectors_train,
            components_count=N_COMPONENTS,
            color_label_map=color_label_map,
            labels=metadata["labels"],
            path=paths["plot_path"],
        )

    return embeddings, metadata


def is_umap_trained(name):
    paths = get_paths(name=name)
    return PathHelper.is_file_exists(paths["reducer_path"])


def run_umap_options(
    latent_vectors, labels, name, color_label_map={}, plot=True, latent_id=None
):
    global N_NEIGHBORS, N_COMPONENTS, MIN_DIST, PRE_UMAP_NORMALIZATION, METRIC, LATENT_ID, OUTPUT_METRIC, TARGET_METRIC, TARGET_WEIGHT, SPREAD, SAMPLE_RATIO, TARGET_ENABLED
    LATENT_ID = latent_id
    import itertools

    config = Config().get(ModelBuilderUnsupervisedConfig).cluster_parameters.umap
    TARGET_ENABLED = config.target_enabled
    TARGET_METRIC = config.target_metric
    TARGET_WEIGHT = config.target_weight
    SPREAD = config.spread
    SAMPLE_RATIO = config.sample_ratio
    datas = [
        {
            "N_NEIGHBORS": config.n_neighbors,
            "N_COMPONENTS": config.n_components,
            "MIN_DIST": config.min_distance,
            "PRE_UMAP_NORMALIZATION": [config.pre_umap_normalization],
            "METRIC": [config.metric],
            "OUTPUT_METRIC": [config.output_metric],
        }
    ]

    logging.getLogger().info(f"UMAP data to procees={datas}")

    for data in datas:
        keys = list(data.keys())
        for key_combination in itertools.combinations(keys, len(keys)):
            for items in itertools.product(*[data[key] for key in key_combination]):
                N_NEIGHBORS = items[keys.index("N_NEIGHBORS")]
                N_COMPONENTS = items[keys.index("N_COMPONENTS")]
                MIN_DIST = items[keys.index("MIN_DIST")]
                PRE_UMAP_NORMALIZATION = items[keys.index("PRE_UMAP_NORMALIZATION")]
                METRIC = items[keys.index("METRIC")]
                OUTPUT_METRIC = items[keys.index("OUTPUT_METRIC")]

                logging.getLogger().info(
                    f"N_NEIGHBORS={N_NEIGHBORS}, N_COMPONENTS={N_COMPONENTS}, MIN_DIST={MIN_DIST}, MIN_DIST={PRE_UMAP_NORMALIZATION}, METRIC={METRIC}, OUTPUT_METRIC={OUTPUT_METRIC}, TARGET_METRIC={TARGET_METRIC}, TARGET_WEIGHT={TARGET_WEIGHT}, SPREAD={SPREAD}, SAMPLE_RATIO={SAMPLE_RATIO}, TARGET_ENABLED={TARGET_ENABLED}"
                )
                # run_umap(latent_vectors[:], labels[:], name, color_label_map, plot)
                yield run_umap(
                    latent_vectors[:], labels[:], name, color_label_map, plot
                )

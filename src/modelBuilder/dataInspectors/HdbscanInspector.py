import logging
from hdbscan import HDBSCAN
import numpy as np
import matplotlib.pyplot as plt
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.core.plots.plotting_utils import plt_show
from src.core import PathHelper
from src.modelBuilder.dataInspectors.helpers.Normalization import normalize_data
from src.modelBuilder.dataInspectors.helpers import save_hdbscan, load_hdbscan
from .UmapInspetor import plot_embeddings
from sklearn.metrics import adjusted_rand_score, homogeneity_score
from collections import Counter
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
import itertools

logger = logging.getLogger()


def plot_hdbscan(
    X, labels, partially_known_labels, save_path, alpha=1, remove_noise=False
):
    """
    partially_known_labels - label to compare with the label
    """
    dim_count = len(X[0])
    if dim_count > 3:
        svd = PCA(n_components=3)
        X = svd.fit_transform(X)
        logging.getLogger().info(
            f"Plot dimensions to 3 due to inability to plot to many dimensions, dimensions_count={dim_count}"
        )

    logger.info(f"HDBSCAN plotting...")
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")
    partially_known_labels = set(labels)
    colors = plt.cm.get_cmap("turbo", 6)

    legend_elements = []
    for k in partially_known_labels:
        if k == -1:
            if remove_noise:
                continue
            # Black used for noise.
            col = [0, 0, 0, 1]
        else:
            col = colors(k)

        class_member_mask = labels == k
        xyz = X[class_member_mask]
        label = f"Cluster {k}" if k != -1 else "Noise"
        if len(xyz[0]) == 3:
            sc = ax.scatter(
                xyz[:, 0],
                xyz[:, 1],
                xyz[:, 2],
                c=[col],
                marker="o",
                # edgecolor='k',
                s=0.1,
                alpha=alpha,
                label=label,
            )
        if len(xyz[0]) == 2:
            sc = ax.scatter(
                xyz[:, 0],
                xyz[:, 1],
                c=[col],
                marker="o",
                # edgecolor='k',
                s=0.1,
                alpha=alpha,
                label=label,
            )
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=label,
                markerfacecolor=col,
                markersize=8,
            )
        )

    plt.title("HDBSCAN Clustering Results")

    # Add the legend
    ax.legend(handles=legend_elements)
    ax.set_xlabel("Feature 1", labelpad=10)
    ax.set_ylabel("Feature 2", labelpad=10)
    ax.set_zlabel("Feature 3", labelpad=10)
    fig.canvas.manager.set_window_title(save_path)
    plt.savefig(save_path, dpi=800)
    logger.info(f"HDBSCAN saved under path={save_path}")
    logger.info(f"Showing plot")
    plt_show(plt.gcf())
    plt.close()


def cluster_purity(true_labels, pred_labels):
    # Mask out the unknown labels (-1)
    mask = true_labels != -1
    true_known = true_labels[mask]
    pred_known = np.array(pred_labels)[mask].tolist()

    # For each predicted cluster, count the most frequent true label
    total_correct = 0
    unique_clusters = np.unique(pred_known)
    for cluster in unique_clusters:
        indices = np.where(pred_known == cluster)[0]
        if len(indices) == 0:
            continue
        true_in_cluster = true_known[indices]
        # The most common true label in this cluster
        most_common_label, count = Counter(true_in_cluster).most_common(1)[0]
        total_correct += count

    purity = total_correct / len(true_known)
    return purity


def cluster_fmeasure(true_labels, pred_labels):
    mask = true_labels != -1
    true_known = true_labels[mask]
    pred_known = pred_labels[mask]

    unique_true = np.unique(true_known)
    f1_scores = []
    weights = []

    for label in unique_true:
        true_indices = np.where(true_known == label)[0]
        best_f1 = 0
        for cluster in np.unique(pred_known):
            cluster_indices = np.where(pred_known == cluster)[0]
            intersection = len(np.intersect1d(true_indices, cluster_indices))
            if intersection == 0:
                continue
            precision = intersection / len(cluster_indices)
            recall = intersection / len(true_indices)
            f1 = 2 * precision * recall / (precision + recall)
            best_f1 = max(best_f1, f1)
        f1_scores.append(best_f1)
        weights.append(len(true_indices))

    weighted_f = np.sum(np.array(f1_scores) * np.array(weights)) / np.sum(weights)
    return weighted_f


def get_clutser_assigment(cluster_labels, true_labels, csv_prefix=""):
    df = pd.DataFrame(
        {
            "cluster": cluster_labels,
            "class": true_labels,
        }
    )

    ct = pd.crosstab(df["cluster"], df["class"], margins=True, margins_name="Total")

    ct_summary = ct.drop(index="Total", columns="Total")
    ct_calc = ct_summary.iloc[:, 1:]

    if ct_calc.size == 0:
        logger.info(
            f"Cluster asigmnet size is 0. assigments: {dict(Counter(true_labels))}"
        )
        return
    max_heading = ct_calc.idxmax(axis=1)
    max_counts = ct_calc.max(axis=1)
    row_totals = ct_calc.sum(axis=1)
    share = max_counts / row_totals

    ct.loc[ct.index != "Total", "max_heading"] = max_heading
    ct.loc[ct.index != "Total", "max_counts"] = max_counts
    ct.loc[ct.index != "Total", "share"] = share

    def compute_share_row(row):
        # row.name is the category label (not "Total" because we exclude that later)
        # row["max_heading"] holds the column name where the maximum count is found.
        col = row["max_heading"]
        # Get the count in that column for this row
        value = row[col]
        # Get the column total from the "Total" row
        total_for_col = ct.loc["Total", col]
        return value / total_for_col if total_for_col != 0 else 0

    ct.loc[ct.index != "Total", "share_row"] = ct.loc[ct.index != "Total"].apply(
        compute_share_row, axis=1
    )

    path_prefix = get_path_prefix() + f"_class_counts{csv_prefix}.csv"
    ct.to_csv(path_prefix)

    return ct


# METRICS = []
def print_metrics(partial_labels, labels, csv_prefix=""):
    mask = partial_labels != -1
    true_known = partial_labels[mask]
    pred_known = np.array(labels)[mask].tolist()

    global logger
    adjusted_rand_score, homogeneity_score
    purity = cluster_purity(true_labels=partial_labels, pred_labels=labels)
    f_measure = cluster_fmeasure(true_labels=partial_labels, pred_labels=labels)
    ari = adjusted_rand_score(true_known, pred_known)
    homogeneity = homogeneity_score(true_known, pred_known)
    cluster_assigment = get_clutser_assigment(partial_labels, labels, csv_prefix)

    logger.info(f"HDBSCAN Purity={purity * 100:.2f}%")
    logger.info(f"HDBSCAN F-measure={f_measure * 100:.2f}%")
    logger.info(f"ARI={ari * 100:.2f}%")
    logger.info(f"homogeneity_score={homogeneity * 100:.2f}%")
    logger.info(f"Cluster-Class Counts:\n {cluster_assigment}")
    path_prefix = get_path_prefix() + f"_class_counts_metadata{csv_prefix}.csv"
    df = pd.DataFrame(
        {
            "ari": [ari],
            "homogeneity": [homogeneity],
            "f_measure": [f_measure],
            "purity": [purity],
            "PRE_PCA_NORMALIZATION": [PRE_PCA_NORMALIZATION],
            "PCA_COMPONENTS": [PCA_COMPONENTS],
            "POST_PCA_NORMALIZATION": [POST_PCA_NORMALIZATION],
            "METRIC": [METRIC],
            "MIN_CLUSTER_SIZE": [MIN_CLUSTER_SIZE],
            "MIN_SAMPLES": [MIN_SAMPLES],
            "CLUSTER_SELECTION_ELIPSON": [CLUSTER_SELECTION_ELIPSON],
            "ALPHA": [ALPHA],
            "CLUSTER_SELECTION_METHOD": [CLUSTER_SELECTION_METHOD],
            "SAMPLE_RATIO": [SAMPLE_RATIO],
            "TRANSFORMATION": [TRANSFORMATION],
            "UMAP_ID": [UMAP_ID],
            "MODEL_NAME": [MODEL_NAME],
        }
    )
    df.to_csv(path_prefix)
    # METRICS.append([purity, f_measure])
    # logger.info(f"Cluster-Stability score: persistence={clusterer.cluster_persistence_}, stabilities={clusterer.cluster_stabilities_}")


def train_knn(latent_vectors, cluster_labels, save_path, n_neighbors=5):
    global logger
    from joblib import dump

    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(latent_vectors, cluster_labels)
    logger.info(f"Saving knn under path={save_path}")
    dump(knn, save_path)


def mix_ratio(points, labels):
    import numpy as np
    from scipy.spatial import cKDTree  # Use cKDTree, not KDTree!

    tree = cKDTree(points)
    radius = 1.0
    n_labels = len(np.unique(labels))
    label_counts = np.bincount(labels)

    # Initialize matrices
    co_occurrence = np.zeros((n_labels, n_labels))
    unique_affected = {
        label: set() for label in np.unique(labels)
    }  # Track unique samples

    # Main analysis loop
    for i, (point, label_i) in enumerate(zip(points, labels)):
        neighbors = tree.query_ball_point(point, radius)
        neighbor_labels = labels[neighbors]

        # Update co-occurrence matrix
        unique, counts = np.unique(neighbor_labels, return_counts=True)
        for l, cnt in zip(unique, counts):
            co_occurrence[label_i, l] += cnt

        # Track unique affected samples
        for idx in neighbors:
            unique_affected[labels[idx]].add(idx)

    # Normalize co-occurrence matrix
    co_occurrence_normalized = co_occurrence / label_counts[:, None]

    # Print results
    print("Mix Ratios (Row=Source, Column=Neighbor):\n", co_occurrence_normalized)
    print("\nLabel Statistics:")
    for label in sorted(np.unique(labels)):
        total = label_counts[label]
        affected = len(unique_affected[label])
        print(f"Label {label}:")
        print(f"  - Total samples: {total}")
        print(f"  - Unique samples in radius: {affected} ({affected/total:.1%})")
        print(f"  - Total neighborhood appearances: {co_occurrence[:, label].sum()}\n")


def to_path_str(value):
    return str(value).replace(".", "_")


def downsample_set(embeddings, labels):
    n_samples = int(len(embeddings) * SAMPLE_RATIO)
    np.random.seed(42)
    indices = np.random.choice(len(embeddings), n_samples, replace=False)
    np.random.seed(None)

    logger.info(
        f"HDBSCAN set downsampled with ratio={SAMPLE_RATIO}, samples left count={n_samples}/{len(embeddings)}"
    )
    X_downsampled = embeddings[indices]
    y_downsampled = labels[indices]

    return X_downsampled, y_downsampled


def transform_data(embeddings, transformation, color_label_map):
    if transformation is not None:
        logger.info(
            f"Running transformation on dataset, transformation={transformation}"
        )

    if transformation == "qt":
        from sklearn.preprocessing import QuantileTransformer

        qt = QuantileTransformer(
            output_distribution="normal",
            n_quantiles=1000,
            random_state=42,
        )

        # Fit and transform the data
        embeddings = qt.fit_transform(embeddings)
    return embeddings


def run_pca(embeddings, color_label_map, labels):
    if (
        PRE_PCA_NORMALIZATION is not None
        and POST_PCA_NORMALIZATION is not None
        and PCA_COMPONENTS is None
    ):
        logger.warning(
            f"Running two normalizations without running PCA, PRE_PCA_NORMALIZATION={PRE_PCA_NORMALIZATION}, POST_PCA_NORMALIZATION={POST_PCA_NORMALIZATION}"
        )
    embeddings = normalize_data(
        embeddings=embeddings, normaliation=PRE_PCA_NORMALIZATION
    )
    embeddings = transform_data(
        embeddings=embeddings,
        transformation=TRANSFORMATION,
        color_label_map=color_label_map,
    )

    if PCA_COMPONENTS is not None:
        components_before_pca = len(embeddings[0])
        components = PCA_COMPONENTS
        if components_before_pca < PCA_COMPONENTS:
            logging.getLogger().warning(
                f"PCA - components too high max dim will be taken, dimensons_count={components_before_pca} (before: {PCA_COMPONENTS})"
            )
            components = components_before_pca
        X_pca_plot = PCA(n_components=components)
        embeddings = X_pca_plot.fit_transform(embeddings)
        logging.getLogger().info(
            f"PCA - components left after PCA, count={len(embeddings[0])} (before: {components_before_pca})"
        )

    embeddings = normalize_data(
        embeddings=embeddings, normaliation=POST_PCA_NORMALIZATION
    )

    return embeddings


PRE_PCA_NORMALIZATION = None  # z_score, min_max, robust
TRANSFORMATION = None  # QT
PCA_COMPONENTS = 0.95
POST_PCA_NORMALIZATION = "l2"  # l1, l2, max
METRIC = "chebyshev"  # max: "chebyshev", l2:euclidean, l1:manhattan
MIN_CLUSTER_SIZE = 1000
MIN_SAMPLES = 250
CLUSTER_SELECTION_ELIPSON = 0.0
ALPHA = 1.0
CLUSTER_SELECTION_METHOD = "eom"  # leaf, eom
SAMPLE_RATIO = 0.5
PLOT = True
PLOT_RESULT = True
UMAP_ID = ""
MODEL_NAME = ""
PREDICTION = True
KNN_NEIGHBORS = 10
TRAIN_KNN = True
WITH_UMAP = False


def get_path_prefix():
    prediction = ""
    if PREDICTION == True:
        prediction = "-pred"
    clusterer_name_prefix = f"{MODEL_NAME}{UMAP_ID}{prediction}-{SAMPLE_RATIO}sr-{PRE_PCA_NORMALIZATION}_pre_norm-{to_path_str(PCA_COMPONENTS)}pca-{POST_PCA_NORMALIZATION}_post_norm-{TRANSFORMATION}trans-{METRIC}-{CLUSTER_SELECTION_METHOD}_csm-{to_path_str(ALPHA)}-{MIN_CLUSTER_SIZE}mcs-{MIN_SAMPLES}ms-{to_path_str(CLUSTER_SELECTION_ELIPSON)}cse_hdbscan"
    return PathHelper.join_path(
        Config().get(ModelBuilderUnsupervisedConfig).get_hdbscan_path(),
        clusterer_name_prefix,
    )


def run(
    umap_embeddings,
    umap_metadata,
    model_save_name,
    color_label_map,
    honor_smaple_ration=True,
):
    global MIN_CLUSTER_SIZE, MIN_SAMPLES, CLUSTER_SELECTION_ELIPSON, ALPHA, CLUSTER_SELECTION_METHOD, UMAP_ID, MODEL_NAME, SAMPLE_RATIO, PLOT, PLOT_RESULT, KNN_NEIGHBORS, TRAIN_KNN
    MODEL_NAME = model_save_name

    logger.info(
        "Running HDBSCAN to disable it set 'cluster_parameters.hdbscan.run_hdbscan' to false"
    )
    if WITH_UMAP:
        umap_id = umap_metadata["id"]
        UMAP_ID = f"-{umap_id}_umap_id"
        SAMPLE_RATIO = umap_metadata["sample_ratio"]

    path_prefix = get_path_prefix()
    clusterer_plot_path = path_prefix + "_preds_lot.png"
    knn_path = path_prefix + "_knn.joblib"
    clusterer_path = path_prefix + ".joblib"
    labels = np.array(umap_metadata["labels"])

    # if PathHelper.is_file_exists(clusterer_path):
    #     return
    # else:
    #     print("missing")
    #     return
    components_before_pca = len(embeddings[0])
    if components_before_pca >= 50:
        logging.getLogger().warning(
            f"PCA - embeddings has more than 50 components. It will drastically increase hdbscan training time (different calculation method above 50 dimensions), count={len(embeddings[0])} (before: {components_before_pca})"
        )

    umap_embeddings = run_pca(umap_embeddings, color_label_map, labels)

    if SAMPLE_RATIO < 1 and honor_smaple_ration:
        umap_embeddings, labels = downsample_set(
            embeddings=umap_embeddings, labels=labels
        )
    else:
        logger.info(f"Samples count: {len(umap_embeddings)}")

    if PLOT == True:
        plot_embeddings(
            embeddings=np.array(umap_embeddings),
            components_count=len(umap_embeddings[0]),
            color_label_map=color_label_map,
            labels=labels,
            path=get_path_prefix() + "true.png",
            alpha=0.25,
            remove_noise=False,
            cbar_alpha=0.5,
        )

    clusterer = None
    if PathHelper.is_file_exists(clusterer_path):
        logger.info(
            f"HDBSCAN clusterer already trained, retriving..., path={clusterer_path}"
        )
        clusterer: HDBSCAN = load_hdbscan(clusterer_path)
    else:
        dims = len(umap_embeddings[0])
        jobs = -1
        if dims > 50 and MIN_CLUSTER_SIZE > 1000:
            jobs = 4
        elif MIN_CLUSTER_SIZE > 2500 and dims > 50:
            jobs = 1
        elif MIN_CLUSTER_SIZE > 2500:
            jobs = 3

        logger.info(
            f"HDBSCAN clusterer NOT trained, creating a new one..., path={clusterer_path}"
        )
        clusterer = HDBSCAN(
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES,
            cluster_selection_epsilon=CLUSTER_SELECTION_ELIPSON,
            prediction_data=True,
            cluster_selection_method=CLUSTER_SELECTION_METHOD,
            alpha=ALPHA,
            metric=METRIC,
            # approx_min_span_tree=False,
            # approx_min_span_tree=False,
            core_dist_n_jobs=jobs,
        )
        logger.info(f"HDBSCAN training started")
        clusterer.fit(umap_embeddings)
        logger.info(f"HDBSCAN trained, saving under path, path={clusterer_path}")
        save_hdbscan(clusterer, filepath=clusterer_path)

    if  not sum(labels != -1) == 0:
        logger.info(f"HDBSCAN predicting...")
        print_metrics(partial_labels=labels, labels=np.array(clusterer.labels_))

    if not PathHelper.is_file_exists(knn_path):
        if TRAIN_KNN:
            train_knn(
                latent_vectors=umap_embeddings,
                cluster_labels=clusterer.labels_,
                save_path=knn_path,
                n_neighbors=KNN_NEIGHBORS,
            )
    else:
        logger.info("KNN file exists skipping")
    if PLOT_RESULT == True:
        plot_hdbscan(
            X=umap_embeddings,
            labels=np.array(clusterer.labels_),
            partially_known_labels=labels,
            save_path=clusterer_plot_path,
            alpha=0.1,
        )


def get_combinations_count(datas, umap_embeddings):
    combinations = []
    for data in datas:
        keys = list(data.keys())
        for key_combination in itertools.combinations(keys, len(keys)):
            for items in itertools.product(*[data[key] for key in key_combination]):
                if (
                    len(umap_embeddings[0]) > 50
                    and items[keys.index("pca_components")] is None
                ):
                    logger.info(
                        f"Skipped, embeddings={len(umap_embeddings[0])} and PCA None"
                    )
                    continue
                min_samples = items[keys.index("min_samples")]
                min_cluster_size = items[keys.index("min_cluster_sizes")]
                if min_samples > min_cluster_size:
                    logger.info(
                        f"Skipped, MIN_SAMPLES={min_samples}, MIN_CLUSTER_SIZE={min_cluster_size}"
                    )
                    continue
                if (
                    items[keys.index("pca_components")] is None
                    and items[keys.index("post_pca_normalizations")] is not None
                ):
                    logger.info(f"Skipped pca and post pca are Nones")
                    continue
                combinations.append(key_combination)
    return len(combinations)


def run_dhbscan_options2(
    umap_embeddings, umap_metadata, model_save_name, color_label_map, with_umap=False
):
    global PRE_PCA_NORMALIZATION, PCA_COMPONENTS, POST_PCA_NORMALIZATION, METRIC, MIN_CLUSTER_SIZE, MIN_SAMPLES, CLUSTER_SELECTION_METHOD, SAMPLE_RATIO, PLOT, PLOT_RESULT, KNN_NEIGHBORS, TRAIN_KNN, WITH_UMAP
    config = Config().get(ModelBuilderUnsupervisedConfig).cluster_parameters.hdbscan
    PLOT = config.plot_pca
    PLOT_RESULT = config.plot_result
    KNN_NEIGHBORS = config.knn.n_neighbors
    TRAIN_KNN = config.knn.train_knn
    WITH_UMAP = with_umap
    datas = [
        {
            "pre_pca_normalizations": [config.pre_pca_normalization],
            "pca_components": (
                config.pca_components if config.pca_components != None else [None]
            ),
            "post_pca_normalizations": [config.post_pca_normalization],
            "min_cluster_sizes": config.min_cluster_size,
            "min_samples": config.min_samples,
            "metrics": [config.metric],
            "cluster_selection_method": [config.cluster_selection_method],
            "sample_ratio": [config.sample_ratio],
        }
    ]

    # datas = datas + datas2
    logger.info(f"HDBSCAN data to procees={datas}")
    combinations_count = get_combinations_count(datas, umap_embeddings)
    combination = 1
    sets = []
    for data in datas:
        keys = list(data.keys())
        for key_combination in itertools.combinations(keys, len(keys)):
            for items in itertools.product(*[data[key] for key in key_combination]):
                logger.info(f"{combination}/{combinations_count} combination")
                sets.append(items)
                PRE_PCA_NORMALIZATION = items[keys.index("pre_pca_normalizations")]
                PCA_COMPONENTS = items[keys.index("pca_components")]
                POST_PCA_NORMALIZATION = items[keys.index("post_pca_normalizations")]
                MIN_CLUSTER_SIZE = items[keys.index("min_cluster_sizes")]
                MIN_SAMPLES = items[keys.index("min_samples")]
                METRIC = items[keys.index("metrics")]
                if "sample_ratio" in keys:
                    SAMPLE_RATIO = items[keys.index("sample_ratio")]
                CLUSTER_SELECTION_METHOD = items[keys.index("cluster_selection_method")]

                logger.info(
                    f"SAMPLE_RATIO={SAMPLE_RATIO}, PRE_PCA_NORMALIZATION={PRE_PCA_NORMALIZATION}, PCA_COMPONENTS={PCA_COMPONENTS}, POST_PCA_NORMALIZATION={POST_PCA_NORMALIZATION}, MIN_CLUSTER_SIZE={MIN_CLUSTER_SIZE}, MIN_SAMPLES={MIN_SAMPLES}, METRIC={METRIC}, CLUSTER_SELECTION_METHOD={CLUSTER_SELECTION_METHOD}, TRAIN_KNN={TRAIN_KNN}, KNN_NEIGHBORS={KNN_NEIGHBORS}"
                )
                run(umap_embeddings, umap_metadata, model_save_name, color_label_map)
                combination += 1

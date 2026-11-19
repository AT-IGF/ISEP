from dataclasses import dataclass, field
from .KnnModel import KnnModel


@dataclass
class HdbscanModel:
    """HDBSCAN clustering of the latent space or the UMAP embeddings."""

    PRE_PCA_Z_SCORE = "z_score"
    PRE_PCA_MIN_MAX = "min_max"
    PRE_PCA_ROBUST = "robust"

    POST_PCA_L1 = "l1"
    POST_PCA_L2 = "l2"
    POST_PCA_MAX = "max"

    CLUS_SEL_EOM = "eom"
    CLUS_SEL_LEAF = "leaf"

    METRIC_CHEBYSHEV = "chebyshev"
    METRIC_EUCLIDEAN = "euclidean"
    METRIC_MANHATTAN = "manhattan"

    run_hdbscan: bool = False
    """Run hdbscan."""

    plot_pca: bool = True
    """Plot the input embeddings colored by the known labels, before clustering."""

    plot_result: bool = True
    """Plot hdbscan result."""

    pre_pca_normalization: str | None = None
    """Pre PCA normalization. Data normalization before PCA dimensional reduction:
    ``z_score``, ``min_max``, ``robust`` or ``None``."""

    pca_components: list[float] | list[int] | None = field(
        default_factory=lambda: [0.95]
    )
    """PCA before HDBSCAN. Dataset dimensional reduction. A float is the fraction of explained variance
    to keep, an int is the number of components. ``None`` disables PCA. Every value in the list is
    evaluated as a separate combination."""

    post_pca_normalization: str | None = "max"
    """Post PCA normalization. Normalization after the dimensional reduction: ``l1``, ``l2``, ``max``
    or ``None``."""

    sample_ratio: float = 0.5
    """Sample ratio. Randomly select a part of the dataset. Note: random seed is set, so the same subset
    is always selected for a given ratio."""

    min_cluster_size: list[int] = field(default_factory=lambda: [1000])
    """Min cluster size. Minimum number of samples to create a cluster. Every value in the list is
    evaluated as a separate combination."""

    min_samples: list[int] = field(default_factory=lambda: [250])
    """Min samples. Number of samples in the neighborhood of a point for it to be considered a core
    point. Every value in the list is evaluated as a separate combination."""

    cluster_selection_epsilon: float = 0.0
    """Cluster selection epsilon. Distance threshold below which clusters are merged. ``0.0`` disables merging."""

    cluster_selection_method: str = CLUS_SEL_EOM
    """Cluster selection method. Method used to decide which clusters should stay and which should be
    rejected from the cluster tree. EOM (Excess of Mass) favors more stable densities, Leaf picks the
    tree leaf nodes and prefers higher granulation."""

    alpha: float | None = 1.0
    """Alpha. Distance scaling parameter of the robust single linkage."""

    metric: str = "chebyshev"
    """Metric. Way to measure distances between points: ``chebyshev``, ``euclidean``, ``manhattan`` or
    any other metric supported by HDBSCAN."""

    jobs: int = -1
    knn: KnnModel = field(default_factory=KnnModel)

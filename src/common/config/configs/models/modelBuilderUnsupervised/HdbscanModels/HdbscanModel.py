from dataclasses import dataclass, field
from .KnnModel import KnnModel


@dataclass
class HdbscanModel:
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
    plot_pca: bool = True
    plot_result: bool = True
    pre_pca_normalization: str | None = None  # z_score, min_max, robust
    pca_components: list[float] | list[int] | None = field(
        default_factory=lambda: [0.95]
    )
    post_pca_normalization: str | None = "max"  # l1, l2, max
    sample_ratio: float = 0.5
    min_cluster_size: list[int] = field(default_factory=lambda: [1000])
    min_samples: list[int] = field(default_factory=lambda: [250])
    cluster_selection_epsilon: float = 0.0
    prediction_data: bool = True
    cluster_selection_method: str = CLUS_SEL_EOM  # leaf, eom
    alpha: float | None = 1.0
    metric: str = "chebyshev"  # max: "chebyshev", l2:euclidean, l1:manhattan
    jobs: int = -1
    knn: KnnModel = field(default_factory=KnnModel)
    plot: bool = True

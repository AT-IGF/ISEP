from dataclasses import dataclass, field


@dataclass
class UmapModel:
    """UMAP dimensionality reduction of the latent space, used as a preprocessing step for HDBSCAN."""

    MANHATTAN_METRIC = "manhattan"
    COSINE_METRIC = "cosine"
    CHEBYSHEV_METRIC = "chebyshev"
    EUCLIDEAN_METRIC = "euclidean"

    TARGET_METRIC_CATEGORICAL = "categorical"

    PRE_UMAP_NORMALIZATION_L1 = "l1"
    PRE_UMAP_NORMALIZATION_L2 = "l2"
    PRE_UMAP_NORMALIZATION_Z_SCORE = "z_score"
    PRE_UMAP_NORMALIZATION_MIN_MAX = "min_max"
    PRE_UMAP_NORMALIZATION_ROBUST = "robust"

    run_umap: bool = False
    """Run umap."""

    sample_ratio: float = 0.5
    """Sample ratio. Randomly select a part of the dataset. Note: random seed is set, so the same subset
    is always selected for a given ratio."""

    pre_umap_normalization: str | None = "l2"
    """Pre UMAP normalization. Normalization of the latent space before dimensional reduction: ``l1``,
    ``l2``, ``z_score``, ``min_max``, ``robust`` or ``None``."""

    n_neighbors: list[int] = field(default_factory=lambda: [500])
    """N-neighbors. Number of samples for which UMAP will try to find common structure. Lower values favor
    local structure, whereas higher values focus on a broader picture. Every value in the list is evaluated
    as a separate combination."""

    n_components: list[int] = field(default_factory=lambda: [3])
    """N-components. Number of dimensions to which data will be reduced. 2 or 3 dimensions can also be used
    for visualization purposes. Every value in the list is evaluated as a separate combination."""

    min_distance: list[float] = field(default_factory=lambda: [0.10])
    """Min distance. Controls data density between the points in the lower dimension embedding. Defines how
    close points are allowed to be to each other in the lower dimensions. Every value in the list is
    evaluated as a separate combination."""

    spread: float = 1
    """Spread. Controls data density between the clusters in the lower dimension embedding."""

    target_weight: float = 0
    """Target weight. Weighting factor between data topology and target topology. Controls how much labels
    influence the neighbourhood structure: below 0.5 lower label influence, above 0.5 higher label
    influence. Used only with ``target_enabled``."""

    metric: str = "cosine"
    """Metric. Metric used to build the nearest neighbor graph of the data; depends on data
    characteristics. Any metric supported by UMAP can be used. Should be considered together with the
    pre UMAP normalization."""

    target_metric: str | None = "categorical"
    """Target metric. Metric used for the labels with ``target_enabled``."""

    target_enabled: bool = False
    """Enable target. When partially labeled data is used, labels are passed to UMAP, so the embedding is
    fitted to the labeled data as well. Unlabeled samples are passed as ``-1``. Warning: causes strong
    overfitting and should be set with caution; even with ``target_weight`` set to 0, labels still affect
    the results. Advised: keep this option disabled."""

    output_metric: str = EUCLIDEAN_METRIC
    """Output metric. Decides how UMAP measures distance in the output embedding. UMAP default:
    euclidean."""

    plot: bool = True
    """Plot. Result plotting. If more than 3 components are used, data is reduced with TruncatedSVD."""

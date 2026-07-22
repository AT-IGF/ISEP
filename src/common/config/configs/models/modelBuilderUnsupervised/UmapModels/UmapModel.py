from dataclasses import dataclass, field


@dataclass
class UmapModel:
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
    sample_ratio: float = 0.5
    pre_umap_normalization: str | None = "l2"
    n_neighbors: list[int] = field(default_factory=lambda: [500])
    n_components: list[int] = field(default_factory=lambda: [3])
    min_distance: list[float] = field(default_factory=lambda: [0.10])
    spread: float = 1
    target_weight: float = 0
    metric: str = "cosine"
    target_metric: str | None = "categorical"
    target_enabled: bool = False
    output_metric: str = EUCLIDEAN_METRIC
    plot: bool = True

from dataclasses import dataclass


@dataclass
class KnnModel:
    """KNN classifier trained on the HDBSCAN clusters."""

    train_knn: bool = False
    """Run KNN. Train KNN on the HDBSCAN output. Useful in cases when pure HDBSCAN cannot be used;
    the KNN is then trained on the created clusters and can assign new samples to them."""

    n_neighbors: int = 10
    """N-neighbors. Number of neighbors used by the KNN classifier."""

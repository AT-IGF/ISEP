from dataclasses import dataclass, field


@dataclass
class ClustererModel:
    """Mini-batch K-means clustering of the latent space."""

    run_clusterer: bool = False
    """Run mini batch KMeans."""

    cluster_sizes: list[int] = field(default_factory=lambda: [20, 30, 40])
    """Cluster sizes. Defines how many clusters will be searched, e.g. ``[10]`` outputs 10 clusters.
    Every list element is a separate clustering operation, so ``[10, 20]`` outputs two results for 10 and
    20 clusters."""

    cluster_percentiles: list[float] | None = field(
        default_factory=lambda: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    )
    """Cluster percentiles. For every input directory, clusters are sorted by particle count and the top
    clusters are listed until they cover the given fraction of the directory's particles. Results are saved
    in the ``_PROGRESS.csv`` file of every cluster size."""

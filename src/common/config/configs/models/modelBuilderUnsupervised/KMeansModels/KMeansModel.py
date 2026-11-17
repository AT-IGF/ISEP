from dataclasses import dataclass


@dataclass
class KMeansModel:
    """K-means clustering of the latent space with centroids initialized from labeled samples."""

    CENTROIDS_BY_CLASS = "class_centroids"
    """Centroids by class."""

    CENTROIDS_BY_KNOWN_AND_UNKOWN = "known_unknown_centroids"
    """Centroids by known and unknown samples."""

    run_kmeans: bool = False
    """Run KMeans. Requires labeled samples (``with_labeled_samples``); otherwise K-means is skipped."""

    centroids_mode: str = CENTROIDS_BY_CLASS
    """Centroids mode. What centroids to calculate from the data. Centroids by class calculates the center
    of each labeled class, so the number of clusters equals the number of labeled classes. Centroids by
    known and unknown samples creates two centroids and treats the data as two classes."""

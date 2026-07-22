from dataclasses import dataclass


@dataclass
class KMeansModel:
    CENTROIDS_BY_CLASS = "class_centroids"
    CENTROIDS_BY_KNOWN_AND_UNKOWN = "known_unknown_centroids"

    run_kmeans: bool = False
    centroids_mode: str = CENTROIDS_BY_CLASS

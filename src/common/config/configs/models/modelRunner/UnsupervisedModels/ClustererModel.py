from dataclasses import dataclass, field

from src.common.config.configs.models.modelRunner.UnsupervisedModels.UnsupervisedBaseModel import (
    UnsupervisedBaseModel,
)


@dataclass
class ClustererModel:
    HDBSCAN_CLUSTERER = "hdbscan"
    KNN_CLUSTERER = "knn"
    MINI_BATCH_KMEANS_CLUSTERER = "mini_batch_kmeans"
    KMEANS_CLUSTERER = "kmeans"

    clusterer_to_use: str | None = None
    hdbscan: UnsupervisedBaseModel = field(
        default_factory=lambda: UnsupervisedBaseModel(
            path=None,
            mapping_path=None,
            key=ClustererModel.HDBSCAN_CLUSTERER,
        )
    )

    knn: UnsupervisedBaseModel = field(
        default_factory=lambda: UnsupervisedBaseModel(
            path=None,
            mapping_path=None,
            key=ClustererModel.KNN_CLUSTERER,
        )
    )
    mini_batch_kmeans: UnsupervisedBaseModel = field(
        default_factory=lambda: UnsupervisedBaseModel(
            path=None, mapping_path=None, key=ClustererModel.MINI_BATCH_KMEANS_CLUSTERER
        )
    )

    kmeans: UnsupervisedBaseModel = field(
        default_factory=lambda: UnsupervisedBaseModel(
            path=None,
            mapping_path=None,
            key=ClustererModel.KMEANS_CLUSTERER,
        )
    )

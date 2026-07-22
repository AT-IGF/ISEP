from dataclasses import dataclass, field

from src.common.config.configs.models.modelBuilderUnsupervised.HdbscanModels.HdbscanModel import (
    HdbscanModel,
)

from src.common.config.configs.models.modelBuilderUnsupervised.UmapModels.UmapModel import (
    UmapModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised.ClustererModels.ClustererModel import (
    ClustererModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised.KMeansModels.KMeansModel import (
    KMeansModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised.AnomalyDetectorModels.AnomalyDetectorModel import (
    AnomalyDetectorModel,
)


@dataclass
class ClusterParameterModel:
    run_clustering: bool = False
    hdbscan: HdbscanModel = field(default_factory=HdbscanModel)
    umap: UmapModel = field(default_factory=UmapModel)
    clusterer: ClustererModel = field(default_factory=ClustererModel)
    kmeans: KMeansModel = field(default_factory=KMeansModel)
    anomaly_detector: AnomalyDetectorModel = field(default_factory=AnomalyDetectorModel)

    def run_hdbscan(self):
        return self.run_clustering and self.hdbscan.run_hdbscan

    def run_umap(self):
        return self.run_clustering and self.umap.run_umap

    def run_clusterer(self):
        return self.run_clustering and self.clusterer.run_clusterer

    def run_kmeans(self):
        return self.run_clustering and self.kmeans.run_kmeans

    def run_anomaly_detector(self):
        return self.run_clustering and self.anomaly_detector.run_anomaly_detector

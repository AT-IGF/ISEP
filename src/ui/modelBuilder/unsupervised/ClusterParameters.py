from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout


from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import scaler as scaler
from src.ui.common import BannerWidget
from src.core import PathHelper

from src.ui.common import DirectorySelectorWidget
from src.ui.modelBuilder.unsupervised.HdbscanWidget import HdbscanWidget
from src.ui.modelBuilder.unsupervised.UmapWidget import UmapWidget
from src.ui.modelBuilder.unsupervised.MiniBatchKMeansWidget import MiniBatchKMeansWidget
from src.ui.modelBuilder.unsupervised.KMeansWidget import KMeansWidget


class ClusterParameters(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )

        self.umap_widget = UmapWidget(singals)
        self.hdbscan_widget = HdbscanWidget(singals)
        self.clusterer_widget = MiniBatchKMeansWidget(singals)
        self.kmeans_widget = KMeansWidget(singals)

        self._value = self.config.cluster_parameters
        self._value_original = self.config.cluster_parameters

        self.run_clustering_widget = MeasurementWidget(
            self.config.cluster_parameters.run_clustering,
            label="Run clustering",
            tooltip="",
            value_changed=singals.value_changed,
            children=[
                self.umap_widget,
                self.hdbscan_widget,
                self.clusterer_widget,
                self.kmeans_widget,
            ],
            layout="Vertical",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.run_clustering_widget)
        layoutV.addStretch()
        layoutV.setSpacing(0)

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    @property
    def value(self):
        if self.run_clustering_widget.value == True:
            self._value.run_clustering = True
            self._value.umap = self.umap_widget.value
            self._value.hdbscan = self.hdbscan_widget.value
            self._value.clusterer = self.clusterer_widget.value
            self._value.kmeans = self.kmeans_widget.value
        else:
            self._value = self._value_original
            self._value.run_clustering = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

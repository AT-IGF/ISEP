from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from src.common import Consts
from src.common.config.configs.models.modelBuilderUnsupervised.HdbscanModels.HdbscanModel import (
    HdbscanModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised.ClusterParameterModel import (
    ClusterParameterModel,
)
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.ui.common import MeasurementWidget, LabelValueWidget
from src.ui.dataViewer import SettingsSignals
from src.ui.dataViewer import aggregatedSamples as aggregated


class MiniBatchKMeansWidget(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.base_config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        self.config = self.base_config.cluster_parameters.clusterer
        self.value_changed = singals.value_changed
        self._value = self.config
        self._value_original = self.config

        self.cluster_sizes_widget = LabelValueWidget(
            "Cluster sizes",
            self.config.cluster_sizes,
            singals,
            val_type=list[int],
            suffix_label=None,
            tooltip="Define how many clusters will be searched, e.g. [10] will output 10 clusters. Every list element is a separate clustering operation [10, 20] will output two results for 10 and 20 clusters.",
            width=200,
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.cluster_percentiles_widget = LabelValueWidget(
            "Cluster percentiles",
            self.config.cluster_percentiles,
            singals,
            val_type=list[float],
            suffix_label=None,
            tooltip="Outputs top clusters within given threshold per every class. For example: a class is defined by clusters 1, 3 and 5; clusters are sorted by count and if fits the percentage cluster is printed.",
            width=200,
            bottom=0,
            top=1,
        )
        self.run_clusterer_widget = MeasurementWidget(
            self.config.run_clusterer,
            label="Run mini batch KMeans",
            tooltip="",
            value_changed=singals.value_changed,
            children=[
                self.cluster_sizes_widget,
                self.cluster_percentiles_widget,
            ],
            layout="Vertical",
            margins=(0, 0, 0, 0),
            margins_children=(10, 0, 0, 0),
        )

        layoutV = QVBoxLayout()
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom

        layoutV.addWidget(self.run_clusterer_widget)

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    @property
    def value(self):
        if self.run_clusterer_widget.value == True:
            self._value.run_clusterer = True
            self._value.cluster_sizes = self.cluster_sizes_widget.value
            self._value.cluster_percentiles = self.cluster_percentiles_widget.value
        else:
            self._value = self._value_original
            self._value.run_clusterer = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

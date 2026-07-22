from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.common.config.configs.models.modelBuilderUnsupervised.KMeansModels.KMeansModel import (
    KMeansModel,
)
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.ui.common import MeasurementWidget
from src.ui.dataViewer import SettingsSignals
from src.ui.dataViewer import aggregatedSamples as aggregated


class KMeansWidget(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.base_config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        self.config = self.base_config.cluster_parameters.kmeans
        self._value = self.config
        self._value_original = self.config
        self.value_changed = singals.value_changed

        sub_apps = [
            aggregated.Radio(
                KMeansModel.CENTROIDS_BY_CLASS,
                self.config.centroids_mode,
                label="Centroids by class",
            ),
            aggregated.Radio(
                KMeansModel.CENTROIDS_BY_KNOWN_AND_UNKOWN,
                self.config.centroids_mode,
                label="Centroids by known and unknown samples",
            ),
        ]
        self.centroids_mode_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Centroids mode:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="What centroids to calculate from the data. Centroids by class calculate the center of each class, centroids bt known and unknown samples creates two centroids and treats data as two classes.",
        )

        self.run_kmeans_widget = MeasurementWidget(
            self.config.run_kmeans,
            label="Run KMeans",
            tooltip="",
            value_changed=singals.value_changed,
            children=[self.centroids_mode_widget],
            layout="Vertical",
            margins=(0, 0, 0, 0),
            margins_children=(10, 0, 0, 0),
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.run_kmeans_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    @property
    def value(self):
        if self.run_kmeans_widget.value == True:
            self._value.run_kmeans = True
            self._value.centroids_mode = self.centroids_mode_widget.selected_app.value
        else:
            self._value = self._value_original
            self._value.run_kmeans = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

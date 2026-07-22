from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout


from src.common.config.configs.models.modelRunner.UnsupervisedModels import (
    UnsupervisedBaseModel,
    ClustererModel,
    DimReducerModel,
)
from src.common.config.configs.models.modelRunner import UnsupervisedModel
from src.common.config.configs import ModelRunnerConfig
from src.common.config import Config

from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import scaler as scaler

from src.ui.common import DirectorySelectorWidget
from src.ui.dataViewer.aggregatedSamples.AggregatorWidget import (
    Radio,
    RadioSelectorWidget,
)
from src.ui.common import PcaComponentsWidget


class DimensionReducerWidget(QWidget):
    def __init__(self, config: DimReducerModel, singals: SettingsSignals):
        super().__init__()
        self._value = config
        self._value_original = config
        joblib_files_selector = "Joblib files (*.joblib)"
        self.umap_path_widget = DirectorySelectorWidget(
            "UMAP path:",
            self._value.umap.path,
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            selector="FILE",
            extensions=joblib_files_selector,
            tooltip="Pre-clustering step to reduce the dimensions of autoencoder latent space",
            margins=(10, 5, 0, 0),
        )
        self.pca_option_widget = PcaComponentsWidget(
            pca_components=self._value.pca.components,
            singals=singals,
            margins=(10, 5, 0, 0),
            is_list=False,
        )
        dim_recuder_apps = [
            Radio(
                None,
                self._value.dim_reducer_to_use,
                widget=None,
                label="None",
            ),
            Radio(
                value=self._value.PCA_REDUCTOR,
                selected_value=self._value.dim_reducer_to_use,
                widget=self.pca_option_widget,
                label="PCA",
            ),
            Radio(
                value=self._value.UMAP_REDUCTOR,
                selected_value=self._value.dim_reducer_to_use,
                widget=self.umap_path_widget,
                label="UMAP",
            ),
        ]

        self.dimensional_reducer_widget = RadioSelectorWidget(
            self,
            dim_recuder_apps,
            singals.value_changed,
            label="Dimensonal reducer:",
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
            tooltip="Dimension reduction method.",
        )
        layoutV = QVBoxLayout()
        layoutV.addWidget(self.dimensional_reducer_widget)
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        selected_val = self.dimensional_reducer_widget.selected_app.value
        self._value.dim_reducer_to_use = selected_val
        if selected_val == self._value.UMAP_REDUCTOR:
            self._value.umap.path = self.umap_path_widget.value
        if selected_val == self._value.PCA_REDUCTOR:
            self._value.pca.components = self.pca_option_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class ClustererOptionsWidget(QWidget):
    def __init__(
        self, config: UnsupervisedBaseModel, singals: SettingsSignals, file_extension
    ):
        super().__init__()
        self._value = config
        self._value_original = config
        layoutV = QVBoxLayout()
        self.path_widget = DirectorySelectorWidget(
            "Clusterer path",
            config.path,
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            selector="FILE",
            extensions=file_extension,
            tooltip="Map to the output cluster file from the Model builder -> unsupervised section",
            margins=(10, 5, 0, 0),
        )
        self.cluster_mapping_widget = DirectorySelectorWidget(
            "Clusters mapping path",
            config.mapping_path,
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            selector="FILE",
            extensions=DirectorySelectorWidget.JSON_FILE_EXTENSION,
            tooltip='Mapping file in json format containg informaton which pollen type belongs to which cluster.\
                <br/><b>NOTE</b>: One cluster can belong to more than one cluster, pollen types can be in both index and string value\
                <br/><b>Example input</b>: { "Alnus": [1, 2, 4], "Corlus": 3 }',
            margins=(10, 5, 0, 0),
        )

        layoutV.addWidget(self.path_widget)
        layoutV.addWidget(self.cluster_mapping_widget)
        layoutV.setContentsMargins(10, 5, 0, 0)  # left, top, right, bottom
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        self._value.run = self.isVisible()
        self._value.path = self.path_widget.value
        self._value.mapping_path = self.cluster_mapping_widget.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class ClustererWidget(QWidget):
    def __init__(self, config: ClustererModel, singals: SettingsSignals):
        super().__init__()
        self._value = config
        self._value_original = config
        self.hdbscan_options_widget = ClustererOptionsWidget(
            config=config.hdbscan,
            singals=singals,
            file_extension=DirectorySelectorWidget.JOBLIB_FILE_EXTENSION,
        )
        self.knn_options_widget = ClustererOptionsWidget(
            config=config.knn,
            singals=singals,
            file_extension=DirectorySelectorWidget.JOBLIB_FILE_EXTENSION,
        )
        self.mini_batch_kmeans_options_widget = ClustererOptionsWidget(
            config=config.mini_batch_kmeans,
            singals=singals,
            file_extension=DirectorySelectorWidget.PICKLE_EXTENSION,
        )
        self.kmeans_options_widget = ClustererOptionsWidget(
            config=config.kmeans,
            singals=singals,
            file_extension=DirectorySelectorWidget.JOBLIB_FILE_EXTENSION,
        )

        clusterer_apps = [
            Radio(None, config.clusterer_to_use, None, "None"),
            Radio(
                config.hdbscan.key,
                config.clusterer_to_use,
                self.hdbscan_options_widget,
                "HDBSCAN",
            ),
            Radio(
                config.knn.key, config.clusterer_to_use, self.knn_options_widget, "KNN"
            ),
            Radio(
                config.mini_batch_kmeans.key,
                config.clusterer_to_use,
                self.mini_batch_kmeans_options_widget,
                "Mini batch KMeans",
            ),
            Radio(
                config.kmeans.key,
                config.clusterer_to_use,
                self.kmeans_options_widget,
                "KMeans",
            ),
        ]

        self.clusterer_widget = RadioSelectorWidget(
            self,
            clusterer_apps,
            singals.value_changed,
            label="Clusterer:",
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
            tooltip="A way to cluster the input data",
        )
        layoutV = QVBoxLayout()
        layoutV.addWidget(self.clusterer_widget)
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        selected_val = self.clusterer_widget.selected_app.value
        self._value.clusterer_to_use = selected_val
        if selected_val == self._value.HDBSCAN_CLUSTERER:
            self._value.hdbscan = self.hdbscan_options_widget.value
        if selected_val == self._value.KNN_CLUSTERER:
            self._value.knn = self.knn_options_widget.value
        if selected_val == self._value.MINI_BATCH_KMEANS_CLUSTERER:
            self._value.mini_batch_kmeans = self.mini_batch_kmeans_options_widget.value
        if selected_val == self._value.KMEANS_CLUSTERER:
            self._value.kmeans = self.kmeans_options_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class UnsupervisedWidget(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.config_base: ModelRunnerConfig = Config.get(ModelRunnerConfig)
        self._value = self.config_base.unsupervised
        self._value_original = self.config_base.unsupervised

        self.autoencoder_path_widget = DirectorySelectorWidget(
            "Autoencoder path",
            self._value.autoencoder_path,
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            selector="FILE",
            extensions=DirectorySelectorWidget.H5_EXTENSION,
            tooltip="Path to the trained unsupervised model from the Model builder -> unsupervised tab",
            margins=(10, 10, 0, 0),
        )

        self.dimension_reducer_widget = DimensionReducerWidget(
            config=self._value.dim_reducer, singals=singals
        )
        self.clusterer_widget = ClustererWidget(
            config=self._value.clusterer, singals=singals
        )

        self.run_unsupervised_widget = MeasurementWidget(
            self._value.run_unsupervised,
            label="Cluster filtering",
            tooltip="Optional. Use output models from the Model builder -> Unsupervised section, used for samples removal when do not fit to the specified cluster",
            value_changed=singals.value_changed,
            children=[
                self.autoencoder_path_widget,
                self.dimension_reducer_widget,
                self.clusterer_widget,
            ],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.run_unsupervised_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(10, 0, 0, 0)  # left, top, right, bottom
        layoutV.setSpacing(0)

        self.setLayout(layoutV)

    @property
    def value(self):
        if self.run_unsupervised_widget.value == True:
            self._value.run_unsupervised = True
            self._value.autoencoder_path = self.autoencoder_path_widget.value
            self._value.dim_reducer = self.dimension_reducer_widget.value
            self._value.clusterer = self.clusterer_widget.value
        else:
            self._value = self._value_original
            self._value.run_unsupervised = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

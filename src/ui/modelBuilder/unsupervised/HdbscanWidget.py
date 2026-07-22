from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from src.common.config.configs.models.modelBuilderUnsupervised.HdbscanModels.KnnModel import (
    KnnModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised.HdbscanModels.HdbscanModel import (
    HdbscanModel,
)
from src.common import Consts

from src.common.config.configs.models.modelBuilderUnsupervised.ClusterParameterModel import (
    ClusterParameterModel,
)
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.ui.common import MeasurementWidget, LabelValueWidget
from src.ui.dataViewer import SettingsSignals
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common import SectionWidget
from src.ui.common import PcaComponentsWidget


class PrePcaNormalizationWidget(QWidget):
    def __init__(self, config: HdbscanModel, value_changed):
        super().__init__()
        pre_pca_normalization = config.pre_pca_normalization
        self._value = pre_pca_normalization

        sub_apps = [
            aggregated.Radio(None, pre_pca_normalization, label="None"),
            aggregated.Radio(
                HdbscanModel.PRE_PCA_Z_SCORE,
                pre_pca_normalization,
                label="Z-score",
            ),
            aggregated.Radio(
                HdbscanModel.PRE_PCA_MIN_MAX,
                pre_pca_normalization,
                label="Min-max",
            ),
            aggregated.Radio(
                HdbscanModel.PRE_PCA_ROBUST,
                pre_pca_normalization,
                label="Robust",
            ),
        ]
        self.pre_pca_normalization_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=value_changed,
            label="Pre PCA normalization:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Data normalization before PCA dimensional reduction.",
        )

        layoutV = QHBoxLayout()
        layoutV.addWidget(self.pre_pca_normalization_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(0, 10, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        return self.pre_pca_normalization_widget.selected_app.value

    @value.setter
    def value(self, value):
        self._value = value


class PostPcaNormalizationWidget(QWidget):
    def __init__(self, config: HdbscanModel, value_changed):
        super().__init__()
        post_pca_normalization = config.post_pca_normalization
        self._value = post_pca_normalization

        sub_apps = [
            aggregated.Radio(None, post_pca_normalization, label="None"),
            aggregated.Radio(
                HdbscanModel.POST_PCA_L1,
                post_pca_normalization,
                label="l1",
            ),
            aggregated.Radio(
                HdbscanModel.POST_PCA_L2,
                post_pca_normalization,
                label="l2",
            ),
            aggregated.Radio(
                HdbscanModel.POST_PCA_MAX,
                post_pca_normalization,
                label="max",
            ),
        ]
        self.post_pca_normalization_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=value_changed,
            label="Post PCA normalization:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Normalization after the dimensional reduction",
        )

        layoutV = QHBoxLayout()
        layoutV.addWidget(self.post_pca_normalization_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(0, 10, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        return self.post_pca_normalization_widget.selected_app.value

    @value.setter
    def value(self, value):
        self._value = value


class ClusteringSelectionMethodWidget(QWidget):
    def __init__(self, config: HdbscanModel, value_changed):
        super().__init__()
        cluster_selection_method = config.cluster_selection_method
        self._value = cluster_selection_method

        sub_apps = [
            aggregated.Radio(
                HdbscanModel.CLUS_SEL_EOM,
                cluster_selection_method,
                label="EOM",
            ),
            aggregated.Radio(
                HdbscanModel.CLUS_SEL_LEAF,
                cluster_selection_method,
                label="Leaf",
            ),
        ]
        self.post_pca_normalization_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=value_changed,
            label="Cluster selection method:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Method used to decide which clusters should stay and which should be rejected from the cluster tree. EOM (Excess of Mass) - favors more stable densities, Leaf - picks three leaf nodes, and prefers higher granulation",
        )

        layoutV = QHBoxLayout()
        layoutV.addWidget(self.post_pca_normalization_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(0, 10, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        return self.post_pca_normalization_widget.selected_app.value

    @value.setter
    def value(self, value):
        self._value = value


class MetricWidget(QWidget):
    METRICS = [
        HdbscanModel.METRIC_CHEBYSHEV,
        HdbscanModel.METRIC_EUCLIDEAN,
        HdbscanModel.METRIC_MANHATTAN,
        None,
    ]

    def __init__(self, config: HdbscanModel, singals):
        super().__init__()
        metric = config.metric
        self._value = metric

        sub_apps = [
            aggregated.Radio(
                HdbscanModel.METRIC_CHEBYSHEV,
                metric,
                label="Chebyshev",
            ),
            aggregated.Radio(
                HdbscanModel.METRIC_EUCLIDEAN,
                metric,
                label="Euclidean",
            ),
            aggregated.Radio(
                HdbscanModel.METRIC_MANHATTAN,
                metric,
                label="Manhattan",
            ),
            aggregated.OtherRadio(
                values=self.METRICS, selected_value=metric, signals=singals
            ),
        ]
        self.metric_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Metric:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Way to measure distances between points. When other option selected accepts all metrics from the documentation.",
        )

        layoutV = QHBoxLayout()
        layoutV.addWidget(self.metric_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(0, 10, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        return self.metric_widget.selected_app.value

    @value.setter
    def value(self, value):
        self._value = value


class HdbscanWidget(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.base_config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        self.config = self.base_config.cluster_parameters.hdbscan
        self.value_changed = singals.value_changed
        self._value = self.config
        self._value_original = self.config
        self.pre_pca_section_widget = SectionWidget(
            "PCA - before HDBSCAN",
            margins=(5, 0, 0, 0),
            tooltip="Dataset dimensional reduction.",
        )

        self.pre_pca_normalization_widget = PrePcaNormalizationWidget(
            config=self.config, value_changed=singals.value_changed
        )
        self.pca_components_widget = PcaComponentsWidget(
            pca_components=self.config.pca_components, singals=singals
        )
        self.post_pca_normalization_widget = PostPcaNormalizationWidget(
            config=self.config, value_changed=singals.value_changed
        )

        self.hdbscan_section_widget = SectionWidget(
            "HDBSCAN clustering configuration",
            margins=(5, 10, 0, 0),
            tooltip="Dataset dimensional reduction.",
        )

        self.sample_ratio_widget = LabelValueWidget(
            "Sample ratio",
            int(self.config.sample_ratio * 100),
            singals,
            val_type=int,
            suffix_label="%",
            tooltip="Randomly select a part of the dataset. <br/><b>NOTE</b>: random seed is set, the random function will always return the same randomly selected set for given ratio.",
            width=50,
            bottom=0,
            top=100,
        )

        self.min_cluster_size_widget = LabelValueWidget(
            "Min cluster size",
            self.config.min_cluster_size,
            singals,
            val_type=list[int],
            suffix_label=None,
            tooltip="Minium number of samples to create cluster",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.min_samples_widget = LabelValueWidget(
            "Min samples",
            self.config.min_samples,
            singals,
            val_type=list[int],
            suffix_label=None,
            tooltip="Number of samples in the neighborhood of the sample to be considered as a cluster.",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.cluster_selection_epsilon_widget = LabelValueWidget(
            "Cluster selection elipson",
            int(self.config.cluster_selection_epsilon),
            singals,
            val_type=int,
            suffix_label=None,
            tooltip=None,
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.cluster_selection_epsilon_widget = LabelValueWidget(
            "Cluster selection elipson",
            int(self.config.cluster_selection_epsilon),
            singals,
            val_type=int,
            suffix_label=None,
            tooltip=None,
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.prediction_data_widget = MeasurementWidget(
            self.config.prediction_data,
            label="Save prediction data",
            tooltip="Saves information about cluster to use it to for KNN prediction for new samples witout reclustering",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        self.cluster_selection_method_widget = ClusteringSelectionMethodWidget(
            config=self.config, value_changed=singals.value_changed
        )

        self.alpha_widget = LabelValueWidget(
            "Alpha",
            int(self.config.alpha),
            singals,
            val_type=float,
            suffix_label=None,
            tooltip="Determines how conservative the clustering is, changes shapes of clusters. Changing this parameter should be done in the later steps, documentation says: “in practice it is best not to mess with this parameter.”. Default value = 1.",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.metric_widget = MetricWidget(config=self.config, singals=singals)

        self.jobs_widget = LabelValueWidget(
            "Jobs",
            int(self.config.jobs),
            singals,
            val_type=int,
            suffix_label=None,
            tooltip="Number of jobs to process clustering process. -1 - unlimited. Warning to high values are highly memory consuming.",
            width=100,
            bottom=-1,
            top=Consts.INT_MAX,
        )

        self.n_neighbors_widget = LabelValueWidget(
            "N-neighbors:",
            int(self.config.knn.n_neighbors),
            singals,
            val_type=int,
            suffix_label=None,
            tooltip=None,
            width=100,
            bottom=-1,
            top=Consts.INT_MAX,
            margins=(0, 0, 0, 0),
        )

        self.post_hdbscan_section_widget = SectionWidget(
            "Post HDBSCAN options",
            margins=(5, 10, 0, 0),
        )

        self.knn_widget = MeasurementWidget(
            self.config.knn.train_knn,
            label="Run KNN",
            tooltip="Train KNN on the points output. Useful in the cases when pure HDBSCAN cannot be used then the KNN is trained on the created clusters.",
            value_changed=singals.value_changed,
            children=[self.n_neighbors_widget],
            layout="Horizontal",
            margins=(0, 10, 0, 0),
        )

        self.plot_pca_widget = MeasurementWidget(
            self.config.plot_pca,
            label="Plot data before hdbscan",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        self.plot_result_widget = MeasurementWidget(
            self.config.plot_result,
            label="Plot hdbscan result",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        self.run_hdbscan_widget = MeasurementWidget(
            self.config.run_hdbscan,
            label="Run hdbscan",
            tooltip="",
            value_changed=singals.value_changed,
            children=[
                self.pre_pca_section_widget,
                self.pre_pca_normalization_widget,
                self.pca_components_widget,
                self.post_pca_normalization_widget,
                self.plot_pca_widget,
                self.hdbscan_section_widget,
                self.sample_ratio_widget,
                self.min_cluster_size_widget,
                self.min_samples_widget,
                self.prediction_data_widget,
                self.cluster_selection_method_widget,
                self.alpha_widget,
                self.metric_widget,
                self.jobs_widget,
                self.post_hdbscan_section_widget,
                self.knn_widget,
                self.plot_result_widget,
            ],
            layout="Vertical",
            margins=(0, 0, 0, 0),
            margins_children=(10, 0, 0, 0),
        )

        layoutV = QVBoxLayout()
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom
        layoutV.setSpacing(0)
        layoutV.addWidget(self.run_hdbscan_widget)
        layoutV.addStretch()

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    @property
    def value(self):
        if self.run_hdbscan_widget.value == True:
            self._value.run_hdbscan = True
            self._value.pre_pca_normalization = self.pre_pca_normalization_widget.value
            self._value.pca_components = self.pca_components_widget.value
            self._value.post_pca_normalization = (
                self.post_pca_normalization_widget.value
            )
            self._value.sample_ratio = self.sample_ratio_widget.value / 100
            self._value.min_cluster_size = self.min_cluster_size_widget.value
            self._value.min_samples = self.min_samples_widget.value
            self._value.cluster_selection_epsilon = (
                self.cluster_selection_epsilon_widget.value
            )
            self._value.prediction_data = self.prediction_data_widget.value
            self._value.cluster_selection_method = (
                self.cluster_selection_method_widget.value
            )
            self._value.alpha = self.alpha_widget.value
            self._value.metric = self.metric_widget.value
            self._value.jobs = self.jobs_widget.value
            self._value.knn = KnnModel(
                train_knn=self.knn_widget.value,
                n_neighbors=self.n_neighbors_widget.value,
            )
            self._value.plot_pca = self.plot_pca_widget.value
            self._value.plot_result = self.plot_result_widget.value
        else:
            self._value = self._value_original
            self._value.run_hdbscan = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

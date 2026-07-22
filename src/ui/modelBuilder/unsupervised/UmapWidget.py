from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from src.common import Consts
from src.common.config.configs.models.modelBuilderUnsupervised.UmapModels.UmapModel import (
    UmapModel,
)
from src.common.config.configs.models.modelBuilderUnsupervised.ClusterParameterModel import (
    ClusterParameterModel,
)
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig
from src.ui.common import MeasurementWidget, LabelValueWidget
from src.ui.dataViewer import SettingsSignals
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common import SectionWidget


def get_other_value(value, values):
    if value == None or value in values:
        return ""
    return value


class PreUmapNormalizationWidget(QWidget):
    def __init__(self, config: UmapModel, singals):
        super().__init__()
        pre_umap_normalization = config.pre_umap_normalization
        self._value = pre_umap_normalization
        sub_apps = [
            aggregated.Radio(None, pre_umap_normalization, label="None"),
            aggregated.Radio(
                UmapModel.PRE_UMAP_NORMALIZATION_L1,
                pre_umap_normalization,
                label="l1",
            ),
            aggregated.Radio(
                UmapModel.PRE_UMAP_NORMALIZATION_L2,
                pre_umap_normalization,
                label="l2",
            ),
            aggregated.Radio(
                UmapModel.PRE_UMAP_NORMALIZATION_Z_SCORE,
                pre_umap_normalization,
                label="Z-score",
            ),
            aggregated.Radio(
                UmapModel.PRE_UMAP_NORMALIZATION_MIN_MAX,
                pre_umap_normalization,
                label="Min-max",
            ),
            aggregated.Radio(
                UmapModel.PRE_UMAP_NORMALIZATION_ROBUST,
                pre_umap_normalization,
                label="Robust",
            ),
        ]
        self.post_pca_normalization_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Pre UMAP normalization:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Not dimensionally reduced latent space normalization.",
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
    UMAP_METRICS = [
        None,
        UmapModel.COSINE_METRIC,
        UmapModel.MANHATTAN_METRIC,
        UmapModel.CHEBYSHEV_METRIC,
        UmapModel.EUCLIDEAN_METRIC,
    ]

    def __init__(self, config: UmapModel, singals):
        super().__init__()
        metric = config.metric
        self._value = metric

        sub_apps = [
            aggregated.Radio(
                UmapModel.COSINE_METRIC,
                metric,
                label="cosine",
            ),
            aggregated.Radio(
                UmapModel.MANHATTAN_METRIC,
                metric,
                label="manhattan",
            ),
            aggregated.Radio(
                UmapModel.CHEBYSHEV_METRIC,
                metric,
                label="chebyshev",
            ),
            aggregated.Radio(
                UmapModel.EUCLIDEAN_METRIC,
                metric,
                label="euclidean",
            ),
            aggregated.OtherRadio(
                values=self.UMAP_METRICS, selected_value=metric, signals=singals
            ),
        ]
        self.post_pca_normalization_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Metric:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Metric that will be used to fit the data during KNN, depends on data characteristics (in signals cases Minkowski metrics are advised). Other option takes every metric that is supported by the UMAP.\
                <br/>Should be considered together with Pre UMAP normalization when set, recommended mappings:\
                <ul>\
                    <li>l1 - manhattan</li>\
                    <li>l2 - cosine/euclidean</li>\
                    <li>max - chebyshev/euclidean</li>\
                    <li>robust - euclidean/manhattan/cosine</li>\
                    <li>min-max - euclidean/manhattan</li>\
                    <li>z-score - euclidean/cosine</li>\
                </ul>\
                <br/><br/>\
                <b>NOTE</b>: euclidean metric needs to load whole data into memory, out of memory error possible when used.<br/>Umap default: euclidean; advised: cosine \
                    ",
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


class TargetMetricWidget(QWidget):
    TARGET_METRICS = [None, UmapModel.TARGET_METRIC_CATEGORICAL]

    def __init__(self, config: UmapModel, singals):
        super().__init__()
        metric = config.target_metric
        self._value = metric

        sub_apps = [
            aggregated.Radio(None, metric, label="None"),
            aggregated.Radio(
                UmapModel.TARGET_METRIC_CATEGORICAL,
                metric,
                label="Categorical",
            ),
            aggregated.OtherRadio(
                values=self.TARGET_METRICS, selected_value=metric, signals=singals
            ),
        ]
        self.target_metric_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Target metric:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
        )

        layoutV = QHBoxLayout()
        layoutV.addWidget(self.target_metric_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        return self.target_metric_widget.selected_app.value

    @value.setter
    def value(self, value):
        self._value = value

    def update(self, value):
        self.target_metric_widget.update(value)


class OutputMetricWidget(QWidget):
    OUTPUT_METRICS = [
        UmapModel.COSINE_METRIC,
        UmapModel.MANHATTAN_METRIC,
        UmapModel.CHEBYSHEV_METRIC,
        UmapModel.EUCLIDEAN_METRIC,
        None,
    ]

    def __init__(self, config: UmapModel, singals):
        super().__init__()
        metric = config.output_metric
        self._value = metric

        sub_apps = [
            aggregated.Radio(
                UmapModel.EUCLIDEAN_METRIC,
                metric,
                label="euclidean",
            ),
            aggregated.Radio(
                UmapModel.COSINE_METRIC,
                metric,
                label="cosine",
            ),
            aggregated.Radio(
                UmapModel.MANHATTAN_METRIC,
                metric,
                label="manhattan",
            ),
            aggregated.Radio(
                UmapModel.CHEBYSHEV_METRIC,
                metric,
                label="chebyshev",
            ),
            aggregated.OtherRadio(
                values=self.OUTPUT_METRICS, selected_value=metric, signals=singals
            ),
        ]
        self.post_pca_normalization_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Output metric:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Decides how UMAP measures distance in output plot.<br/>Umap default: euclidean",
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


class UmapWidget(QWidget):
    def __init__(self, singals: SettingsSignals):
        super().__init__()
        self.base_config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        self.config = self.base_config.cluster_parameters.umap
        self._value = self.config
        self._value_original = self.config
        self.value_changed = singals.value_changed

        self.pre_umap_section_widget = SectionWidget(
            "Before umap training", margins=(5, 0, 0, 0)
        )

        self.sample_ratio_widget = LabelValueWidget(
            "Sample ratio",
            int(self.config.sample_ratio * 100),
            singals,
            val_type=int,
            suffix_label="%",
            tooltip="Randomly select a part of the dataset. <br/><b>NOTE</b>: random seed is set, the random function will always return the same randomly selected set for given ratio.",
            width=50,
            margins=(0, 10, 0, 0),
            bottom=0,
            top=100,
        )

        self.pre_umap_normalization_widget = PreUmapNormalizationWidget(
            config=self.config, singals=singals
        )

        self.umap_section_widget = SectionWidget(
            "Umap configuration",
            tooltip="To get more information regarding below parameters visit UMAP official website. https://umap-learn.readthedocs.io",
            margins=(5, 10, 0, 0),
        )
        self.n_neighbors_widget = LabelValueWidget(
            "N-neighbors:",
            self.config.n_neighbors,
            singals,
            val_type=list[int],
            suffix_label=None,
            tooltip="Number of n samples for which UMAP will try to find common structure. Lower values favorites local structure whereas higher values will focus on more broader picture.",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )
        self.n_components_widget = LabelValueWidget(
            "N-components:",
            self.config.n_components,
            singals,
            val_type=list[int],
            suffix_label=None,
            tooltip="Number of dimensions to which data will be reduced. 2 or 3 dimensions can be used for visualization purposes also.",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )
        self.spread_widget = LabelValueWidget(
            "Spread:",
            self.config.spread,
            singals,
            val_type=float,
            suffix_label=None,
            tooltip="Parameter that allows to control data density <b>between the clusters</b> in the lower dimension embedding .",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )
        self.min_distance_widget = LabelValueWidget(
            "Min distance:",
            self.config.min_distance,
            singals,
            val_type=list[float],
            suffix_label=None,
            tooltip="Parameter that allows to control data density <b>between the points</b> in the lower dimension embedding. Defines how far points are allowed to be from each other in the lower dimensions.",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
        )
        # y is not given in UmapInspector
        self.target_weight_widget = LabelValueWidget(
            "Target weight:",
            self.config.target_weight,
            singals,
            val_type=float,
            suffix_label=None,
            tooltip="weighting factor between data topology and target topology. Controls how much labels influence neighbourhood structure, <0.5 - lower label influence, >0.5 - higher label influence.\
                <br/><b>NOTE</b>:When target is enabled, even when value is set to 0 it would still affect the results.",
            width=100,
            bottom=0,
            top=Consts.INT_MAX,
            margins=(10, 5, 0, 0),
        )
        self.metric_widget = MetricWidget(config=self.config, singals=singals)

        self.target_metric_widget = TargetMetricWidget(
            config=self.config, singals=singals
        )

        self.target_enabled_widget = MeasurementWidget(
            self.config.target_enabled,
            label="Enable target",
            tooltip="When partially labeled data is used it allows to determine whether UMAP should focus more to fit the points to labeled data of to focus more on data.<br/><b>WARNING</b>: causes strong overfitting when to high, should be set with cautious. Overfitting tests required.\
                <br/><b>WARNING2</b>: when option is selected, even when value is set to 0 it would still a little fot to the labels. In current solution setting target weight to 0 is equivalent of not passing labels.\
                <br/><b>Advised</b>: keep this option disabled.",
            value_changed=singals.value_changed,
            children=[self.target_weight_widget, self.target_metric_widget],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        def set_target(is_enabled):
            if is_enabled == False:
                self.target_weight_widget.update(0)
                self.target_metric_widget.update(None)

        self.target_enabled_widget.visibility_signal.connect(
            lambda is_enabled: set_target(is_enabled)
        )
        self.output_metric_widget = OutputMetricWidget(
            config=self.config, singals=singals
        )

        self.post_umap_section_widget = SectionWidget(
            "Post UMAP operations",
            margins=(5, 10, 0, 0),
        )

        self.plot_widget = MeasurementWidget(
            self.config.plot,
            label="Plot",
            tooltip="Result plotting, if more than 3 components is used data will be decreased with the use of TruncatedSVD (instead of PCA due to linearity and ability to not transform data points before dimensional reduction operation).",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        self.run_umap_widget = MeasurementWidget(
            self.config.run_umap,
            label="Run umap",
            tooltip="",
            value_changed=self.value_changed,
            children=[
                self.pre_umap_section_widget,
                self.sample_ratio_widget,
                self.pre_umap_normalization_widget,
                self.umap_section_widget,
                self.n_neighbors_widget,
                self.n_components_widget,
                self.spread_widget,
                self.min_distance_widget,
                self.metric_widget,
                self.target_enabled_widget,
                self.output_metric_widget,
                self.post_umap_section_widget,
                self.plot_widget,
            ],
            layout="Vertical",
            margins=(0, 0, 0, 0),
            margins_children=(10, 0, 0, 0),
        )

        layoutV = QVBoxLayout()
        layoutV.setSpacing(0)
        layoutV.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom
        layoutV.addStretch()
        layoutV.addWidget(self.run_umap_widget)

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    @property
    def value(self):
        if self.run_umap_widget.value == True:
            self._value.run_umap = True
            self._value.sample_ratio = self.sample_ratio_widget.value / 100
            self._value.pre_umap_normalization = (
                self.pre_umap_normalization_widget.value
            )
            self._value.n_neighbors = self.n_neighbors_widget.value
            self._value.n_components = self.n_components_widget.value
            self._value.min_distance = self.min_distance_widget.value
            self._value.spread = self.spread_widget.value
            self._value.target_weight = self.target_weight_widget.value
            self._value.metric = self.metric_widget.value
            self._value.target_metric = self.target_metric_widget.value
            self._value.target_enabled = self.target_enabled_widget.value
            self._value.output_metric = self.output_metric_widget.value
            self._value.plot = self.plot_widget.value
        else:
            self._value = self._value_original
            self._value.run_umap = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

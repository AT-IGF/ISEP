from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.common.config.configs.models.dataViewer import (
    SingleSamplePlotModel,
    BoundariesModel,
)
from src.common.config.configs import DataViewerConfig
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals


class SingleSamplePlotWidget(QWidget):
    def __init__(
        self,
        config: SingleSamplePlotModel,
        singals: SettingsSignals,
        modality_name: str,
        aggregation_function: str,
    ):
        super().__init__()
        self.value_original = config
        self._value = config

        layoutV_plots = QVBoxLayout()
        self.exclude_lower_than_widget = LabelValueWidget(
            label=f"Exclude, if {aggregation_function} is below",
            tooltip=f"Display only {modality_name} samples which {aggregation_function} value is above threshold",
            value=config.boundaries.exclude_lower_than,
            singals=singals,
            suffix_label="AU",
            margins=(10, 0, 0, 0),
            val_type=int | None,
        )
        # checkbox
        self.exclude_higher_than_widget = LabelValueWidget(
            label=f"Exclude, if {aggregation_function} is above",
            tooltip=f"Display only {modality_name} samples which {aggregation_function} value is below threshold",
            value=config.boundaries.exclude_higher_than,
            singals=singals,
            suffix_label="AU",
            margins=(10, 10, 0, 0),
            val_type=int | None,
        )
        self.plot_widget = MeasurementWidget(
            config.show,
            label=f"Plot {modality_name}",
            tooltip=f"Plot single particle {modality_name}",
            value_changed=singals.value_changed,
            children=[
                self.exclude_lower_than_widget,
                self.exclude_higher_than_widget,
            ],
            layout="Vertical",
        )
        layoutV_plots.addWidget(self.plot_widget)
        layoutV_plots.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        self.setLayout(layoutV_plots)

    @property
    def value(self):
        if self.plot_widget.value == True:
            self._value.show = True
            self._value.boundaries.exclude_lower_than = (
                self.exclude_lower_than_widget.value
            )
            self._value.boundaries.exclude_higher_than = (
                self.exclude_higher_than_widget.value
            )
        else:
            self._value = self.value_original
            self._value.show = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

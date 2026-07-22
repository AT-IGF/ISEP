from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.common.config.configs.models.dataViewer import (
    PlotCombinedModel,
)
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import SectionWidget


class PlotWidget(QWidget):
    def __init__(self, config: PlotCombinedModel, singals: SettingsSignals):
        super().__init__()
        self.config = config
        self.signals = singals

        layoutV_plots = QVBoxLayout()
        self.plot_styling_section_widget = SectionWidget(
            "Plot styling", margins=(10, 10, 15, 0)
        )

        self.n_cols_legend_widget = LabelValueWidget(
            "Legend columns:",
            config.n_cols,
            singals,
            val_type=int,
            tooltip="Number of columns in the legend",
            width=50,
            margins=(10, 10, 0, 0),
            bottom=1,
        )

        self.y_min_widget = LabelValueWidget(
            "Y axis min:",
            config.y_min,
            singals,
            val_type=int | None,
            suffix_label="AU",
            tooltip="Min value on the y axis",
            width=50,
            margins=(10, 10, 0, 0),
        )

        self.y_max_widget = LabelValueWidget(
            "Y axis max:",
            config.y_max,
            singals,
            val_type=int | None,
            suffix_label="AU",
            tooltip="Max value on the y axis",
            width=50,
            margins=(10, 10, 0, 0),
        )

        self.plot_modifications_section_widget = SectionWidget(
            "Data filtering", margins=(10, 10, 15, 0)
        )
        self.q_min_widget = LabelValueWidget(
            "Exclude percentiles lower than:",
            config.q_min,
            singals,
            val_type=int | None,
            suffix_label="pth",
            margins=(10, 10, 0, 0),
        )
        self.q_max_widget = LabelValueWidget(
            "Exclude percentiles higher than:",
            config.q_max,
            singals,
            val_type=int | None,
            suffix_label="pth",
            margins=(10, 10, 0, 0),
        )

        self.plot_widget = MeasurementWidget(
            self.config.plot,
            label="Plot combined",
            tooltip="Plot all classes in a single plot.",
            value_changed=singals.value_changed,
            children=[
                self.plot_styling_section_widget,
                self.n_cols_legend_widget,
                self.y_min_widget,
                self.y_max_widget,
                self.plot_modifications_section_widget,
                self.q_min_widget,
                self.q_max_widget,
            ],
            layout="Vertical",
            margins=(0, 10, 0, 0),
        )

        self._value_original = PlotCombinedModel(
            plot=self.plot_widget.value,
            q_min=self.q_min_widget.value,
            q_max=self.q_max_widget.value,
            n_cols=self.n_cols_legend_widget.value,
            y_min=self.y_min_widget.value,
            y_max=self.y_max_widget.value,
        )

        self._value = PlotCombinedModel(
            plot=self.plot_widget.value,
            q_min=self.q_min_widget.value,
            q_max=self.q_max_widget.value,
            n_cols=self.n_cols_legend_widget.value,
            y_min=self.y_min_widget.value,
            y_max=self.y_max_widget.value,
        )

        layoutV_plots.addWidget(self.plot_widget)
        self.setLayout(layoutV_plots)

    @property
    def value(self):
        self._value.plot = self.plot_widget.value
        self._value.q_min = self.q_min_widget.value
        self._value.q_max = self.q_max_widget.value
        self._value.n_cols = self.n_cols_legend_widget.value
        self._value.y_min = self.y_min_widget.value
        self._value.y_max = self.y_max_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

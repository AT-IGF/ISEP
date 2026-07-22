from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from src.common import Consts
from src.common.config.configs.models.dataViewer import (
    LifetimeModel,
    HistogramModel,
    PlotCombinedModel,
)
from src.common.config.configs import AllParticlesAvgsConfig
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import SectionWidget
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common.LayoutWidget import LayoutWidget
from src.ui.common.FieldsHelper import toogle_fields_visibility


class HistogramWidget(QWidget):
    AGGREGATION_FUNCTION = "AGGREGATION_FUNCTION"

    def __init__(
        self,
        config: HistogramModel,
        singals: SettingsSignals,
        units="AU",
        aggregation_function_tooltip="",
        hide=[],
    ):
        super().__init__()
        self.config = config

        layoutV_plots = QVBoxLayout()
        self.setLayout(layoutV_plots)

        self.plotting_options_section_widget = SectionWidget(
            "Plotting options", margins=(10, 10, 15, 0)
        )

        self.as_grid_widget = MeasurementWidget(
            config.display_as_grid,
            label="Display as grid",
            tooltip="All plots in one window but next to each other",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(0, 0, 0, 0),
        )

        self.share_y_grid_widget = MeasurementWidget(
            config.share_y_grid,
            label="Share y",
            tooltip="Plot y value common between the plots",
            value_changed=singals.value_changed,
            children=[],
            layout="Vertical",
            margins=(0, 0, 0, 0),
        )

        self.n_cols_widget = LabelValueWidget(
            "Columns:",
            config.n_cols,
            singals,
            val_type=int,
            tooltip="Number of columns in the plot",
            width=50,
            margins=(0, 0, 0, 0),
            bottom=0,
        )

        all_in_one_layout_widget = LayoutWidget(
            children=[
                self.as_grid_widget,
                self.share_y_grid_widget,
                self.n_cols_widget,
            ],
            margins=(10, 5, 0, 0),
        )

        sub_apps = [
            aggregated.Radio(
                HistogramModel.ALL_IN_ONE_MODE,
                config.display_mode,
                widget=all_in_one_layout_widget,
                label="All in one",
            ),
            aggregated.Radio(
                HistogramModel.ONE_BY_ONE_MODE, config.display_mode, label="One by one"
            ),
        ]

        self.display_mode_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            singals.value_changed,
            label="Display mode:",
            layout="Horizontal",
            tooltip="Show a single plot with all pollen types or one plot per pollen type",
            margins=(5, 5, 0, 0),
            is_white_background=True,
            sub_widgets_layout="Below",
        )

        self.hist_bins_widget = LabelValueWidget(
            "Bins:",
            config.hist_bins,
            singals,
            suffix_label=units,
            val_type=int,
            tooltip="Number of bins in the histogram",
            margins=(10, 10, 0, 0),
            bottom=0,
            top=Consts.INT_MAX,
        )

        self.plot_modifications_section_widget = SectionWidget(
            "Data filtering", margins=(10, 15, 15, 0)
        )

        sub_apps = [
            aggregated.Radio(
                HistogramModel.MAX_OPERATION, config.operation, label="max"
            ),
            aggregated.Radio(
                HistogramModel.AVG_OPERATION, config.operation, label="average"
            ),
        ]

        self.operation_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            singals.value_changed,
            label="Aggregation function:",
            layout="Horizontal",
            tooltip=aggregation_function_tooltip,
            margins=(5, 5, 0, 0),
            is_white_background=True,
            sub_widgets_layout="Below",
            force_hide=self.AGGREGATION_FUNCTION in hide,
        )

        self.lower_than_widget = LabelValueWidget(
            "Exclude lower than:",
            config.lower_than,
            singals,
            suffix_label=units,
            val_type=float | None,
            margins=(10, 10, 0, 0),
        )
        self.higher_than_widget = LabelValueWidget(
            "Exclude higher than:",
            config.higher_than,
            singals,
            suffix_label=units,
            val_type=float | None,
            margins=(10, 10, 0, 0),
        )
        self.plot_pointers_section_widget = SectionWidget(
            "Reference lines", margins=(10, 15, 15, 0)
        )
        self.q_min_widget = LabelValueWidget(
            "Lower percentile:",
            config and config.q_min,
            singals,
            suffix_label="pth",
            val_type=int | None,
            margins=(10, 10, 0, 0),
        )
        self.q_max_widget = LabelValueWidget(
            "Higher percentile:",
            config and config.q_max,
            singals,
            suffix_label="pth",
            val_type=int | None,
            margins=(10, 10, 0, 0),
        )
        self.custom_line_widget = LabelValueWidget(
            "Custom line at:",
            config and config.cutom_line,
            singals,
            suffix_label=units,
            val_type=float | None,
            margins=(10, 10, 0, 0),
        )

        self.histogram_widget = MeasurementWidget(
            self.config.plot,
            label="Plot histogram",
            tooltip="Plots per class histograms. Every channel is handled separately.",
            value_changed=singals.value_changed,
            children=[
                self.plotting_options_section_widget,
                self.display_mode_widget,
                self.hist_bins_widget,
                self.plot_modifications_section_widget,
                self.operation_widget,
                self.lower_than_widget,
                self.higher_than_widget,
                self.plot_pointers_section_widget,
                self.q_min_widget,
                self.q_max_widget,
                self.custom_line_widget,
            ],
            layout="Vertical",
            margins=(10, 0, 0, 0),
        )

        pointer_widgets = [
            self.plot_pointers_section_widget,
            self.q_min_widget,
            self.q_max_widget,
            self.custom_line_widget,
        ]
        toogle_fields_visibility(
            pointer_widgets,
            self.histogram_widget.is_checked()
            and self.as_grid_widget.value
            and self.display_mode_widget.selected_app.value
            == HistogramModel.ALL_IN_ONE_MODE,
        )

        self.display_mode_widget.value_changed.connect(
            lambda app, _value: toogle_fields_visibility(
                pointer_widgets,
                self.histogram_widget.is_checked()
                and (
                self.display_mode_widget.selected_app.value
                == HistogramModel.ONE_BY_ONE_MODE
                or self.display_mode_widget.selected_app.value
                == HistogramModel.ALL_IN_ONE_MODE
                and self.as_grid_widget.value == True),
            )
        )

        self._value = HistogramModel(
            plot=self.histogram_widget.value,
            operation=self.operation_widget.selected_app.value,
            lower_than=self.lower_than_widget.value,
            higher_than=self.higher_than_widget.value,
            q_min=self.q_min_widget.value,
            q_max=self.q_max_widget.value,
            cutom_line=self.custom_line_widget.value,
        )

        layoutV_plots.addWidget(self.histogram_widget)
        layoutV_plots.setContentsMargins(0, 10, 0, 0)  # left, top, right, bottom
        layoutV_plots.setSpacing(0)
        self.setLayout(layoutV_plots)

    @property
    def value(self):
        self._value.display_mode = self.display_mode_widget.selected_app.value
        self._value.hist_bins = self.hist_bins_widget.value
        self._value.plot = self.histogram_widget.value
        self._value.operation = self.operation_widget.selected_app.value
        self._value.lower_than = self.lower_than_widget.value
        self._value.higher_than = self.higher_than_widget.value
        self._value.q_min = self.q_min_widget.value
        self._value.q_max = self.q_max_widget.value
        self._value.cutom_line = self.custom_line_widget.value
        self._value.display_as_grid = self.as_grid_widget.value
        self._value.share_y_grid = self.share_y_grid_widget.value
        self._value.n_cols = self.n_cols_widget.value
        self._value.hist_bins = self.hist_bins_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

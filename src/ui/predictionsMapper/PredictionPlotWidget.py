from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)


from src.common.config.configs.models.predictionsMapper.PlotSettings import (
    LinePlotSettingsModel,
)
from src.common.config.configs.models.predictionsMapper.PlotSettings import (
    BarPlotSettingsModel,
)
from src.common.config import Config
from src.common.config.configs import PredictionsMapperConfig

from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common import MeasurementWidget
from src.ui.common import DirectorySelectorWidget
from src.ui.common import LayoutWidget
from src.ui.common import LabelValueWidget


class BarPlotTypeWidget(QWidget):

    def __init__(self, config: BarPlotSettingsModel, signals):
        super().__init__()
        self.current_config = Config.get(PredictionsMapperConfig)

        sub_apps = [
            aggregated.Radio(
                config.PARTICLES_PER_METER_CUBED, config.plot_type, label="P/m³"
            ),
            aggregated.Radio(
                config.PERCENTAGE_SHARE_IN_TIMESPAN_PLOT,
                config.plot_type,
                label="Share (%) within split time span",
            ),
        ]

        self.plot_type_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            signals.value_changed,
            label="Display mode:",
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
            tooltip="Normalization in which plot is displayed",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.plot_type_widget)
        layoutV.setContentsMargins(10, 5, 0, 0)
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        return self.plot_type_widget.selected_app.value

    @value.setter
    def value(self, value):
        self._value = value


class LinePlotSettingsWidget(QWidget):

    def __init__(self, config: LinePlotSettingsModel, signals):
        super().__init__()
        self._value = config
        self._value_original = config

        sub_apps = [
            aggregated.Radio(
                config.PARTICLES_PER_METER_CUBED,
                config.plot_type,
                label="P/m³",
            ),
            aggregated.Radio(config.COUNT, config.plot_type, label="Count"),
        ]

        self.plot_type_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            signals.value_changed,
            label="Display mode:",
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
            tooltip="Normalization in which plot is displayed",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.plot_type_widget)
        layoutV.setContentsMargins(10, 5, 0, 0)
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        self._value.plot_type = self.plot_type_widget.selected_app.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class BarPlotSettingsWidget(QWidget):

    def __init__(self, config: BarPlotSettingsModel, signals):
        super().__init__()
        self._value = config
        self._value_original = config
        self.months_of_expectance_mapping_path_widget = DirectorySelectorWidget(
            "Path",
            self._value.months_of_expectance_mapping_path,
            value_changed=signals.value_changed,
            show_modal=signals.show_modal,
            selector="FILE",
            extensions=DirectorySelectorWidget.JSON_FILE_EXTENSION,
            tooltip='Mapping file in json format containing information about expected months of pollination.\
                <br/><b>NOTE</b>: the user needs to specify the expected pollination themselves, months are mapped as 1 - January, 2 - February... \
                <br/><b>Example input</b>: { "Alnus": [2,3], "Corlus": [1, 2] }',
            margins=(0, 0, 0, 2),
        )

        self.is_months_of_expectance_widget = MeasurementWidget(
            self._value.is_months_of_expectance,
            label="Months of expectance",
            tooltip="indicate which pollination periods are expected for specific pollen type, non pollination periods will be greyed on the plot",
            value_changed=signals.value_changed,
            children=[self.months_of_expectance_mapping_path_widget],
            layout="Horizontal",
            margins=(10, 5, 0, 0),
        )

        self.n_cols_widget = LabelValueWidget(
            "Columns:",
            config.n_cols,
            signals,
            val_type=int,
            tooltip="Number of columns in the plot",
            width=50,
            margins=(10, 0, 0, 0),
            bottom=0,
        )

        self.show_particle_count_widget = MeasurementWidget(
            self._value.show_particle_count,
            label="Show particle count",
            tooltip="Add particle count line on the plot",
            value_changed=signals.value_changed,
            children=[],
            layout="Horizontal",
            margins=(10, 5, 0, 0),
        )
        self.display_as_grid_widget = MeasurementWidget(
            self._value.display_as_grid,
            label="Display as grid",
            tooltip="All plots in one window but next to each other",
            value_changed=signals.value_changed,
            children=[
                self.n_cols_widget,
                self.show_particle_count_widget,
                self.is_months_of_expectance_widget,
            ],
            layout="Horizontal",
            margins=(10, 5, 0, 0),
        )
        self.plot_type_widget = BarPlotTypeWidget(config=self._value, signals=signals)

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.plot_type_widget)
        layoutV.addWidget(self.display_as_grid_widget)
        layoutV.setContentsMargins(0, 0, 0, 0)
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        self._value.is_months_of_expectance = (
            self.is_months_of_expectance_widget.is_checked()
        )
        self._value.months_of_expectance_mapping_path = (
            self.months_of_expectance_mapping_path_widget.value
        )
        self._value.plot_type = self.plot_type_widget.value
        self._value.display_as_grid = self.display_as_grid_widget.value
        self._value.n_cols = self.n_cols_widget.value
        self._value.show_particle_count = self.show_particle_count_widget.is_checked()
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class PredictionPlotWidget(QWidget):
    def __init__(self, signals):
        super().__init__()
        self.current_config = Config.get(PredictionsMapperConfig)
        self._value = Config.get(PredictionsMapperConfig).plot_settings
        self._value_original = Config.get(PredictionsMapperConfig).plot_settings

        self.line_plot_settings_widget = LinePlotSettingsWidget(
            self._value.line_plot_settings, signals
        )
        self.bar_plot_settings_widget = BarPlotSettingsWidget(
            self._value.bar_plot_settings, signals
        )

        sub_apps = [
            aggregated.Radio(
                self._value.LINE_STYLE_PLOT,
                self._value.plot_style,
                widget=self.line_plot_settings_widget,
                label="Line",
            ),
            aggregated.Radio(
                self._value.BAR_STYLE_PLOT,
                self._value.plot_style,
                widget=self.bar_plot_settings_widget,
                label="Bar",
            ),
        ]

        self.plot_style_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            signals.value_changed,
            label="Plot style:",
            layout="Horizontal",
            margins=(0, 10, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
            tooltip="The way in which plot is presented.",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.plot_style_widget)
        layoutV.setContentsMargins(10, 0, 0, 0)
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        if self.plot_style_widget.selected_app.value == self._value.LINE_STYLE_PLOT:
            self._value = self._value_original
            self._value.plot_style = self._value.LINE_STYLE_PLOT
            self._value.line_plot_settings = self.line_plot_settings_widget.value
        else:
            self._value = self._value_original
            self._value.plot_style = self._value.BAR_STYLE_PLOT
            self._value.bar_plot_settings = self.bar_plot_settings_widget.value

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

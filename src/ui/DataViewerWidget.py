from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QVBoxLayout,
    QScrollArea,
)

from src.common.config.configs.models.dataViewer.SingleSamplePlotModel import (
    SingleSamplePlotModel,
)
from src.common.config.configs import TypesConfig
from src.common.config import Config
from src.common.config.configs import (
    DataViewerConfig,
    AllParticlesAvgsConfig,
)
from src.ui.common.SubmitWidget import SubmitWidget
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget

from src.ui.dataViewer import (
    SettingsSignals,
    SameTypeCountWidget,
    RandWidget,
)
import matplotlib
from src.ui.dataViewer import aggregatedSamples as aggregated

from src.ui.common.FormWidget import FormWidget, SubApp
import src.common.tensorflow.InputModelNames as inputNames
from src.ui.common import DirectorySelectorWidget
from src.ui.common.businessComponents import PollenTypesWidget
from src.ui.dataViewer.settigsWidget.SingleSamplePlotWidget import (
    SingleSamplePlotWidget,
)
from src.ui.common.businessComponents import FilterWidget

matplotlib.use("Qt5Agg")


class SettigsWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.config: DataViewerConfig = Config.get(DataViewerConfig)
        types_config: TypesConfig = Config.get(TypesConfig)
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )

        self.pollen_types_exclude_widget = PollenTypesWidget(
            pollen_types=self.config.pollen_types_to_show,
            signals=singals,
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.RESET_OPTION,
            ],
            show_no_types_error=False,
            label="Pollen types to show",
            tooltip="Labeled samples directories that will not take part in the training",
        )
        self.filter_widget = FilterWidget(
            filter_path=self.config.filter_path, singals=singals
        )
        self.same_type_count_widget = LabelValueWidget(
            label="Same type count",
            value=self.config.same_type_count,
            singals=singals,
            tooltip="Count of samples from the same type to be displayed.",
            val_type=int,
            margins=(10, 10, 0, 0),
            bottom=1,
        )

        self.rand_0_1_frequency_widget = LabelValueWidget(
            label="Random frequency",
            value=self.config.rand_0_1_frequency,
            singals=singals,
            tooltip="Randomizes particle type that will be processed. If '0' every particle will be taken. If '0.5' every second.",
            val_type=float,
            bottom=0,
            top=1,
            margins=(10, 10, 0, 0),
        )
        self.spectrum_plot_widget = SingleSamplePlotWidget(
            config=self.config.spectrum_plot,
            singals=singals,
            modality_name="fluorescence spectral ranges",
            aggregation_function="max peak",
        )
        self.lifetime_plot_widget = SingleSamplePlotWidget(
            config=self.config.lifetime_plot,
            singals=singals,
            modality_name="fluorescence lifetime",
            aggregation_function="max peak",
        )
        self.scattering_plot_widget = SingleSamplePlotWidget(
            config=self.config.scattering_plot,
            singals=singals,
            modality_name="scattering",
            aggregation_function="average",
        )
        self.show_plots_widget = MeasurementWidget(
            self.config.show_plots,
            label="Show plots",
            margins=(10, 10, 0, 0),
            value_changed=singals.value_changed,
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.pollen_types_exclude_widget)
        layoutV.addWidget(self.filter_widget)
        layoutV.addWidget(self.same_type_count_widget)
        layoutV.addWidget(self.rand_0_1_frequency_widget)
        layoutV.addWidget(self.spectrum_plot_widget)
        layoutV.addWidget(self.lifetime_plot_widget)
        layoutV.addWidget(self.scattering_plot_widget)
        layoutV.addWidget(self.show_plots_widget)
        layoutV.addStretch(1)
        layoutV.setAlignment(Qt.AlignTop)
        layoutV.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)


class SingleSampleWidget(QWidget):
    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        config: DataViewerConfig = Config.get(DataViewerConfig)

        save_directory = DirectorySelectorWidget(
            label="Plots save directory:", init_path=config.get_save_path()
        )
        settings = SettigsWidget()

        def get_config_callback():
            return self.get_new_config(save_directory, settings)

        from src.dataViewer.DataViewer import handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=get_config_callback,
            on_run_click=handle,
        )

        widgets = [settings, save_directory]
        [
            widget.value_changed.connect(
                lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
            )
            for widget in widgets
        ]

        widgets.append(submit_widget)

        [widget.show_modal.connect(lambda x: self.show_modal(x)) for widget in widgets]

        self.layout = QVBoxLayout(self)

        [self.layout.addWidget(widget) for widget in widgets]
        self.layout.setSpacing(0)
        self.layout.addStretch(1)
        self.layout.setAlignment(Qt.AlignTop)

        container = QWidget()
        container.setLayout(self.layout)
        p = container.palette()
        p.setColor(container.backgroundRole(), Qt.white)
        container.setPalette(p)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addWidget(submit_widget)

    def show_modal(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self, save_directory: DirectorySelectorWidget, settings: SettigsWidget
    ):

        new_config = DataViewerConfig(
            show_plots=settings.show_plots_widget.value,
            plots_save_path=save_directory.value,
            filter_path=settings.filter_widget.value,
            same_type_count=settings.same_type_count_widget.value,
            spectrum_plot=settings.spectrum_plot_widget.value,
            lifetime_plot=settings.lifetime_plot_widget.value,
            scattering_plot=settings.scattering_plot_widget.value,
            rand_0_1_frequency=settings.rand_0_1_frequency_widget.value,
            pollen_types_to_show=settings.pollen_types_exclude_widget.value,
        )

        return new_config


class AggregatedSamplesWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        config: AllParticlesAvgsConfig = Config.get(AllParticlesAvgsConfig)
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )

        sub_apps = [
            aggregated.Radio(
                inputNames.LIFETIME,
                config.metric_to_process,
                aggregated.LifetimeWidget(config.lifetime, singals),
            ),
            aggregated.Radio(
                inputNames.SCATTERING,
                config.metric_to_process,
                aggregated.ScatteringWidget(config.scattering, singals),
            ),
            aggregated.Radio(
                inputNames.SPECTRUM,
                config.metric_to_process,
                aggregated.SpectrumWidget(config.spectrum, singals),
            ),
            aggregated.Radio(
                inputNames.SIZE,
                config.metric_to_process,
                aggregated.SizeWidget(config.size, singals),
            ),
        ]

        form_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            self.value_changed,
            label="Modality:",
            layout="Horizontal",
            margins=(10, 10, 0, 0),
            is_white_background=True,
            sub_widgets_layout="Below",
        )
        settings_widget = aggregated.SettigsWidget(config, singals)

        def get_config_callback():
            return self.get_new_config(settings_widget, form_widget)

        # def handle_func():

        #     return

        from src.dataViewer.AllParticlesAvgs import handle as _handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=get_config_callback,
            on_run_click=_handle,
        )

        self.value_changed.connect(
            lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
        )
        self.show_modal.connect(lambda x: self.show_modal_fn(x))

        widgets = [settings_widget, form_widget, submit_widget]

        self.layout = QVBoxLayout()
        [self.layout.addWidget(widget) for widget in widgets]

        self.layout.setSpacing(0)
        self.layout.addStretch(1)
        self.layout.setAlignment(Qt.AlignTop)

        container = QWidget()
        container.setLayout(self.layout)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addWidget(submit_widget)

    def show_modal_fn(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self,
        settings_widget: aggregated.SettigsWidget,
        radio_selector: aggregated.RadioSelectorWidget,
    ):
        config: AllParticlesAvgsConfig = Config.get(AllParticlesAvgsConfig)

        def get_app_model_or_none(app_name):
            sub_app = [x for x in radio_selector.sub_apps if x.value == app_name][0]
            return sub_app.widget.value

        new_config = AllParticlesAvgsConfig(
            metric_to_process=radio_selector.selected_app.value,
            pollen_types=settings_widget.pollen_types_widget.value,
            filter_path=settings_widget.filter_widget.value,
            single_type_count=settings_widget.single_type_count_widget.value,
            lifetime=get_app_model_or_none(inputNames.LIFETIME),
            spectrum=get_app_model_or_none(inputNames.SPECTRUM),
            scattering=get_app_model_or_none(inputNames.SCATTERING),
            size=get_app_model_or_none(inputNames.SIZE),
        )

        return new_config


class DataViewerWidget(QWidget):
    def __init__(self, parent):
        super(DataViewerWidget, self).__init__(parent)
        sub_apps = [
            SubApp("Single sample", SingleSampleWidget()),
            SubApp("Aggregated samples", AggregatedSamplesWidget()),
        ]

        self.form_widget = FormWidget(self, sub_apps)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.form_widget)
        self.setLayout(self.layout)

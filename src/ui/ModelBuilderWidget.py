from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QVBoxLayout,
    QScrollArea,
)

from src.common.config import Config
from src.common.config.configs import (
    ModelBuilderConfig,
    ModelBuilderUnsupervisedConfig,
    ModelBuilderScalerConfig,
)

from src.ui.common.SubmitWidget import SubmitWidget
from src.ui.dataViewer import (
    SettingsSignals,
)
import matplotlib
from src.ui.dataViewer import aggregatedSamples as aggregated

from src.ui.common.FormWidget import FormWidget, SubApp
from src.ui.modelBuilder import supervised as supervised
from src.ui.modelBuilder import unsupervised as unsupervised
from src.ui.modelBuilder import scaler as scaler
from src.ui.common import BannerWidget


matplotlib.use("Qt5Agg")


class SupervisedWidget(QWidget):

    def __init__(self):
        super().__init__()
        config: ModelBuilderConfig = Config.get(ModelBuilderConfig)
        banner_widget = BannerWidget(type="Warning")

        scroll = QScrollArea()
        settings = supervised.SettigsWidget(banner_widget)
        summaries_widget = supervised.SummariesWidget(scroll)
        calibration_widget = supervised.CalibrationWidget(
            summaries_widget.model_summary_banner_signal,
            scroll,
            model_name_signal=settings.model_save_name_widget.editingFinished,
        )

        def get_config_callback():
            return self.get_new_config(settings, summaries_widget, calibration_widget)

        from src.modelBuilder.ModelBuilder import handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=get_config_callback,
            on_run_click=handle,
        )

        widgets = [settings, calibration_widget, summaries_widget, banner_widget]
        [
            widget.value_changed.connect(
                lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
            )
            for widget in widgets
        ]

        widgets.append(submit_widget)

        [widget.show_modal.connect(lambda x: self.show_modal(x)) for widget in widgets]

        self.layout = QVBoxLayout()
        [self.layout.addWidget(widget) for widget in widgets]
        self.layout.addStretch(1)

        container = QWidget()
        container.setLayout(self.layout)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addWidget(banner_widget)
        main_layout.addWidget(submit_widget)

        self.setLayout(main_layout)

    def show_modal(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self,
        settings: supervised.SettigsWidget,
        summaries_widget: supervised.SummariesWidget,
        calibration_widget: supervised.CalibrationWidget,
    ):
        config: ModelBuilderConfig = Config.get(ModelBuilderConfig)

        new_config = ModelBuilderConfig(
            model_save_name=settings.model_save_name_widget.value,
            excludeTypes=settings.exclude_types_widget.get_types(),
            learningModels=settings.learning_models_widget.get_selected_values(),
            pollen_types_cache_rel_path=settings.pollen_types_cache_dir_widget.value,
            test_model_name=settings.test_model_name_widget.value + "_test_model",
            run_training=settings.run_training_widget.value == True,
            filter_rel_path=settings.filter_rel_path_widget.value,
            scaler_path=settings.scaler_widget.value,
            summaries=summaries_widget.value,
            train_parameters=settings.train_parameters_widget.value,
            calibration=calibration_widget.value,
        )

        return new_config


class UnsupervisedWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )
        banner_widget = BannerWidget(type="Warning")

        scroll = QScrollArea()
        settings_widget = unsupervised.SettigsWidget(singals, banner_widget)
        cluster_widget = unsupervised.ClusterParameters(singals)
        verify_widget = unsupervised.VerifyWidget(singals)

        def get_config_callback():
            return self.get_new_config(
                settings_widget=settings_widget,
                cluster_widget=cluster_widget,
                verify_widget=verify_widget,
            )

        from src.modelBuilder.ModelBuilderUnsupervided import handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=get_config_callback,
            on_run_click=handle,
        )

        self.value_changed.connect(
            lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
        )
        self.show_modal.connect(lambda x: self.show_modal_fn(x))

        widgets = [
            settings_widget,
            verify_widget,
            cluster_widget,
            banner_widget,
            submit_widget,
        ]

        self.layout = QVBoxLayout()
        [self.layout.addWidget(widget) for widget in widgets]

        container = QWidget()
        container.setLayout(self.layout)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addWidget(banner_widget)
        main_layout.addWidget(submit_widget)

    def show_modal_fn(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self,
        settings_widget: unsupervised.SettigsWidget,
        cluster_widget: unsupervised.ClusterParameters,
        verify_widget: unsupervised.VerifyWidget,
    ):
        config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        new_config = ModelBuilderUnsupervisedConfig(
            model_save_name=settings_widget.model_save_name_widget.value,
            train_parameters=settings_widget.value,
            cluster_parameters=cluster_widget.value,
            verify_model=verify_widget.value,
        )

        return new_config


class ScalerdWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        config: ModelBuilderScalerConfig = Config.get(ModelBuilderScalerConfig)
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )

        settings_widget = scaler.SettingsWidget(singals)

        def get_config_callback():
            return self.get_new_config(settings_widget)

        from src.modelBuilder.ModelBuilderDataScaler import handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=get_config_callback,
            on_run_click=handle,
        )

        self.value_changed.connect(
            lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
        )
        self.show_modal.connect(lambda x: self.show_modal_fn(x))

        widgets = [settings_widget, submit_widget]

        self.layout = QVBoxLayout(self)
        [self.layout.addWidget(widget) for widget in widgets]
        self.layout.addStretch()
        self.setLayout(self.layout)

    def show_modal_fn(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self,
        settings_widget: scaler.SettingsWidget,
    ):

        new_config = ModelBuilderScalerConfig(
            scaler_name=settings_widget.scaler_name_widget.value,
            pollen_types_binaries_paths=settings_widget.pollen_types_binaries_paths_widget.value,
            rescale_existing_files=settings_widget.rescale_existing_files_widget.value,
            scaler_save_path=settings_widget.scaler_save_path_widget.value,
            filter_rel_path=settings_widget.filter_rel_path_widget.value,
        )

        return new_config


class ModelBuilderWidget(QWidget):
    def __init__(self, parent):
        super(ModelBuilderWidget, self).__init__(parent)
        sub_apps = [
            SubApp("Supervised", SupervisedWidget()),
            SubApp("Unsupervised", UnsupervisedWidget()),
            SubApp("Scaler", ScalerdWidget()),
        ]

        self.form_widget = FormWidget(self, sub_apps)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.form_widget)
        self.setLayout(self.layout)

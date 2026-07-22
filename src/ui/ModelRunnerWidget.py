from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QAbstractItemView,
    QScrollArea,
)
from PyQt5.QtGui import QColor

from src.core import PathHelper, is_blank

from src.ui.common import IconLabel, toogle_field_visibility
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelRunnerConfig
import src.ui.common.Messages as messages
from src.ui.common import DirectorySelectorWidget, MeasurementWidget, BannerWidget
from src.ui.modelBuilder.common import ScalerWidget
from src.ui.dataViewer import SettingsSignals
from src.ui.common.SubmitWidget import SubmitWidget
from src.ui.modelRunner import UnsupervisedWidget
from src.ui.common import LabelValueWidget
from src.ui.common import SectionWidget
from src.ui.common import LayoutWidget
from src.ui.common.businessComponents import PollenTypesWidget
from src.ui.common import DirectoriesSelectorWidget
from src.ui.common.businessComponents import FilterWidget


def is_valid_path(path: str):
    return path != "" or path.startswith(Consts.RESOURCES_PATH)


class OptionsWidget(QWidget):
    filter_path_value_changed = pyqtSignal(object, bool)
    filter_value_changed = pyqtSignal(object, bool)

    def __init__(self, signals, banner_widget):
        super().__init__()
        self.config = Config.get(ModelRunnerConfig)

        self.scaler_widget = ScalerWidget(
            scaler_path=self.config.scaler_path,
            value_changed=signals.value_changed,
            show_modal=signals.show_modal,
            banner_widget=banner_widget,
            margins=(0, 10, 0, 0),
        )

        self.filter_rel_path_widget = FilterWidget(
            filter_path=self.config.filter_rel_path, singals=signals
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.scaler_widget)
        layoutV.addWidget(self.filter_rel_path_widget)
        layoutV.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom

        self.setLayout(layoutV)


class ProcessingWidget(QWidget):
    def __init__(self, singals):
        super().__init__()
        self.value_changed = singals.value_changed
        self.show_modal = singals.show_modal

        self.current_config = Config.get(ModelRunnerConfig)
        config = Config.get(ModelRunnerConfig)
        self._file_dateformat_regex = config.processing.file_dateformat_regex
        self._date_format_from_regex_mapping = (
            config.processing.date_format_from_regex_mapping
        )
        self._combined_files_filename = config.processing.combined_files_filename
        self._threshold = config.processing.threshold

        filename_section_widget = SectionWidget(
            "Binary files file names processing", margins=(5, 10, 5, 0)
        )
        self.file_dateformat_regex_widget = LabelValueWidget(
            "Filename regex date:",
            config.processing.file_dateformat_regex,
            singals,
            val_type=str,
            tooltip="Regex representation of date within filename. For example for filename 'D_001060749_202006160650' regex is '\d{4}\d{2}\d{2}\d{2}\d{2}'",
            margins=(10, 5, 0, 0),
        )

        self.date_format_from_regex_mapping_widget = LabelValueWidget(
            "Filename regex date mapping:",
            config.processing.date_format_from_regex_mapping,
            singals,
            val_type=str,
            tooltip="Python date format of regex representation. For example for '\d{4}\d{2}\d{2}\d{2}\d{2}' mapping is '%Y%m%d%H%M'",
            margins=(10, 10, 0, 0),
        )

        layoutH_batch_info = QHBoxLayout()
        layoutH_batch_info.setAlignment(Qt.AlignLeft)

        logging_section_widget = SectionWidget("Logging", margins=(5, 10, 5, 0))
        self.info_threshold_widget = LabelValueWidget(
            "Info threshold:",
            config.processing.threshold,
            singals,
            val_type=float,
            tooltip="Displays live summary regarding amount of detected particles. Just informational - files are saved with threshold 0, retrieving aggregated threshold is done in model mapper.",
            margins=(10, 10, 0, 0),
        )

        data_saving_section_widget = SectionWidget("Data saving", margins=(5, 10, 5, 0))

        self.save_directory_widget = DirectorySelectorWidget(
            "Save directory:",
            config.processing.get_progress_dir(),
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            selector="DIRECTORY",
            tooltip="Directory under which output with 0 threshold will be saved (an input for predictions mapper).",
            margins=(10, 5, 0, 0),
        )

        self.combined_files_filename_widget = LabelValueWidget(
            "Output filename",
            config.processing.combined_files_filename,
            singals,
            val_type=str,
            prefix_label="tr_0_",
            suffix_label=".csv",
            margins=(10, 0, 0, 0),
        )

        combine_files_widget = self.CombineIntoOneFileWidget(
            self.save_directory_widget.value
        )

        combined_files_layout = LayoutWidget(
            children=[self.combined_files_filename_widget, combine_files_widget],
            margins=(0, 0, 0, 0),
        )

        # temporarly disabled
        # self.combined_files_widget = MeasurementWidget(
        #     is_blank(config.processing.combined_files_filename),
        #     label="Combine into one file",
        #     tooltip="Merge result into one file. </br>Default: result will be saved in separated date files.",
        #     value_changed=self.combine_into_file_value_changed,
        #     children=[combined_files_layout],
        #     layout="Horizontal",
        #     margins=(10, 10, 0, 0),
        # )

        self.combined_files_filename_widget.editingFinished.connect(
            lambda val: combine_files_widget.toggle_warning_icon(val)
        )
        combine_files_widget.toggle_warning_icon(
            config.processing.combined_files_filename
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(filename_section_widget)
        layoutV.addWidget(self.file_dateformat_regex_widget)
        layoutV.addWidget(self.date_format_from_regex_mapping_widget)
        layoutV.addWidget(logging_section_widget)
        layoutV.addWidget(self.info_threshold_widget)
        layoutV.addWidget(data_saving_section_widget)
        layoutV.addWidget(self.save_directory_widget)
        layoutV.addWidget(combined_files_layout)
        self.setLayout(layoutV)
        # self.setAutoFillBackground(True)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.white)
        # self.setPalette(p)

    def on_edit_finish(self, prop, field):
        if field.text() == "":
            self.show_modal.emit("Field cannot be empty")
            field.setText(getattr(self, prop))
            return
        setattr(self, prop, field.text())

    @property
    def combined_files_filename(self):
        return self._combined_files_filename

    @combined_files_filename.setter
    def combined_files_filename(self, value):
        if self._combined_files_filename != value:
            self._combined_files_filename = value
            self.signals.value_changed.emit(self.combined_files_filename)

    class CombineIntoOneFileWidget(QWidget):
        textChanged = pyqtSignal(object)
        editingFinished = pyqtSignal()

        def __init__(self, save_directory):
            super().__init__()
            layoutH_combine_files = QHBoxLayout()
            file_exists_warning_icon = IconLabel(
                "mdi.alert-outline",
                tooltip="File already exists! New data will be added to the existing file.",
                color=QColor(185, 144, 8, 255),
            )

            layoutH_combine_files.addWidget(file_exists_warning_icon)
            save_path = PathHelper.get_absolute_path(
                Consts.RESOURCES_PATH, save_directory, raise_on_not_found=False
            )

            def toggle_warning_icon(filename: str):
                toogle_field_visibility(
                    file_exists_warning_icon,
                    PathHelper.is_file_exists(
                        PathHelper.join_path(save_path, f"tr_0_{filename}.csv")
                    ),
                )

            self.toggle_warning_icon = toggle_warning_icon
            layoutH_combine_files.setContentsMargins(5, 0, 0, 0)
            layoutH_combine_files.setSpacing(0)
            layoutH_combine_files.addStretch(1)
            self.setLayout(layoutH_combine_files)


class ListWidget(QListWidget):
    def Clicked(self, item):
        QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())


class ModelRunnerWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self, parent):
        super(ModelRunnerWidget, self).__init__(parent)
        config = Config.get(ModelRunnerConfig)
        signals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )
        scroll = QScrollArea()

        banner_widget = BannerWidget(type="Warning")

        dirs_list = DirectoriesSelectorWidget(
            directories=config.types_to_predict_rel_dirs,
            label="Directories to predict",
            signals=signals,
            tooltip="Directories list of folders with measurements.<br/>\
                Root folder can be set, e.g. 'Measurements' containing sub-folders with the measurements:\
                <ul>\
                    <li>Measurements/Day1</li>\
                    <li>Measurements/Day2</li>\
                    <li>Measurements/...</li>\
                </ul>",
        )

        model_path = DirectorySelectorWidget(
            label="Model path",
            init_path=config.model_rel_path,
            selector="FILE",
            extensions=[
                DirectorySelectorWidget.H5_EXTENSION,
                DirectorySelectorWidget.KERAS_EXTENSION,
                DirectorySelectorWidget.TF_MODEL_EXTENSION,
            ],
            value_changed=self.value_changed,
            show_modal=self.show_modal,
            align=None,
            tooltip="Path to the trained model from the Model builder supervised section",
            banner=(banner_widget, "Trained model is not set"),
        )
        filter_widget = OptionsWidget(signals, banner_widget)
        unsupervised_widget = UnsupervisedWidget(singals=signals)

        pollen_types = PollenTypesWidget(
            config.pollen_types,
            signals=signals,
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.MOVE_OPTION,
            ],
            margins=(10, 10, 0, 0),
        )

        processing = ProcessingWidget(
            singals=signals,
        )  # should be below 'dirs_list' due to signals emitting on load

        def model_runner_config():
            return self.get_new_config(
                dirs_list,
                model_path,
                filter_widget,
                unsupervised_widget,
                pollen_types,
                processing,
            )

        from src.modelRunner.ModelRunner import handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=model_runner_config,
            on_run_click=handle,
        )

        self.value_changed.connect(
            lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
        )
        self.show_modal.connect(lambda x: self.show_modal_fn(x))

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(model_path)
        self.layout.addWidget(dirs_list)
        self.layout.addWidget(filter_widget)
        self.layout.addWidget(unsupervised_widget)
        self.layout.addWidget(pollen_types)
        self.layout.addWidget(processing)

        container = QWidget()
        container.setLayout(self.layout)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addWidget(banner_widget)
        main_layout.addWidget(submit_widget)

        self.setLayout(self.layout)

    def show_modal_fn(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self,
        dirs_list: DirectoriesSelectorWidget,
        model_path: DirectorySelectorWidget,
        filter_widget: OptionsWidget,
        unsupervised_widget: UnsupervisedWidget,
        pollen_types: PollenTypesWidget,
        processing: ProcessingWidget,
    ):
        from src.common.config.configs.models.modelRunner import ProcessingModel

        new_processing = ProcessingModel(
            output_dir=processing.save_directory_widget.value,
            file_dateformat_regex=processing.file_dateformat_regex_widget.value,
            date_format_from_regex_mapping=processing.date_format_from_regex_mapping_widget.value,
            combined_files_filename=processing.combined_files_filename_widget.value,
            threshold=processing.info_threshold_widget.value,
        )
        new_config = ModelRunnerConfig(
            types_to_predict_rel_dirs=dirs_list.value,
            filter_rel_path=filter_widget.filter_rel_path_widget.value,
            scaler_path=filter_widget.scaler_widget.value,
            model_rel_path=model_path.value,
            pollen_types=pollen_types.get_types(),
            processing=new_processing,
            unsupervised=unsupervised_widget.value,
        )
        return new_config

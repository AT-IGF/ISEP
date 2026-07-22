from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QVBoxLayout,
    QScrollArea,
)


from src.core.path import PathHelper
from src.common.config import Config
from src.common.config.configs import PredictionsMapperConfig

from src.ui.common import (
    DirectorySelectorWidget,
)
from src.ui.dataViewer import SettingsSignals
from src.ui.common.SubmitWidget import SubmitWidget
from src.ui.predictionsMapper import SplitTimespanWidget
from src.ui.predictionsMapper import PredictionPlotWidget
from src.ui.predictionsMapper import ThresholdWidget
from src.ui.predictionsMapper import PreviewWidget
from src.ui.common.businessComponents import PollenTypesWidget
from src.ui.common import BannerWidget


class PredictionsMapperWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self, parent):
        super(PredictionsMapperWidget, self).__init__(parent)
        config = Config.get(PredictionsMapperConfig)
        scroll = QScrollArea()
        signals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )
        banner_widget = BannerWidget(type="Warning")

        file_to_process_widget = DirectorySelectorWidget(
            label="File to process",
            init_path=config.file_to_process_rel_path,
            value_changed=self.value_changed,
            show_modal=self.show_modal,
            selector="FILE",
            extensions=DirectorySelectorWidget.CSV_FILE_EXTENSION,
            align=None,
            tooltip="Model runner threshold 0 output file.",
            margins=(10, 10, 0, 0),
            banner=(banner_widget, "File to process is not set"),
        )

        split_timespan_widget = SplitTimespanWidget(signals=signals)
        threshold_widget = ThresholdWidget(signals=signals)
        pollen_types_widget = PollenTypesWidget(
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
        plot_type_widget = PredictionPlotWidget(signals=signals)
        preview_widget = PreviewWidget(signals=signals)
        save_directory_widget = DirectorySelectorWidget(
            label="Save directory",
            init_path=config.save_path_rel_path,
            value_changed=self.value_changed,
            show_modal=self.show_modal,
            selector="DIRECTORY",
            align=None,
            tooltip="Result output directory.",
            margins=(10, 15, 0, 0),
        )

        def predictions_mapper_config():
            return self.get_new_config(
                file_to_process=file_to_process_widget,
                threshold=threshold_widget,
                split_timespan=split_timespan_widget,
                pollen_types=pollen_types_widget,
                plot=plot_type_widget,
                preview=preview_widget,
                save_directory=save_directory_widget,
            )

        from src.predictionsMapper.PredictionsMapper import handle

        submit_widget = SubmitWidget(
            config=config,
            config_callback=predictions_mapper_config,
            on_run_click=handle,
        )

        self.value_changed.connect(
            lambda obj, is_changed: submit_widget.on_form_change(obj, is_changed)
        )
        self.show_modal.connect(lambda x: self.show_modal_fn(x))

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(file_to_process_widget)
        self.layout.addWidget(split_timespan_widget)
        self.layout.addWidget(threshold_widget)
        self.layout.addWidget(pollen_types_widget)
        self.layout.addWidget(plot_type_widget)
        self.layout.addWidget(preview_widget)
        self.layout.addWidget(save_directory_widget)
        self.layout.addWidget(submit_widget)

        container = QWidget()
        container.setLayout(self.layout)

        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        main_layout.addWidget(banner_widget)
        main_layout.addWidget(submit_widget)

        self.layout.addStretch(1)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def show_modal_fn(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_new_config(
        self,
        file_to_process: DirectorySelectorWidget,
        threshold: ThresholdWidget,
        split_timespan: SplitTimespanWidget,
        pollen_types: PollenTypesWidget,
        preview: PreviewWidget,
        plot: PredictionPlotWidget,
        save_directory: DirectorySelectorWidget,
    ):
        from src.common.config.configs.models.predictionsMapper import (
            SplitTimespanModel,
        )

        new_config = PredictionsMapperConfig(
            file_to_process_rel_path=file_to_process.value,
            save_path_rel_path=save_directory.value,
            split_timespan=split_timespan.value,
            pollen_types=pollen_types.get_types(),
            thresholds=threshold.value,
            preview=preview.value,
            plot_settings=plot.value,
        )
        return new_config

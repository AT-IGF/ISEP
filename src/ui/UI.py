from src.common.tensorflow.Pathes import patch_stdout

patch_stdout()
import logging
import sys, platform
from functools import partial

from PyQt5.QtWidgets import QApplication, QMainWindow
from src.core.path import PathHelper
from src.common.tensorflow import setup_module_logger
from src.common import override_config_log
from src.ui.common.FormWidget import FormWidget, SubApp
from src.ui.common import AppSplash
import time
from src.common import Consts
from PyQt5.QtGui import QIcon


class MainWindow(QMainWindow):
    APP_ICON_PATH = f"{Consts.RESOURCES_PATH}/ui/icons/app.ico"

    def __init__(self):
        super().__init__()
        self.hide()

        self.setWindowTitle("ISEP")
        self.resize(800, 750)

        from src.ui.ModelBuilderWidget import ModelBuilderWidget
        from src.ui.ModelRunnerWidget import ModelRunnerWidget
        from src.ui.PredictionsMapperWidget import PredictionsMapperWidget
        from src.ui.DataViewerWidget import DataViewerWidget
        from src.ui.GeneralSettingsWidget import GeneralSettingsWidget
        sub_apps = [
            SubApp("General", GeneralSettingsWidget(self)),
            SubApp("Data viewer", DataViewerWidget(self)),
            SubApp("Model builder", ModelBuilderWidget(self)),
            SubApp("Model runner", ModelRunnerWidget(self)),
            SubApp("Predictions mapper", PredictionsMapperWidget(self)),
        ]

        self.form_widget = FormWidget(self, sub_apps)
        self.setCentralWidget(self.form_widget)


def handle():
    APP_ICON_PATH = f"{Consts.RESOURCES_PATH}/ui/icons/app.ico"

    if platform.system() == "Windows":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ai.isep.particledetector"
        )

    app = QApplication(sys.argv)
    if PathHelper.is_file_exists(APP_ICON_PATH):
        app.setWindowIcon(QIcon(APP_ICON_PATH))
    else:
        print(f"App icon not found: {APP_ICON_PATH}")
        
    splash = AppSplash("ISEP")
    splash.show()
    time.sleep(0.1)
    app.processEvents()

    window = MainWindow()
    window.show()

    splash.finish(window)

    import src.ui.common.FieldsHelper as fh
    fh._suppress_show = False # workaround for blinking windows on app load

    sys.exit(app.exec_())


if __name__ == "__main__":
    import multiprocessing as mp
    mp.freeze_support()
    mp.set_start_method("spawn", force=True)
    setup_module_logger(module_name="ui")
    try:
        override_config_log(logger_name="ui")
        handle()
    except Exception as ex:
        logging.getLogger().fatal(ex, exc_info=True)

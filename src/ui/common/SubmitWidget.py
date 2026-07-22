from PyQt5.QtCore import QEventLoop, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication

from src.core import PathHelper, ConfigModelBase

from src.common import Consts
from src.ui.logger import LoggerDialog
from src.ui.threading import Worker


class SubmitWidget(QWidget):
    show_modal = pyqtSignal(object)
    on_save_signal = pyqtSignal()

    def __init__(
        self,
        config: ConfigModelBase,
        config_callback,
        on_run_click,
        run_button_text="Run",
        overwrite_btn_text="Overwrite settings",
    ):
        super().__init__()
        self.worker = None
        self.config = config
        self.config_original_path = config.path()
        self.config_callback = config_callback
        self.on_run_click = on_run_click
        self.temp_config_path = PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, f"/ui/temp/{config.module_name}/config.json"
        )

        if on_run_click != None:
            self.run_button = QPushButton(run_button_text)
            self.run_button.setMinimumWidth(250)
            self.run_button.clicked.connect(self.on_run_button_click)

        self.overwrite_button = QPushButton(overwrite_btn_text)
        self.overwrite_button.setMinimumWidth(250)
        self.overwrite_button.setEnabled(False)
        self.overwrite_button.clicked.connect(
            lambda: self.on_overwrite_button_click(self.overwrite_button)
        )

        self.changed_objects = []

        self.on_form_change = self._on_form_change

        layoutH_submit = QHBoxLayout()
        if on_run_click != None:
            layoutH_submit.addWidget(self.run_button)
        layoutH_submit.addWidget(self.overwrite_button)

        self.dialog = LoggerDialog(
            title=f"Logs - {config.config_prop_name}", name=config.config_prop_name
        )
        self.dialog.cancel_task.connect(lambda: self.cancel_task())
        layoutV = QVBoxLayout()
        layoutV.addLayout(layoutH_submit)
        self.setLayout(layoutV)

    def _on_form_change(self, obj, is_changed):
        if is_changed:
            self.changed_objects.append(obj)
        else:
            if obj in self.changed_objects:
                self.changed_objects.remove(obj)
        if len(self.changed_objects):
            self.overwrite_button.setEnabled(True)
        else:
            self.overwrite_button.setEnabled(False)

    def generate_config(self):
        from pathlib import Path
        import json
        from dataclasses import asdict
        from src.core import write_data, AccessType

        path = Path(self.config_original_path)
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)

        new_config = self.config_callback()
        config = {
            **asdict(self.config),
            **asdict(new_config),
        }  # override ole with new and leave not assigned

        data[self.config.config_prop_name] = config

        data = json.dumps(data, indent=4)
        write_data(self.temp_config_path, data, access_type=AccessType.Write)

    def on_run_button_click(self):
        self.dialog.show_cancel_modal = True
        self.run_button.setEnabled(False)
        self.dialog.show()

        QApplication.processEvents(QEventLoop.AllEvents)
        self.generate_config()

        self.worker = Worker(
            task=self.on_run_click,
            config=self.config,
            temp_config_path=self.temp_config_path,
        )
        self.worker.on_task_finished.connect(lambda: self.on_task_finished())
        self.worker.start()

    def on_task_finished(self):
        self.dialog.show_cancel_modal = False
        self.run_button.setEnabled(True)

    def cancel_task(self):
        self.worker.stop()

    def on_overwrite_button_click(self, button):
        import shutil

        self.generate_config()
        shutil.copyfile(self.temp_config_path, self.config_original_path)
        button.setEnabled(False)
        self.on_save_signal.emit()

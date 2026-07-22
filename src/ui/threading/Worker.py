import logging
import logging.handlers
import pickle
import queue
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal

import multiprocessing as mp
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from src.common import override_config
from src.core.plots.plotting_utils import set_plot_dispatch


def subprocess_wrapper(task, config, log_q, plot_q, lock_q, *args, **kwargs):
    import matplotlib

    matplotlib.use(
        "Agg", force=True
    )  # subprocess has issues with plotting in child threads
    type(config).path = staticmethod(lambda: kwargs["temp_config_path"])
    root = logging.getLogger()
    root.handlers[:] = [logging.handlers.QueueHandler(log_q)]
    root.filters[:] = []
    override_config()
    try:
        set_plot_dispatch(plot_queue=plot_q, lock_queue=lock_q)
        task()
    except Exception as e:
        logging.exception(e)
        raise
    root.info("Process finished with exit code 0")


class Worker(QObject):
    on_task_finished = pyqtSignal(bool)

    def __init__(self, task, config, temp_config_path):
        super().__init__()
        self.task = task
        self.config = config
        self.process = None
        self.temp_config_path = temp_config_path

        self.ctx = mp.get_context("spawn")
        self.log_q = self.ctx.Queue()
        self.plot_q = self.ctx.Queue()
        self.lock_q = self.ctx.Queue()

        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.handle_logging)
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.handle_plotting)

        self.monitor_times = QTimer()
        self.monitor_times.timeout.connect(self.check_process)
        self.monitor_times.start(500)

        self.plot_window = PlotWindow(on_close_callback=lambda: self.lock_q.put("ok"))

    def start(self):
        self.process = self.ctx.Process(
            target=subprocess_wrapper,
            args=(self.task, self.config, self.log_q, self.plot_q, self.lock_q),
            kwargs={"temp_config_path": self.temp_config_path},
            daemon=False,
        )
        self.process.start()
        self.log_timer.start(50)  # ms
        self.plot_timer.start(100)

    def kill(self):
        self.log_timer.stop()
        self.plot_timer.stop()
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(2)

    def stop(self):
        self.kill()
        self.handle_logging()

    def handle_logging(self):
        try:
            while True:
                rec = self.log_q.get_nowait()
                logging.getLogger(self.config.config_prop_name).handle(rec)
        except queue.Empty:
            pass

        if self.process and not self.process.is_alive():
            code = self.process.exitcode
            if code not in (None, 0):
                logging.getLogger(self.config.config_prop_name).error(
                    "Process finished with exit code %s", code
                )
                self.kill()

    def handle_plotting(self):
        while not self.plot_q.empty():
            msg_type, raw = self.plot_q.get_nowait()
            if msg_type == "figure":
                fig = pickle.loads(raw)

                self.plot_window.show_figure(fig)

        if self.process is not None and not self.process.is_alive():
            self.plot_timer.stop()

    def check_process(self):
        if not self.process.is_alive():
            self.monitor_times.stop()
            self.on_task_finished.emit(True)


class PlotWindow(QWidget):
    def __init__(self, on_close_callback):
        super().__init__()
        original_close = self.closeEvent

        def on_close(event):
            on_close_callback()
            original_close(event)

        self.closeEvent = on_close

        self.canvas = FigureCanvasQTAgg()
        layout = QVBoxLayout(self)
        toolbar = NavigationToolbar2QT(self.canvas, self)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

    def set_window_title(self, fig):
        self.setWindowTitle(
            fig._suptitle.get_text()
            if fig._suptitle
            else fig.axes[0].get_title() if fig.axes else "Plot"
        )

    def show_figure(self, fig):
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.set_window_title(fig)
        self.canvas.draw()
        self.show()

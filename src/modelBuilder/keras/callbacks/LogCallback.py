import logging
import numbers
import tensorflow as tf


class LogCallback(tf.keras.callbacks.Callback):
    DEFAULT_SAMPLES_INTERVAL = 10_000

    def __init__(
        self,
        batch_size=None,
        epochs=None,
        total_samples=None,
        log_every_n_samples=DEFAULT_SAMPLES_INTERVAL,
    ):
        self.n = log_every_n_samples
        self.processed_samples_count = 0
        self.progress_to_show_count = log_every_n_samples
        self.batch_size = batch_size
        self.epochs = epochs
        self.total_samples = total_samples

    @staticmethod
    def format_keras_log(logs):
        logs = logs or {}
        return " ".join(
            (
                f"{k}={float(v):.4f}"
                if isinstance(v, numbers.Real) and not isinstance(v, bool)
                else f"{k}={v}"
            )
            for k, v in logs.items()
            if v is not None
        )

    def on_train_batch_end(self, b, logs=None):
        self.processed_samples_count += self.batch_size
        if self.processed_samples_count >= self.progress_to_show_count:
            logging.info(
                f"samples={self.processed_samples_count}/{self.total_samples} {LogCallback.format_keras_log(logs)}"
            )
            self.progress_to_show_count += self.n

    def on_epoch_begin(self, epoch, logs=None):
        epoch = epoch + 1
        logging.info(f"--------------------------------------------")
        logging.info(f"Epoch {epoch}/{self.epochs}")

    def on_epoch_end(self, epoch, logs=None):
        epoch = epoch + 1
        logging.info(
            f"{epoch}/{self.epochs} FINISHED - {LogCallback.format_keras_log(logs)}"
        )
        self.processed_samples_count = 0
        self.progress_to_show_count = self.n

    def on_predict_begin(self, logs=None):
        logging.info("Model predicting started")

    def on_predict_end(self, logs=None):
        logging.info("Model predicting finished")

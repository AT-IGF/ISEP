import os
import sys
import logging

from src.core.configurations import ConfigModelBase
from src.core import PathHelper, Logger

from src.common import Consts

LEVEL_0 = "0"  # = all messages are logged (default behavior)
LEVEL_1 = "1"  # = INFO messages are not printed
LEVEL_2 = "2"  # = INFO and WARNING messages are not printed
LEVEL_3 = "3"  # = INFO, WARNING, and ERROR messages are not printed


def set_tf_settings(
    module_name: str, tf_log_level=LEVEL_2, app_log_level=logging.INFO, **kwargs
):
    setup_environmental_variables(tf_log_level)
    setup_logger(module_name, app_log_level, **kwargs)
    log_tensorflow_info()


def setup_environmental_variables(level=LEVEL_2):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = level
    os.environ["XLA_FLAGS"] = f"--xla_gpu_cuda_data_dir={Consts.CUDA_PATH}"
    os.environ["MPLBACKEND"] = f"TkAgg"


def log_tensorflow_info():
    import tensorflow as tf
    patch_keras_signbit()
    from tensorflow.python.platform import build_info

    logger = logging.getLogger()
    logger.info(f"Tensorflow version='{tf.__version__}'. (Implemented in 2.16.1)")
    logger.info(f"is_gpu_available: {tf.config.list_physical_devices('GPU')}")
    cuda_v = None
    warning = ""
    if "cuda_version" in build_info.build_info:
        cuda_v = build_info.build_info["cuda_version"]
    else:
        warning = ". Model training performance may suffer."
    logger.info(
        f"is_built_with_cuda={tf.test.is_built_with_cuda()} (v{cuda_v}){warning}"
    )
    tf.get_logger().addHandler(logger)
    tf.get_logger().setLevel(logging.INFO)


def setup_logger(module_name: str, logging_level=logging.INFO, **kwargs):
    if (
        module_name in logging.Logger.manager.loggerDict
        or "root" in logging.Logger.manager.loggerDict
    ):
        return
    from src.common.config import Config

    Logger.CreateLoggerFromPath(
        PathHelper.join_rel_path(Consts.RESOURCES_PATH, f"{module_name}/logs")
    )
    logger = logging.getLogger(module_name)
    if logging_level is str:
        logging_level = str(logging_level).upper()
    logger.setLevel(level=logging_level)
    logger.name = module_name
    logger.info(f"Python version='{sys.version}'. (Implemented in 3.11.4)")
    logger.info(f"Current Python interpreter path: '{sys.executable}'")
    logger.info(
        f"Configs cache on save is {'' if Config.config_base.invalidate_cache_on_save else 'NOT'} invalidated"
    )


def setup_module_logger(module_name):
    Logger.CreateLoggerFromPath(
        PathHelper.join_rel_path(Consts.RESOURCES_PATH, f"{module_name}/logs"),
        logger_name=module_name,
    )


def patch_keras_signbit():
    """Patches Keras signbit overflow bug on Windows (0x80000000 > C long max)."""
    import platform
    if platform.system() != "Windows":
        return

    try:
        from keras.src.backend.tensorflow import numpy as knp
        import tensorflow as tf

        original = knp.signbit

        def patched(x):
            bits = tf.bitwise.bitwise_and(
                tf.bitcast(tf.cast(x, tf.float32), tf.int32),
                tf.constant(-2147483648, dtype=tf.int32),  # tf.int32.min
            )
            return tf.not_equal(bits, 0)

        knp.signbit = patched
        logging.getLogger().info("Keras signbit patched for Windows")
    except Exception as e:
        logging.getLogger().warning(f"Failed to patch Keras signbit: {e}")
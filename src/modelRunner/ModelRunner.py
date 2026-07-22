from src.common.config import Config, ModelRunnerConfig
from src.common.tensorflow.Settings import set_tf_settings
from src.modelRunner.dataProcessor.progressHandler import ProgressHandler


import logging
from src.modelRunner.summaries.models import ParticlesCountModel
from src.modelRunner.dataProcessor import DataProcessor
from src.modelRunner.predictions import KerasPredictor, Prediction
from src.modelRunner.summaries import (
    ParticlesCountSummary,
    ParticlesCountSummary,
    PredictionSummary,
    PredictionWithThresholdSummary,
)

from src.core import PathHelper

from src.common.rawData import get_raw_data_list_multithread

from src.common import Consts
from src.common.filters.ExternalRunner import get_filter


def should_append_unlabeled_wrapper(callback):
    should_append_unlabeled_wrapper.counter += 1
    return callback


should_append_unlabeled_wrapper.counter = 0


def handle(**kwargs):
    set_tf_settings(
        module_name=ModelRunnerConfig.module_name,
        app_log_level=Config.get(ModelRunnerConfig).log_level,
    )
    logger = logging.getLogger(ModelRunnerConfig.config_prop_name)
    logging.getLogger().info("Started - model runner")
    config = Config.get(ModelRunnerConfig).log_info()
    predictor = KerasPredictor(
        model_path=PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            config.model_rel_path,
            raise_message="Model to run path has to be set",
        ),
        classes=config.pollen_types,
    )
    logger.warning("Data normalization is hardcoded")

    progress_handler = ProgressHandler()
    data_processor = DataProcessor(progress_handler)
    particlesCountSummary = ParticlesCountSummary(threshold=config.get_threshold())
    total_count = 0
    add_file_header = True

    filter_callback = get_filter(config.filter_rel_path)
    if config.filter_rel_path == None:
        logger.warning("No particles filter found all particles will be processed")
    else:
        logger.info(
            f"Data filter found and will be used for particles filtering, path={config.filter_rel_path}"
        )

    for idx, files_to_process in enumerate(
        data_processor.get_files_to_predict(every_nth_file=None)
    ):
        logging.getLogger().info(
            f"Processing date = {files_to_process.date} ({idx + 1}/{progress_handler.dates_to_process_count})"
        )
        data_processor.handle_combined_file_processing(idx, files_to_process)
        predictionSummary = PredictionSummary(files_to_process=files_to_process)
        predictionWithThresholdSummary = PredictionWithThresholdSummary(
            files_to_process=files_to_process, threshold=config.get_threshold()
        )

        # return allow_raw_wrap(*args, **kwargs) # raw_data
        default_callback = True
        callback = should_append_unlabeled_wrapper(
            callback=filter_callback
        )  # common_filter3 - best acc
        if default_callback == False:
            input("Filtering method updated?")

        files_count_left = len(files_to_process.files)
        for raw_data_set, processed_files in get_raw_data_list_multithread(
            files=files_to_process.files,
            batch_size=10000,
            should_append_callback=callback,
        ):
            if len(raw_data_set):
                logger.info("Set empty skipping.")

            y_preds: list[Prediction] = predictor.predict(raw_data_set=raw_data_set)

            predictionSummary.on_measurement(y_preds, add_file_header=add_file_header)
            add_file_header = False
            predictionWithThresholdSummary.on_measurement(y_preds)
            total_count += len(raw_data_set)
            particlesCountSummary.on_measurement(
                model=ParticlesCountModel(
                    with_threshold_count=predictionWithThresholdSummary.y_preds_tr_count,
                    no_threshold_count=predictionSummary.y_preds_count,
                    total_count=total_count,
                )
            )

            progress_handler.save_progress(
                files_to_process=files_to_process, processed_files=processed_files
            )
            files_count_left -= len(processed_files)
            if files_count_left < 0:
                raise ValueError(
                    f"files_count_left is below 0, which should not occur, files_count_left={files_count_left}"
                )
            if files_count_left == 0:
                break
        predictionWithThresholdSummary.summary()

    particlesCountSummary.summary()
    logging.getLogger().info("Finished - model runner")


if __name__ == "__main__":
    handle()

from typing import Any
from src.helpers.PlotHelper import should_be_displayed
from src.common.config.configs.models.predictionsMapper.ThresholdsModel import (
    ThresholdsModel,
)
from src.predictionsMapper.plots.PlotPlot import PlotPlot
from src.predictionsMapper.plots.BarPlot import BarPlot
from src.predictionsMapper.plots.GridBarPlot import GridBarPlot
from src.common.config import Config, PredictionsMapperConfig
from src.common.predictions.Thresholds import is_any_pred_within_threshold
from src.common.tensorflow.Settings import setup_logger

import logging
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from src.common.pandas.DataFrameHelper import write_data_frame_to_csv
from src.common.predictions.ClassesMapper import to_argmax
from src.common import Consts
from src.core import File, PathHelper, AccessType
from src.predictionsMapper.common.Consts import (
    TIMESTAMP_INDEX,
    FROM_TIME_KEY,
    TO_TIME_KEY,
    TIME_FORMAT,
)


def get_particles_predictions(config: PredictionsMapperConfig, file: File):
    parse_dates = [config.split_timespan.timestamp_column_name]

    logging.getLogger().info(f"Processing file={config.file_to_process_rel_path}")

    if config.preview.is_row_skipping_enabled():
        logging.getLogger().warning(
            f"Measurements skipping enabled. Every n-th row will be skipped. n-th_row={config.preview.keep_every_nth_row}"
        )

    df = pd.read_csv(
        file.get_file_path(),
        skiprows=(
            None
            if not config.preview.is_row_skipping_enabled()
            else lambda i: i > 0 and i % config.preview.get_keep_every_nth_row() != 0
        ),
    )
    for parse_date in parse_dates:
        converted = pd.to_datetime(df[parse_date], errors='coerce')
        bad = converted.isna()
        if bad.any():
            logging.getLogger().warning(f"{parse_date} column: dropped {bad.sum()} row(s) with invalid timestamps. Line indexes={df.index[bad].tolist()}")
        df[parse_date] = converted
        df = df[~bad]

    for col in df.columns:
        if col not in parse_dates and df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass 
        
    return df


def validate_columns(columns: list[str], thresholds: ThresholdsModel):
    if thresholds.is_class_threshold():
        column_types = list(columns)[:]
        column_types_original = list(columns)[:]
        del column_types[TIMESTAMP_INDEX]
        del column_types_original[TIMESTAMP_INDEX]
        for tr_type in thresholds.get_thresholds().keys():
            if tr_type not in column_types:
                raise ValueError(
                    f"Threshold column not found file to process columns. threshold_column={tr_type}, column_types={column_types_original}"
                )
            column_types.remove(tr_type)
        if len(column_types) > 0:
            missing_types = ", ".join(column_types)
            raise ValueError(
                "All thresholds in 'thresholds.types' must have its equivalent in columns "
                "or set common threshold by setting thresholds.threshold_type to 'COMMON_THRESHOLD'."
                f" Missing thresholds for types=[{missing_types}]"
            )


def is_within_class_threshold(columns, tr_by_types: dict, row_measurements):
    max_idx = np.array(row_measurements).argmax(axis=0)
    type_tr = tr_by_types[columns[max_idx + 1]]
    meas_max_tr = row_measurements[max_idx]

    return meas_max_tr >= type_tr


def get_threshold_particles_between_timespan(
    data_frame: pd.DataFrame, config: PredictionsMapperConfig
) -> list[list[Any]]:
    """Summed particles count between specified time interval with given thresold
    Returns:
        list[list[Any]]: [["from [datetime]", "to [datetime]", "particle_type1_sum [int]", "particleType2_sum [int]", ...]]
    """
    frame_max_time = datetime.min
    frames_by_span = []
    frames = []
    from_time = datetime.min
    to_time = datetime.min

    initial_count = len(data_frame)
    data_frame = data_frame.drop_duplicates(
        subset=[config.split_timespan.timestamp_column_name]
    )
    final_count = len(data_frame)
    removed_rows = initial_count - final_count
    frame = []
    frame_sum=[]
    if removed_rows > 0:
        logging.getLogger().info(
            f"Duplicated datatimes found and removed. Duplicated rows count={removed_rows}"
        )

    for idx, row in enumerate(
        data_frame.sort_values(config.split_timespan.timestamp_column_name).values
    ):
        try:
            measurement_time: datetime = pd.Timestamp.to_pydatetime(
                row[TIMESTAMP_INDEX]
            )
            if config.split_timespan.is_below_from_range(
                value=measurement_time
            ) or config.split_timespan.is_above_to_range(value=measurement_time):
                continue
            row_measurements = np.delete(row, TIMESTAMP_INDEX)
            if config.thresholds.is_class_threshold():
                if not is_within_class_threshold(
                    data_frame.columns,
                    config.thresholds.get_thresholds(),
                    row_measurements,
                ):
                    continue
            else:
                if not is_any_pred_within_threshold(
                    row_measurements, config.thresholds.threshold
                ):
                    continue
            row_measurements = to_argmax(row_measurements)
            if measurement_time < frame_max_time:
                frames.append(row_measurements)
            else:
                if frame_max_time != datetime.min:
                    to_time = measurement_time
                    frame_sum = np.sum(frames, axis=0).tolist()
                    frame = [from_time, to_time] + frame_sum
                    frames_by_span.append(frame)
                frames = [row_measurements]
                from_time = measurement_time
                frame_max_time = measurement_time + timedelta(
                    days=config.split_timespan.days,
                    minutes=config.split_timespan.minutes,
                    hours=config.split_timespan.hours,
                    seconds=config.split_timespan.seconds,
                )
        except Exception as e:
            logging.getLogger().error(f"Error in row={idx} occurred; check it may contain corrupted data. error={e}")
            raise e
    
    # add last frame  
    if len(frame) != 0:
        to_time = measurement_time
        frame_sum = np.sum(frames, axis=0).tolist()
        frame = [from_time, to_time] + frame_sum
        frames_by_span.append(frame)

    return frames_by_span


def plot_summary(config: PredictionsMapperConfig, frame_summary: pd.DataFrame):
    logger = logging.getLogger()
    if config.plot_settings.plot_style is None:
        logger.info("Showing plot is disabled add 'plot' section in configuration")
        return

    plt.rcParams.update({"font.size": 20})
    plot_settings = config.plot_settings
    if plot_settings.plot_style == plot_settings.BAR_STYLE_PLOT:
        if plot_settings.bar_plot_settings.display_as_grid:
            grid_bar_plot = GridBarPlot(config=config)
            grid_bar_plot.show(frame_summary)
        else:
            grid_bar_plot = BarPlot(config=config)
            grid_bar_plot.show(frame_summary)
    else:
        grid_bar_plot = PlotPlot(config=config)
        grid_bar_plot.show(frame_summary)


def handle():
    setup_logger(module_name=PredictionsMapperConfig.config_prop_name)
    logger = logging.getLogger()

    logger.info("Sterted - predictions mapper")
    config = Config.get(PredictionsMapperConfig)
    logger.info(
        f"Detecting particles with threshold={config.thresholds.get_threshold()}"
    )

    predictions_file: File = File(path=config.get_file_to_process_path())
    predictions_df: pd.DataFrame = get_particles_predictions(config, predictions_file)
    validate_columns(predictions_df.columns, config.thresholds)
    if config.split_timespan.is_range_set():
        logger.warning(
            f"Processed measurements are constrained between range: from='{config.split_timespan.range_from_text()}', to='{config.split_timespan.range_to_text()}'"
        )
    frames_by_span: pd.DataFrame = get_threshold_particles_between_timespan(
        predictions_df, config
    )

    if len(frames_by_span) == 0:
        logger.info(
            f"No particles found with given threshold={config.thresholds.threshold}"
        )
        logger.info("Finished - predictions mapper")
        return

    summary_columns = [FROM_TIME_KEY, TO_TIME_KEY] + np.delete(
        predictions_df.columns, TIMESTAMP_INDEX
    ).tolist()
    frame_summary = pd.DataFrame(frames_by_span, columns=summary_columns)
    write_data_frame_to_csv(
        path=PathHelper.join_rel_path(
            Consts.RESOURCES_PATH,
            config.save_path_rel_path,
            f"tr_{config.thresholds.threshold}_of_{predictions_file.get_file_name_no_extension()}",
        ),
        data=frame_summary,
        access_type=AccessType.Write,
    )

    measurement_start = frame_summary[FROM_TIME_KEY].iloc[0]
    measurement_end = frame_summary[TO_TIME_KEY].iloc[-1]
    days = (measurement_end - measurement_start).days
    logger.info(
        f"Detected particles count = {frame_summary.drop(columns=[FROM_TIME_KEY, TO_TIME_KEY]).sum().sum()}"
    )
    logger.info(
        f"Timespan: {days} day(s), from={measurement_start.strftime(TIME_FORMAT)}, to={measurement_end.strftime(TIME_FORMAT)}"
    )
    logger.info(
        f"Total: \n{frame_summary.drop(columns=[FROM_TIME_KEY, TO_TIME_KEY]).sum().to_frame().transpose()}"
    )

    plot_summary(config, frame_summary)

    logger.info("Finished - predictions mapper")


if __name__ == "__main__":
    matplotlib.use("TkAgg")  # Use a non-GUI backend (good for servers)
    handle()

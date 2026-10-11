from pathlib import Path

import pandas as pd
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig, ModelRunnerConfig, ModelBuilderScalerConfig, PredictionsMapperConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool

def test_handle_when_run_runs_predictions_mapping(monkeypatch, test_resources):
    # arrange
    output_plot = test_resources /  "plots" / "show_1.png"
    output_file_1 = test_resources /  "predictionsMapper"/ "out" / "tr_0.2_of_tr_0_to_predict.csv"
    
    expected = pd.DataFrame([
    {
        "from": "2020-06-15 11:16:00.960",
        "to": "2020-06-22 11:16:00.960",
        "Alnus": 9,
        "ArrhinateRum": 77,
    }
    ])


    model_builder_config = ModelBuilderConfig()
    model_builder_config.run_training = True
    model_builder_config.binary_paths = (
        Path(__file__).resolve().parent.parent
        / "resources"
        / "binary_paths"
    )
    
    monkeypatch.setattr(
        Consts,
        "RESOURCES_PATH",
        str(test_resources)
    )
    
    types_config = TypesConfig()
    types_config.pollen_types = ["Alnus", "ArrhinateRum"]
    paths_config = PathsConfig()
    paths_config.zip_files_rel_path = "binary_paths"
    model_builder_unsup_config = ModelBuilderUnsupervisedConfig()
    model_builder_scaler_config = ModelBuilderScalerConfig()
    model_runner_config = ModelRunnerConfig()
    predictions_mapper_config = PredictionsMapperConfig()
    predictions_mapper_config.file_to_process_rel_path = str(test_resources / "modelRunner" / "out" / "tr_0_to_predict.csv")
    predictions_mapper_config.pollen_types = ["Alnus", "ArrhinateRum"]
    predictions_mapper_config.thresholds.threshold = 0.2
    predictions_mapper_config.plot_settings.bar_plot_settings.is_months_of_expectance = True
    predictions_mapper_config.plot_settings.bar_plot_settings.months_of_expectance_mapping_path = str(test_resources / "common" / "months_of_expectance" / "test.json")
    predictions_mapper_config.plot_settings.bar_plot_settings.display_as_grid = True
    
    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config
        
        if config is ModelBuilderScalerConfig:
            return model_builder_scaler_config
        
        if config is ModelRunnerConfig:
            return model_runner_config
        
        if config is PredictionsMapperConfig:
            return predictions_mapper_config

        raise ValueError(f"Unexpected config: {config}")

    monkeypatch.setattr(
        Config,
        "get",
        staticmethod(fake_get)
    )

    from src.common.rawData import RawDataHanlder
    monkeypatch.setattr(
        RawDataHanlder.multiprocessing,
        "Pool",
        SequentialPool
    )
    
    # act
    from src.predictionsMapper import PredictionsMapper
    PredictionsMapper.handle()

    # assert
    actual = pd.read_csv(output_file_1)
    pd.testing.assert_frame_equal(actual, expected)
    assert output_plot.is_file(), f"Runner output plot was not created: {output_plot}"
    
 
def test_handle_when_run_and_time_frame_as_one_day_runs_predictions_mapping(monkeypatch, test_resources):
    # arrange
    output_plot = test_resources /  "plots" / "show_1.png"
    output_file_1 = test_resources /  "predictionsMapper"/ "out" / "tr_0.2_of_tr_0_to_predict.csv"
    
    expected = pd.DataFrame([
        {
            "from": "2020-06-15 11:16:00.960",
            "to": "2020-06-16 08:50:02.586",
            "Alnus": 7,
            "ArrhinateRum": 32,
        },
        {
            "from": "2020-06-16 08:50:02.586",
            "to": "2020-06-16 08:51:00.890",
            "Alnus": 2,
            "ArrhinateRum": 45,
        },
    ])


    model_builder_config = ModelBuilderConfig()
    model_builder_config.run_training = True
    model_builder_config.binary_paths = (
        Path(__file__).resolve().parent.parent
        / "resources"
        / "binary_paths"
    )
    
    monkeypatch.setattr(
        Consts,
        "RESOURCES_PATH",
        str(test_resources)
    )
    
    types_config = TypesConfig()
    types_config.pollen_types = ["Alnus", "ArrhinateRum"]
    paths_config = PathsConfig()
    paths_config.zip_files_rel_path = "binary_paths"
    model_builder_unsup_config = ModelBuilderUnsupervisedConfig()
    model_builder_scaler_config = ModelBuilderScalerConfig()
    model_runner_config = ModelRunnerConfig()
    predictions_mapper_config = PredictionsMapperConfig()
    predictions_mapper_config.file_to_process_rel_path = str(test_resources / "modelRunner" / "out" / "tr_0_to_predict.csv")
    predictions_mapper_config.pollen_types = ["Alnus", "ArrhinateRum"]
    predictions_mapper_config.thresholds.threshold = 0.2
    predictions_mapper_config.plot_settings.plot_style= "LINE_STYLE_PLOT"
    predictions_mapper_config.split_timespan.days = 0
    predictions_mapper_config.split_timespan.hours = 1
    
    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config
        
        if config is ModelBuilderScalerConfig:
            return model_builder_scaler_config
        
        if config is ModelRunnerConfig:
            return model_runner_config
        
        if config is PredictionsMapperConfig:
            return predictions_mapper_config

        raise ValueError(f"Unexpected config: {config}")

    monkeypatch.setattr(
        Config,
        "get",
        staticmethod(fake_get)
    )

    from src.common.rawData import RawDataHanlder
    monkeypatch.setattr(
        RawDataHanlder.multiprocessing,
        "Pool",
        SequentialPool
    )
    
    # act
    from src.predictionsMapper import PredictionsMapper
    PredictionsMapper.handle()

    # assert
    actual = pd.read_csv(output_file_1)
    pd.testing.assert_frame_equal(actual, expected)
    assert output_plot.is_file(), f"Runner output plot was not created: {output_plot}"
    
 
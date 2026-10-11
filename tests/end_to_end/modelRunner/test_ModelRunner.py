from pathlib import Path
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig, ModelRunnerConfig, ModelBuilderScalerConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool


def test_handle_when_run_runs_model_prediction(monkeypatch, test_resources):
    # arrange
    output_file = test_resources /  "modelRunner"/ "out" / "tr_0_combined_files.csv"
    processed_files_file_path = test_resources /  "modelRunner"/ "out" / "processed" / "PROCESSED_combined_files.txt"
    summary_file_path = test_resources /  "modelRunner"/ "out" / "processed" / "SUMMARY_combined_files_tr_0.2_1.csv"
    
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
    model_runner_config.model_rel_path = str(test_resources / "modelBuilder" / "supervised_tests_model.h5")
    model_runner_config.scaler_path =  str(test_resources / "scaler1_scaler.pkl")
    model_runner_config.pollen_types =  ["Alnus", "ArrhinateRum"]
    model_runner_config.types_to_predict_rel_dirs = ["binary_paths"]
    model_runner_config.processing.combined_files_filename = "combined_files"
    
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
    from src.modelRunner import ModelRunner
    ModelRunner.handle()

    # assert
    assert output_file.is_file(), f"Runner output file was not created: {output_file}"
    assert processed_files_file_path.is_file(), f"Processed files file was not created: {processed_files_file_path}"
    assert summary_file_path.is_file(), f"Summary file was not created: {summary_file_path}"
 
def test_handle_when_run_and_save_in_separate_files_runs_model_prediction(monkeypatch, test_resources):
    # arrange
    output_file_1 = test_resources /  "modelRunner"/ "out" / "tr_0_20200615.csv"
    output_file_2 = test_resources /  "modelRunner"/ "out" / "tr_0_20200616.csv"
    processed_files_file_path_1 = test_resources /  "modelRunner"/ "out" / "processed" / "PROCESSED_20200615.txt"
    processed_files_file_path_2 = test_resources /  "modelRunner"/ "out" / "processed" / "PROCESSED_20200616.txt"
    summary_file_path = test_resources /  "modelRunner"/ "out" / "processed" / "SUMMARY_None_tr_0.2_1.csv"
    
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
    model_runner_config.model_rel_path = str(test_resources / "modelBuilder" / "supervised_tests_model.h5")
    model_runner_config.scaler_path =  str(test_resources / "scaler1_scaler.pkl")
    model_runner_config.pollen_types =  ["Alnus", "ArrhinateRum"]
    model_runner_config.types_to_predict_rel_dirs = ["binary_paths"]
    model_runner_config.processing.combined_files_filename = None
    
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
    from src.modelRunner import ModelRunner
    ModelRunner.handle()

    # assert
    assert output_file_1.is_file(), f"Runner output file was not created: {output_file_1}"
    assert output_file_2.is_file(), f"Runner output file was not created: {output_file_2}"
    assert processed_files_file_path_1.is_file(), f"Processed files file was not created: {processed_files_file_path_1}"
    assert processed_files_file_path_2.is_file(), f"Processed files file was not created: {processed_files_file_path_2}"
    assert summary_file_path.is_file(), f"Summary file was not created: {summary_file_path}"
 
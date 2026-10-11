from pathlib import Path
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig, DataViewerConfig, ModelBuilderScalerConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool


def test_handle_when_run_scaler_runs_scaler(monkeypatch, test_resources):
    # arrange
    scaler_path = test_resources /  "modelBuilder"/ "scaler" / "raw" / "scaler1_scaler.pkl"
    scaler_progress_path = test_resources /  "modelBuilder"/ "scaler" / "raw" / "scaler1_scaler_PROGRESS.txt"
    
    model_builder_config = ModelBuilderConfig()
    model_builder_config.run_training = True
    model_builder_config.scaler_path =  "scaler1_scaler.pkl"
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
    model_builder_scaler_config.pollen_types_binaries_paths = [str(test_resources / "binary_paths")]

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
    from src.modelBuilder import ModelBuilderDataScaler
    ModelBuilderDataScaler.handle()

    # assert
    assert scaler_path.is_file(), f"Scaler was not created: {scaler_path}"
    assert scaler_progress_path.is_file(), f"Scaler progress file was not created: {scaler_progress_path}"
 
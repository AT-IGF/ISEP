from pathlib import Path

import pandas as pd
import pytest
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig, ModelRunnerConfig, ModelBuilderScalerConfig, PredictionsMapperConfig, AllParticlesAvgsConfig, DataViewerConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool
from src.common.tensorflow import InputModelNames


def test_handle_when_run_displays_aggregated_summaries(monkeypatch, test_resources):
    # arrange
    plots_path = test_resources / "dataViewer" / "out"
    expected_plots = {'scattering/ArrhinateRum0.png', 'spectrometer/ArrhinateRum1.png', 'scattering/Alnus2.png', 'lifetime/ArrhinateRum0.png', 'lifetime/ArrhinateRum1.png', 'lifetime/Alnus2.png', 'spectrometer/ArrhinateRum0.png', 'scattering/ArrhinateRum1.png', 'scattering/Alnus3.png', 'lifetime/Alnus3.png', 'spectrometer/Alnus3.png', 'spectrometer/Alnus2.png'}

    model_builder_config = ModelBuilderConfig()

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
    all_particles_avgs_config = AllParticlesAvgsConfig()
    data_viewer_config = DataViewerConfig()
    data_viewer_config.pollen_types_to_show = ["Alnus", "ArrhinateRum"]
    data_viewer_config.spectrum_plot.show = True
    data_viewer_config.lifetime_plot.show = True
    data_viewer_config.scattering_plot.show = True
    
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
        
        if config is AllParticlesAvgsConfig:
            return all_particles_avgs_config
        
        if config is DataViewerConfig:
            return data_viewer_config

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
    from src.dataViewer import DataViewer
    DataViewer.handle()

    assert_files(plots_path, expected_plots, "*.png")
     
def assert_files(path, expected_files, extension="*"):
    actual_files = {
        str(file.relative_to(path))
        for file in path.rglob("*")
        if file.is_file()
    }

    assert actual_files == set(expected_files)
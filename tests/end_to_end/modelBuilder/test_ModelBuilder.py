from pathlib import Path
import re

import pytest
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool

def test_handle_when_run_training_true_runs_training(monkeypatch, test_resources):
    # arrange
    model_path = test_resources / "modelBuilder" / "hello_world_model.h5"
    cache_path = test_resources / "supervised" / "cache"
    expected_files = [
        "hello_world_Alnus_test_reference_to_scale.tfrecord",
        "hello_world_Alnus_test.tfrecord",
        "hello_world_Alnus_train.tfrecord",
        "hello_world_Alnus_validation.tfrecord",

        "hello_world_ArrhinateRum_test_reference_to_scale.tfrecord",
        "hello_world_ArrhinateRum_test.tfrecord",
        "hello_world_ArrhinateRum_train.tfrecord",
        "hello_world_ArrhinateRum_validation.tfrecord",
    ]
    
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

    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config

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
    from src.modelBuilder import ModelBuilder
    ModelBuilder.handle()

    # assert
    assert model_path.is_file(), f"Model was not created: {model_path}"

    for filename in expected_files:
        path = cache_path / filename
        assert path.is_file(), f"Expected file was not created: {path}"
    
        
def test_handle_when_run_calibration_true_runs_calibration(monkeypatch, test_resources):
    # arrange
    model_path = test_resources / "modelBuilder" / "supervised_tests_model_calibrated.keras"
    
    plots_path = test_resources / "plots"
    expected_plots = {
        "plot_temp_changes_1.png",
        "plot_toplabel_reliability_1.png",
        *{f"plot_probability_distributions_{i}.png" for i in range(1, 3)}
    }

    model_builder_config = ModelBuilderConfig()
    model_builder_config.model_save_name = "supervised_tests"
    model_builder_config.test_model_name = "supervised_tests_test_model"
    model_builder_config.run_training = False
    model_builder_config.calibration.run_calibration = True
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

    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config

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
    from src.modelBuilder import ModelBuilder
    ModelBuilder.handle()

    # assert
    assert model_path.is_file(), f"Model was not created: {model_path}"
    
    actual_plots = {
        path.name
        for path in plots_path.glob("*.png")
    }
    assert actual_plots == expected_plots
    
    
        
def test_handle_when_run_validation_true_runs_validation(monkeypatch, test_resources, caplog):
    # arrange
    plots_path = test_resources / "plots"
    expected_plots = {
        "plot_confucion_matrix_1.png",
        "summary_1.png",
        *{f"multiclass_roc_auc_score_{i}.png" for i in range(1, 4)}
    }

    model_builder_config = ModelBuilderConfig()
    model_builder_config.model_save_name = "supervised_tests"
    model_builder_config.test_model_name = "supervised_tests_test_model"
    model_builder_config.run_training = False
    model_builder_config.calibration.run_calibration = False
    model_builder_config.summaries.run_summaries = True
    model_builder_config.summaries.evaluate = True
    model_builder_config.summaries.roc_curve = True
    model_builder_config.summaries.prec_recall_curve = True
    model_builder_config.summaries.f1_score = True
    model_builder_config.summaries.confusion_matrix = True
    model_builder_config.summaries.thresholds = [0.5, 0.95]
    model_builder_config.summaries.size_summary = True
    
    
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

    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config

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
    from src.modelBuilder import ModelBuilder
    ModelBuilder.handle()

    # assert
    precision = get_metric(caplog, "Precission")
    recall = get_metric(caplog, "Recall")
    f1 = get_metric(caplog, "F1")
    roc_auc = get_metric(caplog, "ROC AUC score")

    assert precision == pytest.approx(28.57, abs=0.5)
    assert recall == pytest.approx(50.00, abs=0.5)
    assert f1 == pytest.approx(36.36, abs=0.5)
    assert roc_auc == pytest.approx(60.42, abs=0.5)
    
    actual_plots = {
        path.name
        for path in plots_path.glob("*.png")
    }
    assert actual_plots == expected_plots
    
    
def get_metric(caplog, name):
    for record in caplog.records:
        match = re.search(
            rf"{re.escape(name)}:\s*([\d.]+)%",
            record.message
        )
        if match:
            return float(match.group(1))

    raise AssertionError(f"Metric not found: {name}")
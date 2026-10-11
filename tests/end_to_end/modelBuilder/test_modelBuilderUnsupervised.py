from pathlib import Path
import re
import time

import pytest
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig, DataViewerConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool

def test_handle_when_run_training_true_runs_training(monkeypatch, test_resources):
    # arrange
    model_path = test_resources / "modelBuilder" / "hello_unsupervised_world_model.h5"
    history_plot_path = test_resources / "modelBuilder" / "hello_unsupervised_world_model_history.pkl"
    history_plot_csv_path = test_resources / "modelBuilder" / "hello_unsupervised_world_model_history.pkl.csv"
    cache_path = test_resources / "modelBuilder" / "unsupervised"
    expected_files = [
        "KerasTrainer/hello_unsupervised_world/hello_unsupervised_world_epoch5_model_history.pkl",
        "KerasTrainer/hello_unsupervised_world/hello_unsupervised_world_epoch5_model.h5",
        "KerasTrainer/hello_unsupervised_world/hello_unsupervised_world_epoch10_model_history.pkl",
        "KerasTrainer/hello_unsupervised_world/hello_unsupervised_world_epoch10_model.h5",
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
    model_builder_unsup_config.train_parameters.pollen_types_binaries_paths = ["binary_paths"]
    model_builder_unsup_config.train_parameters.filter_rel_path = "common/filters/modality_filters.py"
    model_builder_unsup_config.train_parameters.scaler_path = "scaler1_scaler.pkl"
    model_builder_unsup_config.train_parameters.learningModels = ["spectrum_unsup", "lifetime_unsup", "scattering_unsup", "size"]
    model_builder_unsup_config.train_parameters.epochs = 10
    model_builder_unsup_config.train_parameters.train_model = True
    model_builder_unsup_config.verify_model.verify_model = False
    model_builder_unsup_config.cluster_parameters.run_clustering = False

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
    from src.modelBuilder import ModelBuilderUnsupervided
    ModelBuilderUnsupervided.handle()

    # assert
    assert model_path.is_file(), f"Model was not created: {model_path}"
    assert history_plot_path.is_file(), f"History plot was not created: {history_plot_path}"
    assert history_plot_csv_path.is_file(), f"History plot csv file was not created: {history_plot_csv_path}"
    
    for filename in expected_files:
        path = cache_path / filename
        assert path.is_file(), f"Expected file was not created: {path}"
 
def test_handle_when_run_validation_true_runs_validation(monkeypatch, test_resources):
    # arrange
    latent_vectors_path = test_resources / "unsupervised" / "latent_vectors" / "unsupervised_tests-_reg-2dirs_latent_vectors.h5"
    
    plots_path = test_resources / "plots"
    expected_plots = {
        "plot_embeddings_1.png",
        "show_history_plot_1.png",

        *{f"plot_lifetime_{i}.png" for i in range(1, 7)},
        *{f"plot_scattering_intensity_{i}.png" for i in range(1, 13)},
        *{f"plot_spectrum_{i}.png" for i in range(1, 7)},
    }

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
    
    data_viewer_config = DataViewerConfig()
    types_config = TypesConfig()
    types_config.pollen_types = ["Alnus", "ArrhinateRum"]
    paths_config = PathsConfig()
    paths_config.zip_files_rel_path = "binary_paths"
    model_builder_unsup_config = ModelBuilderUnsupervisedConfig()
    model_builder_unsup_config.train_parameters.pollen_types_binaries_paths = ["binary_paths"]
    model_builder_unsup_config.train_parameters.filter_rel_path = "common/filters/modality_filters.py"
    model_builder_unsup_config.train_parameters.scaler_path = "scaler1_scaler.pkl"
    model_builder_unsup_config.train_parameters.learningModels = ["spectrum_unsup", "lifetime_unsup", "scattering_unsup", "size"]
    model_builder_unsup_config.model_save_name = "unsupervised_tests"
    model_builder_unsup_config.train_parameters.train_model = False
    model_builder_unsup_config.verify_model.verify_model = True
    model_builder_unsup_config.cluster_parameters.run_clustering = False

    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config
        
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
    from src.modelBuilder import ModelBuilderUnsupervided
    ModelBuilderUnsupervided.handle()

    # assert
    assert latent_vectors_path.is_file(), f"Latent vectors file was not created: {latent_vectors_path}"
    
    actual_plots = {
        path.name
        for path in plots_path.glob("*.png")
    }
    assert actual_plots == expected_plots
    
@pytest.mark.forked 
def test_handle_when_run_clustering_true_runs_clustering(monkeypatch, test_resources):
     # arrange
     timestamp = 1791710450
     
     latent_vectors_path = test_resources / "unsupervised" / "latent_vectors" / "unsupervised_clustering_tests-_reg-2dirs_latent_vectors.h5"
     
     plots_path = test_resources / "plots"
     expected_plots = {
         "plot_hdbscan_1.png",
         *{f"plot_embeddings_{i}.png" for i in range(1, 3)},
     }
     
     umap_files_path = test_resources / "unsupervised" / "umap"
     umap_files = {
         f"{timestamp}_latent_id-l2_pre_norm-0_5sr-cosine_m-categorical_tm-euclidean_out_m-0tw-0_1md-1_sp-500n-3D-umap-embeddings.h5",
         f"{timestamp}_latent_id-l2_pre_norm-0_5sr-cosine_m-categorical_tm-euclidean_out_m-0tw-0_1md-1_sp-500n-3D-umap-plot.png",
         f"{timestamp}_latent_id-l2_pre_norm-0_5sr-cosine_m-categorical_tm-euclidean_out_m-0tw-0_1md-1_sp-500n-3D-umap.pk1"
     }
     
     hdbscan_files_path = test_resources / "unsupervised" / "hdbscan"
     hdbscan_files = {
         f"unsupervised_clustering_tests-{timestamp}_umap_id-pred-0.5sr-None_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscan_preds_lot.png",
         f"unsupervised_clustering_tests-{timestamp}_umap_id-pred-0.5sr-None_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscan.joblib",
         f"unsupervised_clustering_tests-{timestamp}_umap_id-pred-0.5sr-None_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscantrue.png"
     }
     
     mini_batch_kmeans_files_path = test_resources / "unsupervised" / "mini_batch_kmeans" / "unsupervised_clustering_tests"
     mini_batch_kmeans_files = {
         "mini_batch_kmeans_clusterer_2_PROGRESS.csv",
         "mini_batch_kmeans_clusterer_2.pk1",
         "mini_batch_kmeans_clusterer_3_PROGRESS.csv",
         "mini_batch_kmeans_clusterer_3.pk1",
     }
     
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
     
     data_viewer_config = DataViewerConfig()
     types_config = TypesConfig()
     types_config.pollen_types = ["Alnus", "ArrhinateRum"]
     paths_config = PathsConfig()
     paths_config.zip_files_rel_path = "binary_paths"
     model_builder_unsup_config = ModelBuilderUnsupervisedConfig()
     model_builder_unsup_config.train_parameters.pollen_types_binaries_paths = ["binary_paths"]
     model_builder_unsup_config.train_parameters.filter_rel_path = "common/filters/modality_filters.py"
     model_builder_unsup_config.train_parameters.scaler_path = "scaler1_scaler.pkl"
     model_builder_unsup_config.train_parameters.learningModels = ["spectrum_unsup", "lifetime_unsup", "scattering_unsup", "size"]
     model_builder_unsup_config.model_save_name = "unsupervised_clustering_tests"
     model_builder_unsup_config.train_parameters.train_model = False
     model_builder_unsup_config.verify_model.verify_model = False
     model_builder_unsup_config.cluster_parameters.run_clustering = True
     model_builder_unsup_config.cluster_parameters.hdbscan.run_hdbscan = True
     model_builder_unsup_config.cluster_parameters.hdbscan.min_samples = [2]
     model_builder_unsup_config.cluster_parameters.umap.run_umap = True
     model_builder_unsup_config.cluster_parameters.clusterer.run_clusterer = True
     model_builder_unsup_config.cluster_parameters.clusterer.cluster_sizes = [2, 3]
     model_builder_unsup_config.cluster_parameters.kmeans.run_kmeans = True
 
     def fake_get(config, refresh=False):
         if config is ModelBuilderConfig:
             return model_builder_config
 
         if config is TypesConfig:
             return types_config
 
         if config is PathsConfig:
             return paths_config
         
         if config is ModelBuilderUnsupervisedConfig:
             return model_builder_unsup_config
         
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
     
     monkeypatch.setattr(time, "time", lambda: timestamp)
     
     # act
     from src.modelBuilder import ModelBuilderUnsupervided
     ModelBuilderUnsupervided.handle()
 
     # assert
     assert latent_vectors_path.is_file(), f"Latent vectors file was not created: {latent_vectors_path}"
     
     assert_files(plots_path, expected_plots, "*.png")
     assert_files(umap_files_path, umap_files)
     assert_files(hdbscan_files_path, hdbscan_files)
     assert_files(mini_batch_kmeans_files_path, mini_batch_kmeans_files)
     
def assert_files(path, expected_files, extension="*"):
    actual_files = {
        file.name
        for file in path.glob(f"{extension}" if extension != "*" else "*")
        if file.is_file()
    }

    assert actual_files == set(expected_files)    
    
@pytest.mark.forked
def test_handle_when_run_clustering_true_with_known_sample_and_without_umap_given_runs_clustering(monkeypatch, test_resources):
     # arrange
     timestamp = 1791710451
     
     latent_vectors_path = test_resources / "unsupervised" / "latent_vectors" / "unsupervised_clustering_known_sample_tests-_reg-2dirs_latent_vectors.h5"
     
     plots_path = test_resources / "plots"
     expected_plots = {
         "plot_3.png",
         "plot_hdbscan_1.png",
         *{f"plot_embeddings_{i}.png" for i in range(1, 3)},
     }
     
     umap_files_path = test_resources / "unsupervised" / "umap"
     umap_files = {}
     
     hdbscan_files_path = test_resources / "unsupervised" / "hdbscan"
     hdbscan_files = {
         f"unsupervised_clustering_known_sample_tests-pred-0.5sr-z_score_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscan_class_counts_metadata.csv",
         f"unsupervised_clustering_known_sample_tests-pred-0.5sr-z_score_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscan_knn.joblib",
         f"unsupervised_clustering_known_sample_tests-pred-0.5sr-z_score_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscan_preds_lot.png",
         f"unsupervised_clustering_known_sample_tests-pred-0.5sr-z_score_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscan.joblib",
         f"unsupervised_clustering_known_sample_tests-pred-0.5sr-z_score_pre_norm-0_95pca-max_post_norm-Nonetrans-chebyshev-eom_csm-1_0-1000mcs-2ms-0_0cse_hdbscantrue.png",
     }
     
     mini_batch_kmeans_files_path = test_resources / "unsupervised" / "mini_batch_kmeans" / "unsupervised_clustering_known_sample_tests"
     mini_batch_kmeans_files = {
         "mini_batch_kmeans_clusterer_2_PROGRESS.csv",
         "mini_batch_kmeans_clusterer_2.pk1",
         "mini_batch_kmeans_clusterer_3_PROGRESS.csv",
         "mini_batch_kmeans_clusterer_3.pk1",
     }
     kmeans_files_path = test_resources / "unsupervised" / "kmeans"
     kmeans_files = {
         "unsupervised_clustering_known_sample_tests-2cl-kmeans.joblib",
     }
     
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
     
     data_viewer_config = DataViewerConfig()
     types_config = TypesConfig()
     types_config.pollen_types = ["Alnus", "ArrhinateRum"]
     paths_config = PathsConfig()
     paths_config.zip_files_rel_path = "binary_paths"
     model_builder_unsup_config = ModelBuilderUnsupervisedConfig()
     model_builder_unsup_config.train_parameters.pollen_types_binaries_paths = ["binary_paths"]
     model_builder_unsup_config.train_parameters.with_labeled_samples = True
     model_builder_unsup_config.train_parameters.pollen_types = ["Alnus"]
     model_builder_unsup_config.train_parameters.filter_rel_path = "common/filters/modality_filters.py"
     model_builder_unsup_config.train_parameters.scaler_path = "scaler1_scaler.pkl"
     model_builder_unsup_config.train_parameters.learningModels = ["spectrum_unsup", "lifetime_unsup", "scattering_unsup", "size"]
     model_builder_unsup_config.model_save_name = "unsupervised_clustering_known_sample_tests"
     model_builder_unsup_config.train_parameters.train_model = False
     model_builder_unsup_config.verify_model.verify_model = False
     model_builder_unsup_config.cluster_parameters.run_clustering = True
     model_builder_unsup_config.cluster_parameters.hdbscan.run_hdbscan = True
     model_builder_unsup_config.cluster_parameters.hdbscan.min_samples = [2]
     model_builder_unsup_config.cluster_parameters.hdbscan.pre_pca_normalization = "z_score"
     model_builder_unsup_config.cluster_parameters.hdbscan.knn.train_knn = True
     model_builder_unsup_config.cluster_parameters.hdbscan.knn.n_neighbors = 2
     model_builder_unsup_config.cluster_parameters.umap.run_umap = False
     model_builder_unsup_config.cluster_parameters.clusterer.run_clusterer = True
     model_builder_unsup_config.cluster_parameters.clusterer.cluster_sizes = [2, 3]
     model_builder_unsup_config.cluster_parameters.kmeans.run_kmeans = True
     
 
     def fake_get(config, refresh=False):
         if config is ModelBuilderConfig:
             return model_builder_config
 
         if config is TypesConfig:
             return types_config
 
         if config is PathsConfig:
             return paths_config
         
         if config is ModelBuilderUnsupervisedConfig:
             return model_builder_unsup_config
         
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
     
     monkeypatch.setattr(time, "time", lambda: timestamp)
     
     # act
     from src.modelBuilder import ModelBuilderUnsupervided
     ModelBuilderUnsupervided.handle()
 
     # assert
     assert latent_vectors_path.is_file(), f"Latent vectors file was not created: {latent_vectors_path}"
     
     assert_files(plots_path, expected_plots, "*.png")
     assert_files(umap_files_path, umap_files)
     assert_files(hdbscan_files_path, hdbscan_files)
     assert_files(mini_batch_kmeans_files_path, mini_batch_kmeans_files)
     assert_files(kmeans_files_path, kmeans_files)
     
def assert_files(path, expected_files, extension="*"):
    actual_files = {
        file.name
        for file in path.glob(f"{extension}" if extension != "*" else "*")
        if file.is_file()
    }

    assert actual_files == set(expected_files)
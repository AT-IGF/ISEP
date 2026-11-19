"""
Sample flow of all ISEP tasks run on the sample/PKL_Test.zip data (Alnus and ArrhinateRum).
The data is small (86 particles), it serves as a check that the installation works, results are not
a model evaluation. Run from the repository root: python sample/sample_flow.py
"""

import logging
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))  # running from source, without installed package


def handle_sample_data():
    logging.getLogger().info("================================")
    logging.getLogger().info("FILES EXTRACTION")
    logging.getLogger().info("================================")

    data_path = REPO_ROOT / "resources" / "PKL_Test"
    if data_path.is_dir() and any(path.is_file() for path in data_path.rglob("*")):
        print(f"Sample data already extracted, path='{data_path}'")
        return
    with zipfile.ZipFile(REPO_ROOT / "sample" / "PKL_Test.zip") as zip_file:
        zip_file.extractall(REPO_ROOT / "resources")
    print(f"Sample data extracted, path='{data_path}'")


def handle_single():
    logging.getLogger().info("================================")
    logging.getLogger().info("SINGLE SAMPLE")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import TypesConfig, PathsConfig, SingleSampleConfig
    from isep.configs.singleSample import SingleSamplePlotModel

    isep.plot_single_sample(
        PathsConfig(zip_files_rel_path="PKL_Test"),
        TypesConfig(pollen_types=["Alnus", "ArrhinateRum"]),
        SingleSampleConfig(
            plots_save_path="dataViewer/out",
            same_type_count=2,
            spectrum_plot=SingleSamplePlotModel(show=True),
            pollen_types_to_show=["Alnus", "ArrhinateRum"],
            show_plots=False,  # plots are only saved, windows would stop the flow
        ),
    )


def handle_aggregated():
    logging.getLogger().info("================================")
    logging.getLogger().info("AGGREGATED SAMPLES")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import TypesConfig, PathsConfig, MultipleSamplesConfig
    from isep.configs.multipleSamples import ScatteringModel, HistogramModel

    isep.plot_aggregated_samples(
        PathsConfig(zip_files_rel_path="PKL_Test"),
        TypesConfig(pollen_types=["Alnus", "ArrhinateRum"]),
        MultipleSamplesConfig(
            metric_to_process="scattering",
            single_type_count=5000,
            pollen_types=["Alnus", "ArrhinateRum"],
            scattering=ScatteringModel(
                histogram=HistogramModel(
                    plot=True, operation=HistogramModel.MAX_OPERATION, hist_bins=5
                )
            ),
        ),
    )


def handle_scaler():
    logging.getLogger().info("================================")
    logging.getLogger().info("SCALER")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import ModelDataScalerConfig

    isep.scale_model_data(
        ModelDataScalerConfig(
            scaler_name="my_scaler",
            pollen_types_binaries_paths=["PKL_Test"],
            filter_rel_path="common/filters/base_cleanup.py",
        )
    )


def handle_supervised_trainer_training(model_save_name, epochs):
    logging.getLogger().info("================================")
    logging.getLogger().info("SUPERVISED TRAINING")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import SupervisedTrainingConfig, TypesConfig, PathsConfig
    from isep.configs.supervisedTraining import TrainParametersModel, EarlyStoppingModel

    isep.train_supervised_model(
        PathsConfig(zip_files_rel_path="PKL_Test"),
        TypesConfig(pollen_types=["Alnus", "ArrhinateRum"]),
        SupervisedTrainingConfig(
            model_save_name=model_save_name,
            test_model_name="model_1_test_model",  # the same namespace, the same test set
            run_training=True,
            train_parameters=TrainParametersModel(
                single_type_count=2000,
                sampling_strategy=TrainParametersModel.OVERSAMPLE_STRATEGY,
                epochs=epochs,
                early_stopping=EarlyStoppingModel(
                    enabled=True, min_delta=0.05, patience=2
                ),
            ),
            scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
        ),
    )


def handle_supervised_trainer_calibration_evaluation():
    logging.getLogger().info("================================")
    logging.getLogger().info("SUPERVISED MODEL CALIBRATION")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import SupervisedTrainingConfig
    from isep.configs.supervisedTraining import CalibrationModel, SummaryModel

    isep.train_supervised_model(
        SupervisedTrainingConfig(
            model_save_name="model_1",
            test_model_name="model_1_test_model",
            run_training=False,
            calibration=CalibrationModel(
                run_calibration=True,
                evaluate_calibration=True,
                evaluation_mode=CalibrationModel.ALL_EVALUATION,
                plot_probability_distributions=False,
            ),
            scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            summaries=SummaryModel(run_summaries=True, f1_score=True),
        )
    )


def handle_supervised_trainer_comparison():
    logging.getLogger().info("================================")
    logging.getLogger().info("SUPERVISED MODEL EVALUATION")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import SupervisedTrainingConfig
    from isep.configs.supervisedTraining import SummaryModel

    isep.train_supervised_model(
        SupervisedTrainingConfig(
            model_save_name="model_1",
            test_model_name="model_1_test_model",
            run_training=False,
            scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            summaries=SummaryModel(
                run_summaries=True, f1_score=True, diff_model_name="model_2"
            ),
        )
    )


def handle_unsupervised_trainer_training():
    logging.getLogger().info("================================")
    logging.getLogger().info("UNSUPERVISED TRAINING")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import UnsupervisedTrainingConfig
    from isep.configs.unsupervisedTraining import TrainParametersModel, VerifyModel

    isep.train_unsupervised_model(
        UnsupervisedTrainingConfig(
            model_save_name="unsupervised_model_1",
            train_parameters=TrainParametersModel(
                train_model=True,
                pollen_types_binaries_paths=["PKL_Test"],
                learningModels=list(TrainParametersModel.InputModelNames.TRAIN_MODELS),
                scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
                epochs=5,
            ),
            verify_model=VerifyModel(verify_model=False),
        )
    )


def handle_unsupervised_trainer_verification():
    logging.getLogger().info("================================")
    logging.getLogger().info("UNSUPERVISED MODEL EVALUATION")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import UnsupervisedTrainingConfig
    from isep.configs.unsupervisedTraining import TrainParametersModel, VerifyModel

    isep.train_unsupervised_model(
        UnsupervisedTrainingConfig(
            model_save_name="unsupervised_model_1",
            train_parameters=TrainParametersModel(
                train_model=False,
                pollen_types_binaries_paths=["PKL_Test"],
                learningModels=list(TrainParametersModel.InputModelNames.TRAIN_MODELS),
                scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
                with_labeled_samples=True,
                pollen_types=["Alnus"],
            ),
            verify_model=VerifyModel(
                verify_model=True, plot_reconstructions=False, calc_recon_errors=True
            ),
        )
    )


def handle_unsupervised_trainer_clustering():
    logging.getLogger().info("================================")
    logging.getLogger().info("UNSUPERVISED MODEL CLUSTERING")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import UnsupervisedTrainingConfig
    from isep.configs.unsupervisedTraining import (
        TrainParametersModel,
        VerifyModel,
        ClusterParameterModel,
        UmapModel,
        HdbscanModel,
        KMeansModel,
    )

    isep.train_unsupervised_model(
        UnsupervisedTrainingConfig(
            model_save_name="unsupervised_model_1",
            train_parameters=TrainParametersModel(
                train_model=False,
                pollen_types_binaries_paths=["PKL_Test"],
                learningModels=list(TrainParametersModel.InputModelNames.TRAIN_MODELS),
                pollen_types=["Alnus"],
                with_labeled_samples=True,
                filter_rel_path="common/filters/modality_filters.py",
                scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            ),
            verify_model=VerifyModel(verify_model=False),
            cluster_parameters=ClusterParameterModel(
                run_clustering=True,
                # lowered for 86 particles, docs: n_neighbors=[100], min_cluster_size=[250], min_samples=[100]
                umap=UmapModel(
                    run_umap=True,
                    n_neighbors=[15],
                    n_components=[3],
                    sample_ratio=1.0,
                ),
                hdbscan=HdbscanModel(
                    run_hdbscan=True,
                    min_cluster_size=[10],
                    min_samples=[5],
                    pca_components=None,
                    post_pca_normalization=None,
                    sample_ratio=1.0,
                ),
                kmeans=KMeansModel(run_kmeans=True),
            ),
        )
    )


def handle_model_inference():
    logging.getLogger().info("================================")
    logging.getLogger().info("MODEL INFERENCE")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import PredictionsRunnerConfig
    from isep.configs.predictionsRunner import ProcessingModel

    isep.run_predictions(
        PredictionsRunnerConfig(
            model_rel_path="modelBuilder/model_1_model.h5",
            pollen_types=["Alnus", "ArrhinateRum"],
            types_to_predict_rel_dirs=["PKL_Test"],
            filter_rel_path="common/filters/modality_filters.py",
            scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            processing=ProcessingModel(
                output_dir="modelRunner/out",
                combined_files_filename="sample_flow",
                threshold=0.2,
            ),
        )
    )


def handle_predictions_mapper():
    logging.getLogger().info("================================")
    logging.getLogger().info("MODEL PREDICTIONS PLOTTING")
    logging.getLogger().info("================================")

    import isep
    from isep.configs import PredictionsMapperConfig
    from isep.configs.predictionsMapper import (
        SplitTimespanModel,
        ThresholdsModel,
        PlotSettingsModel,
        BarPlotSettingsModel,
    )

    isep.map_predictions(
        PredictionsMapperConfig(
            file_to_process_rel_path="modelRunner/out/tr_0_sample_flow.csv",
            pollen_types=["Alnus", "ArrhinateRum"],
            split_timespan=SplitTimespanModel(days=1),
            thresholds=ThresholdsModel(threshold=0.5),
            plot_settings=PlotSettingsModel(
                plot_style=PlotSettingsModel.BAR_STYLE_PLOT,
                bar_plot_settings=BarPlotSettingsModel(
                    plot_type=BarPlotSettingsModel.PARTICLES_PER_METER_CUBED,
                    display_as_grid=True,
                ),
            ),
        )
    )


def print_results():
    resources_path = REPO_ROOT / "resources"
    print("Results:")
    for path in [
        "dataViewer/out",
        "modelBuilder/scaler/base_cleanup",
        "modelBuilder/model_1_model.h5",
        "modelBuilder/model_2_model.h5",
        "modelBuilder/unsupervised_model_1_model.h5",
        "unsupervised",
        "modelRunner/out/tr_0_sample_flow.csv",
        "predictionsMapper/out",
    ]:
        status = "ok" if (resources_path / path).exists() else "missing"
        print(f"{status}: {resources_path / path}")


if __name__ == "__main__":
    handle_sample_data()
    handle_single()
    handle_aggregated()
    handle_scaler()
    handle_supervised_trainer_training(model_save_name="model_1", epochs=5)
    handle_supervised_trainer_calibration_evaluation()
    handle_supervised_trainer_training(model_save_name="model_2", epochs=2)
    handle_supervised_trainer_comparison()
    handle_unsupervised_trainer_training()
    handle_unsupervised_trainer_verification()
    handle_unsupervised_trainer_clustering()
    handle_model_inference()
    handle_predictions_mapper()
    print_results()

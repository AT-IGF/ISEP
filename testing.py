def handle_single():
    import isep
    from isep.configs.singleSample import SingleSamplePlotModel
    from isep.configs import TypesConfig, PathsConfig

    paths_config = PathsConfig(zip_files_rel_path="E:/PKL_Test")
    types_config = TypesConfig(pollen_types=["Alnus", "ArrhinateRum"])

    isep.plot_single_sample(
        paths_config,
        types_config,
        plots_save_path="dataViewer/out",
        spectrum_plot=SingleSamplePlotModel(show=True),
        pollen_types_to_show=["Alnus", "ArrhinateRum"],
    )


def handle_aggregated():
    import isep
    from isep.configs import TypesConfig, PathsConfig, MultipleSamplesConfig
    from isep.configs.multipleSamples import ScatteringModel, HistogramModel

    paths_config = PathsConfig(zip_files_rel_path="E:/PKL_Test")
    types_config = TypesConfig(pollen_types=["Alnus", "ArrhinateRum"])

    isep.plot_aggregated_samples(
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
        paths_config,
        types_config,
    )


def handle_scaler():
    import isep
    from isep.configs import ModelDataScalerConfig

    isep.scale_model_data(
        ModelDataScalerConfig(
            scaler_name="my_scaler",
            pollen_types_binaries_paths=["E:/PKL_Test"],
            filter_rel_path="common/filters/base_cleanup.py",
        )
    )


def handle_supervised_trainer_training():
    import isep
    from isep.configs import SupervisedTrainingConfig
    from isep.configs.supervisedTraining import TrainParametersModel, EarlyStoppingModel

    isep.train_supervised_model(
        SupervisedTrainingConfig(
            model_save_name="model_1",
            test_model_name="model_1_test_model",
            run_training=True,
            train_parameters=TrainParametersModel(
                single_type_count=2000,
                sampling_strategy=TrainParametersModel.OVERSAMPLE_STRATEGY,
                epochs=5,
                early_stopping=EarlyStoppingModel(
                    enabled=True, min_delta=0.05, patience=5
                ),
            ),
            scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
        )
    )


def handle_supervised_trainer_calibration_evaluation():
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
                plot_probability_distributions=True,
            ),
            scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            summaries=SummaryModel(run_summaries=True, f1_score=True),
        )
    )


def handle_unsupervised_trainer_training():
    import isep
    from isep.configs import UnsupervisedTrainingConfig
    from isep.configs.unsupervisedTraining import TrainParametersModel

    isep.train_unsupervised_model(
        UnsupervisedTrainingConfig(
            model_save_name="unsupervised_model_1",
            train_parameters=TrainParametersModel(
                train_model=True,
                pollen_types_binaries_paths=["E:/PKL_Test"],
                learningModels=TrainParametersModel.InputModelNames.TRAIN_MODELS,
                scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
                epochs=5,
            ),
        )
    )


def handle_unsupervised_trainer_verification():
    import isep
    from isep.configs import UnsupervisedTrainingConfig
    from isep.configs.unsupervisedTraining import TrainParametersModel, VerifyModel

    isep.train_unsupervised_model(
        UnsupervisedTrainingConfig(
            model_save_name="unsupervised_model_1",
            train_parameters=TrainParametersModel(
                train_model=False,
                pollen_types_binaries_paths=["E:/PKL_Test"],
                learningModels=TrainParametersModel.InputModelNames.TRAIN_MODELS,
                scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            ),
            verify_model=VerifyModel(
                with_labeled_samples=True,
                pollen_types=["Alnus"],
                plot_reconstructions=False,
                calc_recon_errors=True,
            ),
        )
    )


def handle_unsupervised_trainer_clustering():
    import isep
    from isep.configs import UnsupervisedTrainingConfig
    from isep.configs.unsupervisedTraining import (
        TrainParametersModel,
        VerifyModel,
        ClusterParameterModel,
        UmapModel,
        HdbscanModel,
    )

    isep.train_unsupervised_model(
        UnsupervisedTrainingConfig(
            model_save_name="unsupervised_model_1",
            train_parameters=TrainParametersModel(
                train_model=False,
                pollen_types_binaries_paths=["E:/PKL_Test"],
                learningModels=TrainParametersModel.InputModelNames.TRAIN_MODELS,
                pollen_types=["Alnus"],
                with_labeled_samples=True,
                filter_rel_path="common/filters/modality_filters.py",
                scaler_path="modelBuilder/scaler/base_cleanup/my_scaler.pkl",
            ),
            verify_model=VerifyModel(verify_model=False),
            cluster_parameters=ClusterParameterModel(
                run_clustering=True,
                umap=UmapModel(
                    run_umap=True,
                    n_neighbors=[100],
                    n_components=[3],
                    sample_ratio=1.0,
                ),
                hdbscan=HdbscanModel(
                    run_hdbscan=True,
                    min_cluster_size=[250],
                    min_samples=[100],
                    post_pca_normalization=None,
                    sample_ratio=1.0,
                ),
            ),
        )
    )


if __name__ == "__main__":
    # handle_single()
    # handle_aggregated()
    # handle_scaler()
    # handle_supervised_trainer_training()
    # handle_supervised_trainer_calibration_evaluation()
    # handle_unsupervised_trainer_training()
    handle_unsupervised_trainer_verification()

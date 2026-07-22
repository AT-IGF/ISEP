import logging

from src.core import PathHelper
import numpy as np
from src.modelBuilder.summaries import ROCSummary, PrecRecallSummary
from src.modelBuilder.summaries import SizeSummary
from src.common.config import Config, ModelBuilderConfig, TypesConfig
from src.modelBuilder.confusionMatrix import make_confusion_matrix
from src.modelBuilder.keras.models import TrainedModel
from src.modelBuilder.summaries import calculate_thresholds


class KerasVerifier:
    @staticmethod
    def get_diff_model(config: ModelBuilderConfig):
        if config.summaries.diff_model_name == None:
            return

        diff_model_path = config.get_model_path(config.summaries.diff_model_name)
        model_diff = None
        if diff_model_path != None and PathHelper.is_file_exists(diff_model_path):
            from tensorflow.keras.models import load_model

            logging.getLogger().info(
                f"Diff (another) model found, path='{diff_model_path}'"
            )
            model_diff = load_model(diff_model_path)
        else:
            if config.summaries.diff_model_name != None:
                logging.getLogger().warning(
                    f"Diff (another) model NOT found, despite 'diff_model_name' is set. Path = {diff_model_path}"
                )

        return model_diff

    @staticmethod
    def get_diff_model_preds(config: ModelBuilderConfig, model_diff, dataset):
        y_pred_diff = model_diff.predict(dataset.X_test)
        if config.summaries.evaluate == True:
            logging.getLogger().info("Evaluation of diff model - no thresold")
            model_diff.evaluate(dataset.X_test, np.array(dataset.y_test))
        return y_pred_diff

    @staticmethod
    @staticmethod
    def verify_model(trained_model: TrainedModel, summary: str, scalers: dict):
        config = Config.get(ModelBuilderConfig)
        logging.getLogger().info(f"Run summaries={config.summaries.run_summaries}")
        if config.summaries.run_summaries == False:
            return
        model = trained_model.model
        dataset = trained_model.get_test_dataset()

        if not config.run_training:  # do not show agin the same summary
            lines = []
            trained_model.model.summary(print_fn=lines.append)
            logging.getLogger().info("\n".join(lines))
        y_pred = model.predict(dataset.X_test)

        if y_pred.shape != dataset.y_test.shape:
            raise TypeError(
                f"Predicted and tested sets shapes does not match. test_shape={dataset.y_test.shape}, pred_shape={y_pred.shape}. Perhaps model was trained on different number of pollen types?"
            )

        if config.summaries.evaluate == True:
            logging.getLogger().info("Evaluation trained model - no threshold")
            model.evaluate(dataset.X_test, np.array(dataset.y_test))

        roc_summary = ROCSummary()
        prec_recall_summary = PrecRecallSummary()
        pollen_types = Config().get(TypesConfig).pollen_types

        y_pred_max = np.array(y_pred).argmax(axis=1)

        logging.getLogger().info("Trained model summary - no threshold")
        prec_recall = prec_recall_summary.print_prec_recall_summary(
            y_pred=y_pred_max, dataset=dataset
        )
        roc_score = roc_summary.print_roc_summary(y_pred=y_pred, y_test=dataset.y_test)
        diff_model = KerasVerifier.get_diff_model(config)
        y_pred_diff = None
        if diff_model is not None:
            y_pred_diff = KerasVerifier.get_diff_model_preds(
                config, diff_model, dataset
            )
            logging.getLogger().info("--- Diff model model summary - no threshold ---")
            y_pred_diff_max = y_pred_diff.argmax(axis=1)
            prec_recall_summary.print_prec_recall_summary(
                y_pred=y_pred_diff_max, dataset=dataset, origin_prec_recall=prec_recall
            )
            roc_summary.print_roc_summary(
                y_pred=y_pred_diff, y_test=dataset.y_test, origin_score=roc_score
            )
            calculate_thresholds(
                y_pred=y_pred_diff,
                dataset=dataset,
                model=diff_model,
                thresholds=config.summaries.thresholds,
                pollen_types=pollen_types,
            )
            logging.getLogger().info(f"--- Diff model calculations finieshed ---")

        if config.summaries.roc_curve == True:
            roc_summary.summary(y_pred=y_pred, dataset=dataset)

        if config.summaries.prec_recall_curve == True:
            prec_recall_summary.summary(
                y_pred=y_pred, dataset=dataset, mode="PREC_RECALL"
            )
        if config.summaries.f1_score == True:
            prec_recall_summary.summary(y_pred=y_pred, dataset=dataset, mode="F1")

        if config.summaries.confusion_matrix == True:
            make_confusion_matrix(
                y_pred=y_pred_max,
                y_true=dataset.y_test_max,
                classes=pollen_types,
                summary=summary,
                y_pred_diff=None if y_pred_diff is None else y_pred_diff.argmax(axis=1),
            )

        calculate_thresholds(
            y_pred=y_pred,
            dataset=dataset,
            model=model,
            thresholds=config.summaries.thresholds,
            pollen_types=pollen_types,
        )

        if config.summaries.size_summary == True:
            SizeSummary().summary(trained_model, scalers)

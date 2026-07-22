import logging
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
import keras

from src.core.plots.plotting_utils import plt_show


@keras.saving.register_keras_serializable(package="MyLayers")
class TemperatureScalingLayer(tf.keras.layers.Layer):
    def __init__(self, classes_count=14, **kwargs):
        super().__init__(**kwargs)
        self.t = self.add_weight(
            name="temperature",
            shape=(classes_count,),
            initializer=tf.keras.initializers.Constant(0.0),
            trainable=True,
        )

    def get_true_t(self):
        return tf.exp(self.t)

    def call(self, logits):
        temp = self.get_true_t()
        return tf.nn.softmax(logits / temp, axis=-1)


class TemperatureScaler:
    def __init__(
        self, base_model, X_calib, y_calib, logits_layer_index=-2, classes_count=1
    ):
        self.base_model = base_model
        self.X_calib = X_calib
        self.y_calib = y_calib
        self.logits_layer_index = logits_layer_index
        self.calibrated_model = None
        self.t_history = []
        self.classes_count = classes_count

        # Freeze base model layers
        for layer in self.base_model.layers:
            layer.trainable = False

    def build_calibrated_model(self):
        """Create modified model with temperature scaling layer"""
        logits = self.base_model.get_layer("logits").output
        scaled_probs = TemperatureScalingLayer(
            classes_count=self.classes_count, name="temperature_scaling"
        )(logits)

        self.calibrated_model = tf.keras.Model(
            inputs=self.base_model.input, outputs=scaled_probs
        )

        self.calibrated_model.summary()

        return self.calibrated_model

    def fit(self, epochs=50, batch_size=32, learning_rate=0.01, verbose=1):
        self.build_calibrated_model()

        lr_schedule = tf.keras.optimizers.schedules.CosineDecay(
            initial_learning_rate=learning_rate,
            decay_steps=epochs,
        )

        lr_cb = tf.keras.callbacks.LearningRateScheduler(
            schedule=lambda epoch, lr: float(lr_schedule(epoch)), verbose=1
        )

        self.calibrated_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss=tf.keras.losses.CategoricalCrossentropy(),
            metrics=["accuracy"],
        )

        self.t_history = []

        class TemperatureHistoryCallback(tf.keras.callbacks.Callback):
            def __init__(self, parent):
                super().__init__()
                self.parent = parent
                self.t_layer = None

            def on_train_begin(self, logs=None):
                for layer in self.model.layers:
                    if isinstance(layer, TemperatureScalingLayer):
                        self.t_layer = layer
                        break
                if self.t_layer is None:
                    raise RuntimeError(
                        "Temperature scaling layer not found in model layers"
                    )

            def on_epoch_end(self, epoch, logs=None):
                current_temp = self.t_layer.get_true_t().numpy()
                self.parent.t_history.append(current_temp)
                temps_formatted = ["{:.2f}".format(x) for x in current_temp]
                logging.getLogger().info(temps_formatted)
                logs["temperature_avg"] = np.average(current_temp)

        history = self.calibrated_model.fit(
            self.X_calib,
            self.y_calib,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
            callbacks=[TemperatureHistoryCallback(self), lr_cb],
        )

        return history

    def plot_temp_changes(self):
        plt.plot(self.t_history)
        plt.title("Temperature Value During Training")
        plt.ylabel("Temperature")
        plt.xlabel("Epoch")
        plt_show(plt.gcf())

    def evaluate_calibration(
        self, X_test, y_test, model, mode="ALL", n_bins=20, name=""
    ):
        probs = model.predict(X_test)
        df = pd.DataFrame()
        pd.set_option("display.max_columns", None)  # show all columns
        pd.set_option("display.max_rows", None)  # show all rows
        pd.set_option("display.max_colwidth", None)  # don't truncate column values
        pd.set_option("display.width", None)  # no fixed width for wrapping

        logging.getLogger().info(f"Evaluation mode={mode}")
        if mode == "CLASS":
            for i in range(0, self.classes_count):
                y_true = y_test.argmax(axis=1)
                y_true_i = (y_true == i).astype(int)
                probs_i = probs[:, i]

                ece_i, acc, bin_acc, bin_conf, bin_counts = self.class_ece_acc_bins(
                    y_true_i, probs_i, n_bins
                )

                df[f"ece_{i}"] = ece_i
                df[f"acc_{i}"] = acc
                df[f"bin_acc_{i}"] = bin_acc
                df[f"bin_conf_{i}"] = bin_conf
                df[f"bin_counts_{i}"] = bin_counts
        else:
            bin_edge_low, bin_edge_top, ece, acc, bin_acc, bin_conf, count = (
                self._calculate_ece(y_test.argmax(axis=1), probs, n_bins)
            )
            df[f"bin_edge_low"] = bin_edge_low
            df[f"bin_edge_top"] = bin_edge_top
            df[f"bin_acc"] = bin_acc
            df[f"bin_conf"] = bin_conf
            df[f"ece"] = ece
            df[f"acc"] = acc
            df[f"count"] = count

        logging.getLogger().info(f"{name}\n{df.round(2)}")

    def _calculate_ece(self, y_true, y_prob, n_bins=10):
        bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
        bin_indices = np.digitize(y_prob.max(axis=1), bin_edges[:-1]) - 1

        ece = 0.0
        bin_acc = []
        bin_conf = []
        count = []
        bin_edge_low = []
        bin_edge_top = []
        acc_total = np.mean(y_true == y_prob.argmax(axis=1))

        for b in range(n_bins):
            mask = bin_indices == b
            count.append(np.sum(mask))
            bin_edge_low.append(bin_edges[b])
            bin_edge_top.append(bin_edges[b + 1])
            if np.sum(mask) > 0:
                acc = np.mean(y_true[mask] == y_prob[mask].argmax(axis=1))
                conf = np.mean(y_prob[mask].max(axis=1))
                ece += np.abs(acc - conf) * np.sum(mask) / len(y_true)
                bin_acc.append(acc)
                bin_conf.append(conf)
            else:
                bin_acc.append(0)
                bin_conf.append(0)

        return bin_edge_low, bin_edge_top, ece, acc_total, bin_acc, bin_conf, count

    def class_ece_acc_bins(
        self, y_true_i, probs_i, n_bins=10
    ):  # On Calibration of Modern Neural Networks Guo et. al., 2017
        y_true_i = np.asarray(y_true_i).astype(float)
        probs_i = np.asarray(probs_i).astype(float)
        if y_true_i.shape[0] != probs_i.shape[0]:
            raise ValueError("y_true_i and probs_i must have the same length")

        N = len(y_true_i)
        bins = np.linspace(0.0, 1.0, n_bins + 1)

        ece_i = 0.0
        bin_acc = np.full(
            n_bins, np.nan, dtype=float
        )  # observed frequency of true==i in each bin
        bin_conf = np.full(
            n_bins, np.nan, dtype=float
        )  # mean predicted prob in each bin
        bin_counts = np.zeros(n_bins, dtype=int)

        for j in range(n_bins):
            lo, hi = bins[j], bins[j + 1]
            if j == 0:
                mask = (probs_i >= lo) & (probs_i <= hi)
            else:
                mask = (probs_i > lo) & (probs_i <= hi)

            m = int(mask.sum())
            bin_counts[j] = m
            if m == 0:
                continue

            obs_freq = y_true_i[mask].mean()
            conf = probs_i[mask].mean()

            bin_acc[j] = obs_freq
            bin_conf[j] = conf

            ece_i += (m / N) * abs(obs_freq - conf)

        acc_i = np.nansum((bin_counts / N) * bin_acc)

        return ece_i, acc_i, bin_acc, bin_conf, bin_counts

    def plot_reliability(self, X_test, y_test, n_bins=10):
        """Generate reliability diagram"""
        probs = self.calibrated_model.predict(X_test)
        prob_true, prob_pred = calibration_curve(
            y_test, probs.max(axis=1), n_bins=n_bins
        )

        plt.figure(figsize=(8, 6))
        plt.plot(prob_pred, prob_true, marker="o", linewidth=1)
        plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
        plt.xlabel("Predicted Probability")
        plt.ylabel("Actual Probability")
        plt.title("Reliability Diagram")
        plt_show(plt.gcf())

    def save_model(self, path):
        """Save calibrated model"""
        self.calibrated_model.save(path)

    def plot_probability_distributions(self, X_test, y_test, bins=15, alpha=0.6):
        """
        Visualize probability distributions before and after calibration
        """
        # Get predictions
        import seaborn as sns

        for i in range(0, self.classes_count):
            mask = y_test.argmax(axis=1) == i
            X_test_masked = {key: value[mask] for key, value in X_test.items()}
            orig_probs = self.base_model.predict(X_test_masked)
            calib_probs = self.calibrated_model.predict(X_test_masked)

            # Plot original probabilities
            fig, (ax1, ax2) = plt.subplots(
                1, 2, sharex=True, sharey=True, figsize=(14, 6)
            )
            ax1.set_xlim(0, 1)
            ax2.set_xlim(0, 1)

            sns.histplot(
                orig_probs.max(axis=1), bins=bins, color="blue", alpha=alpha, ax=ax1
            )
            ax1.set_title("Original Model Confidence Distribution")
            ax1.set_xlabel("Predicted Probability")
            ax1.set_ylabel("Count (log scale)")
            ax1.set_yscale("log")
            ax1.grid(True, alpha=0.3)

            # Plot calibrated probabilities
            ax2 = plt.subplot(1, 2, 2)
            sns.histplot(
                calib_probs.max(axis=1), bins=bins, color="blue", alpha=alpha, ax=ax2
            )
            ax2.set_title("Calibrated Model Confidence Distribution")
            ax2.set_xlabel("Predicted Probability")
            ax2.set_yscale("log")
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt_show(plt.gcf())

            # logging.getLogger().info statistics
            logging.getLogger().info("Original Model:")
            logging.getLogger().info(
                f"- Mean confidence: {orig_probs.max(axis=1).mean():.3f}"
            )
            logging.getLogger().info(
                f"- % predictions > 0.5: {(orig_probs.max(axis=1) > 0.5).mean()*100:.1f}%"
            )

            logging.getLogger().info("\nCalibrated Model:")
            logging.getLogger().info(
                f"- Mean confidence: {calib_probs.max(axis=1).mean():.3f}"
            )
            logging.getLogger().info(
                f"- % predictions > 0.5: {(calib_probs.max(axis=1) > 0.5).mean()*100:.1f}%"
            )

    def plot_reliability_curves(self, X_test, y_test, mode="ALL", bins=10):
        probs = self.calibrated_model.predict(X_test)
        logging.getLogger().info(f"Reliability mode={mode}")
        if mode == "CLASS":
            for i in range(0, self.classes_count):
                self.plot_classwise_reliability(
                    np.argmax(y_test, axis=1), probs, class_idx=i, n_bins=bins
                )
        else:
            self.plot_toplabel_reliability(
                np.argmax(y_test, axis=1), probs, n_bins=bins
            )

    def plot_toplabel_reliability(self, y_true, y_prob, n_bins=10):
        pred_label = np.argmax(y_prob, axis=1)
        conf = np.max(y_prob, axis=1)
        correct = (pred_label == y_true).astype(int)
        frac_pos, mean_pred = calibration_curve(
            correct, conf, n_bins=n_bins, strategy="uniform"
        )
        plt.plot(mean_pred, frac_pos, marker="o")
        plt.plot([0, 1], [0, 1], "k--")
        plt.xlabel("Predicted confidence")
        plt.ylabel("Empirical accuracy")
        plt_show(plt.gcf())
        plt.close()

    def plot_classwise_reliability(self, y_true, y_prob, class_idx, n_bins=10):
        y_true_bin = (y_true == class_idx).astype(int)
        prob = y_prob[:, class_idx]
        frac_pos, mean_pred = calibration_curve(
            y_true_bin, prob, n_bins=n_bins, strategy="uniform"
        )
        plt.plot(mean_pred, frac_pos, marker="o", label=f"class {class_idx}")
        plt.plot([0, 1], [0, 1], "k--", linewidth=0.8)  # 45-degree line
        plt.xlabel("Mean predicted probability")
        plt.ylabel("Observed frequency")
        plt.legend()
        plt_show(plt.gcf())
        plt.close()

    def get_model(self):
        return self.calibrated_model

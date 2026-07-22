import logging
import numpy as np
import tensorflow as tf
from src.common.tensorflow import InputModelNames


class AnomalyDetector:
    CUSTOM_OBJECTS = {
        # For losses (if any MSE-based losses are used)
        'mse': tf.keras.losses.mse,
        # For metrics (critical for your model)
        'lifetime_unsup_decoder_mse': tf.keras.metrics.MeanSquaredError,
        'scattering_unsup_decoder_mse': tf.keras.metrics.MeanSquaredError,
        'size_decoder_mse': tf.keras.metrics.MeanSquaredError,
        'spectrum_unsup_decoder_mse': tf.keras.metrics.MeanSquaredError,
    }
            
    def __init__(self, detecotr_path, thresholds: dict = None):
        self._logger = logging.getLogger()
        self._logger.info(f'AnomalyDetector enabled. Loading... path={detecotr_path}')
        self._model = tf.keras.models.load_model(detecotr_path, custom_objects=self.CUSTOM_OBJECTS)
        if thresholds is None:
            self._thresholds = {InputModelNames.SPECTRUM_UNSUP: 7.8536054934375e-05, InputModelNames.SCATTERING_UNSUP: 0.0002822137088514865, InputModelNames.LIFETIME_UNSUP: 0.0002516890584956855, InputModelNames.SIZE:0.005982901528477669}
            self._logger.warning(f'AnomalyDetector thresholds are None, sefault ones will be taken, thresholds={self._thresholds}')
    
    def predict(self, raw_data_scaled):
        reconstructed_scaled = self._model.predict(raw_data_scaled)
        reconstructed_scaled = {self._model.output_names[i]: reconstructed_scaled[i] for i in range(0, len(reconstructed_scaled))}
        return raw_data_scaled, reconstructed_scaled
        
    def filter_anomalies(self,
        raw_data_scaled
    ) -> dict:

        data_dict, reconstructed_scaled = self.predict(raw_data_scaled)
        def flatten_vals(rec):
            return np.array([x.flatten() for x in rec])

        errors = {}
        dict_keys = list(data_dict.keys())
        for key, values in data_dict.items():
            recon_key = key.replace("_input", "_decoder")
            if np.squeeze(np.array(values)).shape != np.squeeze(np.array(reconstructed_scaled[recon_key])).shape:
                raise ValueError(f"Anomaly sets have different shapes, true_shape={np.array(values).shape}, recon_shape={np.array(reconstructed_scaled[recon_key]).shape}")
            orig_flat = flatten_vals(np.array(values))
            rec_flat  = flatten_vals(np.array(reconstructed_scaled[recon_key]))
            print(key, np.sum(orig_flat))

            if orig_flat.shape != rec_flat.shape:
                raise ValueError(
                    f"Sample {key} dimension mismatch: "
                    f"orig has {orig_flat.shape[0]} elements, "
                    f"recon has {rec_flat.shape[0]} elements."
                )

            mse = np.mean(np.square(orig_flat - rec_flat), axis=1)
            errors.setdefault(key, []).extend(mse)

        mask = None
        for key, values in errors.items():
            key_clean = key.replace("_input", "")
            if key_clean == "size_input":
                continue
            erorr_mask = np.array(values) < self._thresholds[key_clean]
            if mask is None:
                mask = erorr_mask
            else:
                mask = mask & erorr_mask

        filtered_dict = {key: value[mask] for key, value in data_dict.items()}
        filtered_len = len(list(filtered_dict.values())[0])
        self._logger.info(f"Anomaly detector after filtration left={filtered_len}/{len(list(data_dict.values())[0])}")
        return filtered_dict, filtered_len > 0
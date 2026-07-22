from src.common.tensorflow import InputModelNames
import tensorflow as tf
from src.modelBuilder.keras.helpers.TfRecordParsers import TfParserBase

class UnsupervisedTfParser(TfParserBase):
    def __init__(self, learning_models=[], all_models=False):
        self._learning_models = learning_models
        self._all_models = all_models
        self._feature_description = {
            InputModelNames.LIFETIME_UNSUP: tf.io.FixedLenFeature([32 * 8], tf.float32),
            InputModelNames.SCATTERING_UNSUP: tf.io.FixedLenFeature([120 * 24], tf.float32),
            InputModelNames.SPECTRUM_UNSUP: tf.io.FixedLenFeature([32 * 8], tf.float32),
            InputModelNames.SIZE: tf.io.FixedLenFeature((), tf.float32)
        }
        
    def get_shapes(self, suffix, spectrum, scattering, lifetime, size):
        feature_description = {}
        if InputModelNames.SPECTRUM_UNSUP in self._learning_models or self._all_models:
            feature_description[super().to_decoder_name(InputModelNames.SPECTRUM_UNSUP, suffix)] = spectrum
        if InputModelNames.SCATTERING_UNSUP in self._learning_models or self._all_models:
            feature_description[super().to_decoder_name(InputModelNames.SCATTERING_UNSUP, suffix)] = scattering
        if InputModelNames.LIFETIME_UNSUP in self._learning_models or self._all_models:
            feature_description[super().to_decoder_name(InputModelNames.LIFETIME_UNSUP, suffix)] = lifetime
        if InputModelNames.SIZE in self._learning_models or self._all_models:
            feature_description[super().to_decoder_name(InputModelNames.SIZE, suffix)] = size
        return feature_description
    
    def _parse_function(self, proto):
        parsed = tf.io.parse_single_example(proto, self._feature_description)
        lifetime = tf.reshape(parsed[InputModelNames.LIFETIME_UNSUP], [64, 4])
        scattering = tf.reshape(parsed[InputModelNames.SCATTERING_UNSUP], [120, 24])
        spectrum = tf.reshape(parsed[InputModelNames.SPECTRUM_UNSUP], [32, 8])

        size = parsed[InputModelNames.SIZE]
        X_train = self.get_shapes(suffix="_input", spectrum=spectrum, scattering=scattering, lifetime=lifetime, size=size)
        X_test = self.get_shapes(suffix="_decoder", spectrum=spectrum, scattering=scattering, lifetime=lifetime, size=size)

        return X_train, X_test
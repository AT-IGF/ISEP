from src.common.config.configs import TypesConfig
from src.common.config.configs import ModelBuilderConfig
from src.common.config import Config
from src.common.tensorflow import InputModelNames
import tensorflow as tf
from src.modelBuilder.keras.helpers.TfRecordParsers import TfParserBase
import numpy as np


class SupervisedTfParser(TfParserBase):
    TYPE_IDX = "type_idx"
    feature_description = {
        InputModelNames.LIFETIME_UNSUP: tf.io.FixedLenFeature([32 * 8], tf.float32),
        InputModelNames.SCATTERING_UNSUP: tf.io.FixedLenFeature([120 * 24], tf.float32),
        InputModelNames.SPECTRUM_UNSUP: tf.io.FixedLenFeature([32 * 8], tf.float32),
        InputModelNames.SIZE: tf.io.FixedLenFeature((), tf.float32),
        TYPE_IDX: tf.io.FixedLenFeature((), tf.int64),
    }

    def __init__(self, learning_models=[]):
        self._learning_models = learning_models
        self._config_types = Config.get(TypesConfig)
        self._config = Config.get(ModelBuilderConfig)
        self.classes_len = len(
            self._config_types.get_pollen_types(self._config.excludeTypes)
        )

    def get_shapes_train(self, suffix, spectrum, scattering, lifetime, size):
        feature_description = {}
        if InputModelNames.SPECTRUM_UNSUP in self._learning_models:
            feature_description[
                super().to_decoder_name(InputModelNames.SPECTRUM_UNSUP, suffix)
            ] = spectrum
        if InputModelNames.SCATTERING_UNSUP in self._learning_models:
            feature_description[
                super().to_decoder_name(InputModelNames.SCATTERING_UNSUP, suffix)
            ] = scattering
        if InputModelNames.LIFETIME_UNSUP in self._learning_models:
            feature_description[
                super().to_decoder_name(InputModelNames.LIFETIME_UNSUP, suffix)
            ] = lifetime
        if InputModelNames.SIZE in self._learning_models:
            feature_description[
                super().to_decoder_name(InputModelNames.SIZE, suffix)
            ] = size
        return feature_description

    def get_shapes_test(self, type_idx, suffix):
        return {
            super().to_decoder_name(self.TYPE_IDX, suffix): type_idx,
        }

    @tf.function
    def compute_value(self, x):
        # x is a symbolic tensor within this function.
        return tf.reshape(x, [-1])

    def _parse_function(self, proto):
        parsed = tf.io.parse_single_example(proto, self.feature_description)
        lifetime = tf.reshape(parsed[InputModelNames.LIFETIME_UNSUP], [64, 4])
        scattering = tf.reshape(parsed[InputModelNames.SCATTERING_UNSUP], [120, 24])
        spectrum = tf.reshape(parsed[InputModelNames.SPECTRUM_UNSUP], [32, 8])

        size = parsed[InputModelNames.SIZE]
        type_idx = parsed[self.TYPE_IDX]

        X_train = self.get_shapes_train(
            suffix="_input",
            spectrum=spectrum,
            scattering=scattering,
            lifetime=lifetime,
            size=size,
        )
        y_train = self.get_shapes_test(suffix="_output", type_idx=type_idx)
        label_oh = tf.one_hot(type_idx, depth=self.classes_len)

        return X_train, label_oh

    @staticmethod
    def _size_parse_function(proto):
        parsed = tf.io.parse_single_example(
            proto, SupervisedTfParser.feature_description
        )

        size = parsed[InputModelNames.SIZE]

        return size

    @staticmethod
    def _labels_parse_function(proto):
        parsed = tf.io.parse_single_example(
            proto, SupervisedTfParser.feature_description
        )

        type_idx = parsed[SupervisedTfParser.TYPE_IDX]
        return type_idx

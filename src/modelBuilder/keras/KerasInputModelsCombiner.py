import logging
import tensorflow as tf
from src.common.config import Config, ModelBuilderConfig
from src.common.tensorflow import InputModelNames
from src.modelBuilder.keras.helpers import SupervisedTfParser

INPUT_SUFFIX = "_input"
OUTPUT_SUFFIX = "_output"


def create_empty_lists(n):
    return [[] for _ in range(n)]


def create_model(pollen_types):
    tf.random.set_seed(42)
    config = Config().get(ModelBuilderConfig)

    learningModels = Config().get(ModelBuilderConfig).learningModels

    def get_index(model):
        return learningModels.index(model)

    logging.getLogger().info(f"Input modalities: {learningModels}")

    models_count = len(learningModels)
    lists = create_empty_lists(models_count)
    inputs = lists[:]
    models: list[tf.keras.Sequential] = lists[:]

    if InputModelNames.SPECTRUM_UNSUP in learningModels:
        spectrum_input = tf.keras.layers.Input(
            shape=(32, 8), name=f"{InputModelNames.SPECTRUM_UNSUP}{INPUT_SUFFIX}"
        )
        model_spectrum = tf.keras.Sequential(
            [
                tf.keras.layers.Conv1D(
                    input_shape=(32, 8),
                    filters=32,
                    kernel_size=(4),
                    activation="relu",
                    data_format="channels_last",
                ),
                tf.keras.layers.MaxPool1D(2, padding="same"),
                tf.keras.layers.Conv1D(
                    filters=32,
                    kernel_size=(4),
                    activation="relu",
                    data_format="channels_last",
                ),
                tf.keras.layers.GlobalAveragePooling1D(),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dropout(
                    0.3, name=f"{InputModelNames.SPECTRUM_UNSUP}{OUTPUT_SUFFIX}"
                ),
            ],
            name=InputModelNames.SPECTRUM_UNSUP,
        )

        spec_idx = get_index(InputModelNames.SPECTRUM_UNSUP)
        inputs[spec_idx] = spectrum_input
        models[spec_idx] = model_spectrum(spectrum_input)

    if InputModelNames.LIFETIME_UNSUP in learningModels:
        lifetime_input = tf.keras.layers.Input(
            shape=(64, 4), name=f"{InputModelNames.LIFETIME_UNSUP}{INPUT_SUFFIX}"
        )
        model_lifetime = tf.keras.Sequential(
            [
                tf.keras.layers.Conv1D(
                    input_shape=(64, 4),
                    filters=64,
                    kernel_size=(8),
                    activation="relu",
                    data_format="channels_last",
                ),
                tf.keras.layers.MaxPool1D(padding="same"),
                tf.keras.layers.Conv1D(
                    filters=64,
                    kernel_size=(8),
                    activation="relu",
                    data_format="channels_last",
                ),
                tf.keras.layers.GlobalAveragePooling1D(),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dropout(
                    0.3, name=f"{InputModelNames.LIFETIME_UNSUP}{OUTPUT_SUFFIX}"
                ),
            ],
            name=InputModelNames.LIFETIME_UNSUP,
        )

        lft_idx = get_index(InputModelNames.LIFETIME_UNSUP)
        inputs[lft_idx] = lifetime_input
        models[lft_idx] = model_lifetime(lifetime_input)

    if InputModelNames.SCATTERING_UNSUP in learningModels:
        scattering_input = tf.keras.layers.Input(
            shape=(120, 24), name=f"{InputModelNames.SCATTERING_UNSUP}{INPUT_SUFFIX}"
        )
        model_scattering = tf.keras.Sequential(
            [
                tf.keras.layers.Conv1D(
                    input_shape=(120, 24),
                    filters=64,
                    kernel_size=(8),
                    activation="relu",
                    data_format="channels_last",
                ),
                tf.keras.layers.MaxPool1D(padding="same"),
                tf.keras.layers.Conv1D(
                    filters=64,
                    kernel_size=(8),
                    activation="relu",
                    input_shape=(120, 24),
                    data_format="channels_last",
                ),
                tf.keras.layers.MaxPool1D(pool_size=4, padding="same"),
                tf.keras.layers.GlobalAveragePooling1D(),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dropout(
                    0.3, name=f"{InputModelNames.SCATTERING_UNSUP}{OUTPUT_SUFFIX}"
                ),
            ],
            name=InputModelNames.SCATTERING_UNSUP,
        )

        scat_idx = get_index(InputModelNames.SCATTERING_UNSUP)
        inputs[scat_idx] = scattering_input
        models[scat_idx] = model_scattering(scattering_input)

    if InputModelNames.SIZE in learningModels:
        size_input = tf.keras.layers.Input(
            shape=(1,), name=f"{InputModelNames.SIZE}{INPUT_SUFFIX}"
        )
        model_size = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(8, input_shape=(1,), activation="relu"),
                tf.keras.layers.Dropout(
                    0.2, name=f"{InputModelNames.SIZE}{OUTPUT_SUFFIX}"
                ),
            ],
            name=InputModelNames.SIZE,
        )

        size_idx = get_index(InputModelNames.SIZE)
        inputs[size_idx] = size_input
        models[size_idx] = model_size(size_input)

    model_outputs = tf.keras.layers.Concatenate()(models)

    merged_out = tf.keras.layers.BatchNormalization()(model_outputs)
    merged_out = tf.keras.layers.Dense(
        128, activation="swish", kernel_initializer="he_normal"
    )(merged_out)
    merged_out = tf.keras.layers.Dropout(0.3)(merged_out)
    # output = tf.keras.layers.Dense(len(pollen_types), activation='softmax', name=f"{SupervisedTfParser.TYPE_IDX}_output")(merged_out)
    logits = tf.keras.layers.Dense(len(pollen_types), activation=None, name="logits")(
        merged_out
    )
    output = tf.keras.layers.Activation(
        "softmax", name=f"{SupervisedTfParser.TYPE_IDX}_output"
    )(logits)

    model = tf.keras.Model(inputs=inputs, outputs=output)

    logging.getLogger().info(
        f"Smoothing: {config.train_parameters.smoothing}, Learning rate={config.train_parameters.lr}, Weight decay={config.train_parameters.weight_decay}"
    )
    model.compile(
        loss=tf.keras.losses.CategoricalCrossentropy(
            label_smoothing=config.train_parameters.smoothing
        ),
        optimizer=tf.keras.optimizers.AdamW(
            learning_rate=config.train_parameters.lr,
            weight_decay=config.train_parameters.weight_decay,
        ),
        metrics=["accuracy"],
    )

    model.summary()

    return model

    # models = sorted(models, key=lambda model: Config.get(ModelBuilderConfig).get_learning_model_names(suffix=INPUT_SUFFIX).index(model.inputs.name)) # to fit train input

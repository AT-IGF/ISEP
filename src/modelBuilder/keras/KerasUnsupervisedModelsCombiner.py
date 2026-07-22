import logging
import tensorflow as tf

from src.common.config import ModelBuilderUnsupervisedConfig
from src.common.tensorflow import InputModelNames


def create_empty_lists(n):
    return [[] for _ in range(n)]


def get_spatial_size(input):
    input_shape = input.shape[1:]
    if len(input_shape) == 1:
        return 1000000

    return input_shape[0] * input_shape[1]


def create_model(config: ModelBuilderUnsupervisedConfig):
    tf.random.set_seed(42)

    logging.getLogger().info(
        f"Input modalities: {', '.join(config.train_parameters.learningModels) or '[]'}"
    )
    if len(config.train_parameters.learningModels) == 0:
        raise ValueError(f"Input modalities cannot be an empty list (config param: train_parameters.learningModels), available modalities: {', '.join(InputModelNames.TRAIN_MODELS)}")
    
    models_count = len(config.train_parameters.learningModels)
    lists = create_empty_lists(models_count)
    inputs = lists[:]
    encoders = lists[:]
    decoders = lists[:]

    if InputModelNames.SPECTRUM_UNSUP in config.train_parameters.learningModels:
        input1 = tf.keras.layers.Input(
            shape=(32, 8), name=f"{InputModelNames.SPECTRUM_UNSUP}_input"
        )
        model_encoder1 = tf.keras.Sequential(
            [
                tf.keras.layers.Conv1D(32, 3, activation="relu", padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.MaxPool1D(2),  # Output: (16, 32)
                # Conv Block 2
                tf.keras.layers.Conv1D(64, 3, activation="relu", padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.MaxPool1D(2),
                # Conv Block 3
                # Dense Compression
                tf.keras.layers.Flatten(
                    name=f"{InputModelNames.SPECTRUM_UNSUP}_encoder_output"
                ),
            ],
            name=f"{InputModelNames.SPECTRUM_UNSUP}_encoder",
        )

        model_decoder1 = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(
                    8 * 64, activation="relu"
                ),  # Matches encoder1's last conv output (8, 64)
                tf.keras.layers.Reshape((8, 64)),
                # Transposed Conv Block 1
                # Transposed Conv Block 1
                tf.keras.layers.Conv1DTranspose(
                    64, 3, activation="relu", padding="same"
                ),
                tf.keras.layers.UpSampling1D(2),  # Output: (16, 64)
                # Transposed Conv Block 2
                tf.keras.layers.Conv1DTranspose(
                    32, 3, activation="relu", padding="same"
                ),
                tf.keras.layers.UpSampling1D(2),  # Output: (32, 32)
                # Final reconstruction
                tf.keras.layers.Conv1D(8, 3, activation="sigmoid", padding="same"),
                tf.keras.layers.Reshape(
                    (32, 8, 1), name=f"{InputModelNames.SPECTRUM_UNSUP}_decoder_output"
                ),
            ],
            name=f"{InputModelNames.SPECTRUM_UNSUP}_decoder",
        )

        spectrum_index = config.train_parameters.learningModels.index(
            InputModelNames.SPECTRUM_UNSUP
        )
        inputs[spectrum_index] = input1
        encoders[spectrum_index] = model_encoder1(input1)
        decoders[spectrum_index] = model_decoder1

    if InputModelNames.SCATTERING_UNSUP in config.train_parameters.learningModels:
        input2 = tf.keras.layers.Input(
            shape=(120, 24, 1), name=f"{InputModelNames.SCATTERING_UNSUP}_input"
        )
        model_encoder2 = tf.keras.Sequential(
            [
                tf.keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.MaxPooling2D((2, 2), padding="same"),
                # Conv Block 2
                tf.keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.MaxPool2D((2, 2), padding="same"),
                # Dense Compression
                tf.keras.layers.Flatten(
                    name=f"{InputModelNames.SCATTERING_UNSUP}_encoder_output"
                ),
            ],
            name=f"{InputModelNames.SCATTERING_UNSUP}_encoder",
        )

        model_decoder2 = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(30 * 6 * 64, activation="relu"),
                tf.keras.layers.Reshape((30, 6, 64)),
                # Transposed Conv Block 1
                tf.keras.layers.Conv2DTranspose(
                    64, (3, 3), activation="relu", padding="same"
                ),
                tf.keras.layers.UpSampling2D((2, 2)),
                # Transposed Conv Block 2
                tf.keras.layers.Conv2DTranspose(
                    32, (3, 3), activation="relu", padding="same"
                ),
                tf.keras.layers.UpSampling2D((2, 2)),
                # Final reconstruction
                tf.keras.layers.Conv2D(
                    1,
                    (3, 3),
                    activation="sigmoid",
                    padding="same",
                    name=f"{InputModelNames.SCATTERING_UNSUP}_decoder_output",
                ),
            ],
            name=f"{InputModelNames.SCATTERING_UNSUP}_decoder",
        )

        scattering_index = config.train_parameters.learningModels.index(
            InputModelNames.SCATTERING_UNSUP
        )
        inputs[scattering_index] = input2
        encoders[scattering_index] = model_encoder2(input2)
        decoders[scattering_index] = model_decoder2

    if InputModelNames.LIFETIME_UNSUP in config.train_parameters.learningModels:
        input3 = tf.keras.layers.Input(
            shape=(64, 4), name=f"{InputModelNames.LIFETIME_UNSUP}_input"
        )
        model_encoder3 = tf.keras.Sequential(
            [
                tf.keras.layers.Reshape((64, 4)),  # Input shape: (64, 4, 1)
                # Conv Block 1
                tf.keras.layers.Conv1D(32, 3, activation="relu", padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.MaxPool1D(2),  # Output: (32, 32)
                # Conv Block 2
                tf.keras.layers.Conv1D(64, 3, activation="relu", padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.MaxPool1D(2),  # Output: (16, 64)
                # Conv Block 3
                # Dense Compression
                tf.keras.layers.Flatten(
                    name=f"{InputModelNames.LIFETIME_UNSUP}_encoder_output"
                ),
            ],
            name=f"{InputModelNames.LIFETIME_UNSUP}_encoder",
        )

        model_decoder3 = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(
                    16 * 64, activation="relu"
                ),  # Matches encoder3's last conv output (8, 128)
                tf.keras.layers.Reshape((16, 64)),
                # Transposed Conv Block 1
                # Transposed Conv Block 2
                tf.keras.layers.Conv1DTranspose(
                    64, 3, activation="relu", padding="same"
                ),
                tf.keras.layers.UpSampling1D(2),  # Output: (32, 64)
                # Transposed Conv Block 3
                tf.keras.layers.Conv1DTranspose(
                    32, 3, activation="relu", padding="same"
                ),
                tf.keras.layers.UpSampling1D(2),  # Output: (64, 32)
                # Final reconstruction
                tf.keras.layers.Conv1D(4, 3, activation="sigmoid", padding="same"),
                tf.keras.layers.Reshape(
                    (64, 4), name=f"{InputModelNames.LIFETIME_UNSUP}_decoder_output"
                ),
            ],
            name=f"{InputModelNames.LIFETIME_UNSUP}_decoder",
        )

        lifetime_index = config.train_parameters.learningModels.index(
            InputModelNames.LIFETIME_UNSUP
        )
        inputs[lifetime_index] = input3
        encoders[lifetime_index] = model_encoder3(input3)
        decoders[lifetime_index] = model_decoder3

    if InputModelNames.SIZE in config.train_parameters.learningModels:
        input4 = tf.keras.Input(shape=(1,), name=f"{InputModelNames.SIZE}_input")
        model_encoder4 = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(
                    4,
                    activation="relu",
                    kernel_initializer="lecun_normal",
                    kernel_regularizer="l2",
                ),
                tf.keras.layers.Dropout(0.3),
            ],
            name=f"{InputModelNames.SIZE}_encoder",
        )

        model_decoder4 = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(
                    2,
                    activation="relu",
                    kernel_initializer="lecun_normal",
                    kernel_regularizer=tf.keras.regularizers.l2(0.01),
                ),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(
                    1,
                    activation="linear",
                    name=f"{InputModelNames.SIZE}_decoder_output",
                ),
            ],
            name=f"{InputModelNames.SIZE}_decoder",
        )

        size_index = config.train_parameters.learningModels.index(InputModelNames.SIZE)
        inputs[size_index] = input4
        encoders[size_index] = model_encoder4(input4)
        decoders[size_index] = model_decoder4

    if len(inputs) != len(config.train_parameters.learningModels):
        raise ValueError("Model not found")

    merged = tf.keras.layers.Concatenate()(encoders)

    latent_output = tf.keras.layers.Dense(16, activation="relu")(merged)

    loss_weights = {}
    metrics = {
        f"{key}_decoder": ["mse", "mae"]
        for key in config.train_parameters.learningModels
    }
    losses = {f"{key}_decoder": "mse" for key in config.train_parameters.learningModels}
    for i in range(0, len(inputs)):
        loss_weight = 1 / get_spatial_size(inputs[i])
        loss_weights[f"{config.train_parameters.learningModels[i]}_decoder"] = (
            loss_weight
        )

        decoders[i] = decoders[i](latent_output)

    model_ae = tf.keras.Model(inputs=inputs, outputs=decoders)
    model_ae.compile(
        loss=losses,
        optimizer=tf.keras.optimizers.AdamW(
            learning_rate=config.train_parameters.lr,
            weight_decay=config.train_parameters.weight_decay,
        ),
        # loss_weights=loss_weights,
        metrics=metrics,
    )

    model_ae.summary(print_fn=logging.getLogger().info)
    losses_info = ", ".join(f"{key}: {value}" for key, value in loss_weights.items())
    logging.info(f"Loss weights adapted: {losses_info}")

    return model_ae

DEFAULT_TRAIN_PARAMS_TEXT = "Optional. When not set defaults will be taken. Note: action of change and overwrite is treated as defaults update. When enabled, changed and disabled the default parameters would not be overwritten."
EPOCHS_TRAIN_PARAMS_TEXT = "How many times training will be looped"
EARLY_STOPPING_PATIENCE_TRAIN_PARAMS_TEXT = "How many epochs to wait till training will be stopped, when min delta progress not obtained."
EARLY_STOPPING_MIN_DELTA_TRAIN_PARAMS_TEXT = (
    "Minimal progress increase after which training is stopped."
)
LR_TRAIN_PARAMS_TEXT = "Step size during objective function optimization. When too high can leap over the optimum, too low causes search too slow. Can be combined with learning rate reducer section."
MIN_LR_TRAIN_PARAMS_TEXT = (
    "Limit at which training will stop when learning rate will decrease below it."
)
WEIGHT_DECAY_TRAIN_PARAMS_TEXT = "Regularization coefficient to prevent overfitting. Additional penalty for big weights."
MIN_DELTA_TRAIN_PARAMS_TEXT = "Minimal progress below which patience epochs are count. E.g. if min delta equals 0.2, if accuracy increase is below that value for patience epochs learning rate will be decreased by decrease factor."
DECREASE_FACTOR_TRAIN_PARAMS_TEXT = (
    "When patience will be crossed decrease learning rate multiplier."
)
REDUCER_PATIENCE_TRAIN_PARAMS_TEXT = "How many epoch to wait to decrease learning rate by factor, when min delta progress not obtained."

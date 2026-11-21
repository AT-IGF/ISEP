DEFAULT_TRAIN_PARAMS_TEXT = "Optional. When not set defaults will be taken. Note: action of change and overwrite is treated as defaults update. When enabled, changed and disabled the default parameters would not be overwritten."
EPOCHS_TRAIN_PARAMS_TEXT = "How many times training will be looped"
EARLY_STOPPING_PATIENCE_TRAIN_PARAMS_TEXT = "How many epochs to wait till training will be stopped, when min delta progress not obtained."
EARLY_STOPPING_MIN_DELTA_TRAIN_PARAMS_TEXT = (
    "Min delta. Minimal decrease of the validation loss counted as progress."
)
LR_TRAIN_PARAMS_TEXT = "Step size during objective function optimization. When too high can leap over the optimum, too low causes search too slow. Can be combined with learning rate reducer section."
MIN_LR_TRAIN_PARAMS_TEXT = (
    "Lower bound below which the learning rate will not be decreased."
)
WEIGHT_DECAY_TRAIN_PARAMS_TEXT = "Regularization coefficient to prevent overfitting. Additional penalty for big weights."
MIN_DELTA_TRAIN_PARAMS_TEXT = "Minimal progress below which patience epochs are count. E.g. if min delta equals 0.2 and the monitored metric improves by less than that value for patience epochs, the learning rate will be decreased by decrease factor."
DECREASE_FACTOR_TRAIN_PARAMS_TEXT = (
    "Multiplier by which the learning rate is decreased when patience is exceeded."
)
REDUCER_PATIENCE_TRAIN_PARAMS_TEXT = "How many epoch to wait to decrease learning rate by factor, when min delta progress not obtained."

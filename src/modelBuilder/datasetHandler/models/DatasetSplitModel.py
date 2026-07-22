from dataclasses import dataclass

@dataclass()
class DatasetSplitModel:
    X_train: list
    X_test: list
    y_train: list
    y_test: list
    X_val: list
    y_val: list
    feature_models_train: list | None
    feature_models_test: list | None
    feature_models_val: list | None
    sets_names: list[str]

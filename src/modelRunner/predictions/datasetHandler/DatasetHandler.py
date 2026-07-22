from src.common.rawData.datasets import get_set_by_feature
from src.modelBuilder.models import FeatureModel


def get_unlabeled_dataset(feature_models: list[FeatureModel], keras_model, suffix=""):
    X = []
    for feature_model in feature_models:
        subset = []
        for name in keras_model.input_names:
            subset.append(feature_model[name.replace(suffix, '')])
        X.append(subset)

    return get_set_by_feature(X)

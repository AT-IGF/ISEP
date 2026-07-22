
import logging
import numpy as np

from src.common.rawData.features import FeatureModel
from src.common.rawData.datasets import get_set_by_feature
from src.modelBuilder.datasetHandler.models import DatasetSplitModel, DatasetModel
from sklearn.model_selection import train_test_split

def verify_if_test_timestamp_in_train(train_times, val_times, test_times, veryfi_test_set_leaks=False):
    from time import time
    logger = logging.getLogger()
    start = time()
    if veryfi_test_set_leaks != True:
        logger.info("Veryfying test set leaks skipped. To turn it on set 'veryfi_test_set_leaks' flag to 'true'")
        return
    logger.info("Veryfying test set leaks in train set")
    for test_time in test_times:
        if test_time in train_times:
            raise ValueError(f"Ivalid dataset found. Train set leak into test set. Reason: duplicated timestamps")
    logger.info("Veryfying test set leaks in validation set")
    for test_time in test_times:
        if test_time in val_times:
            raise ValueError(f"Ivalid dataset found. Validation set leak into test set. Reason: duplicated timestamps")
    logger.info("Veryfying validation set leaks in train set")
    for val_time in val_times:
        if val_time in train_times:
            raise ValueError(f"Ivalid dataset found. Validation set leak into test set. Reason: duplicated timestamps")
    stop = time()
    logger.info(f"No set leak found. Verified in {stop-start:.0f} seconds")
        
    
def train_test_validation_split(dataset: DatasetModel, train_ratio=0.70, test_ratio=0.15, validation_ratio=0.15, veryfi_test_set_leaks=False):
    if round(train_ratio + test_ratio + validation_ratio, 2) != 1:  # round due to float number precision
        raise ValueError("Train test validation split does not sum to 1")

    X_train, X_test, y_train, y_test, times_train, times_test, feature_models_train, feature_models_test = train_test_split(dataset.data_X, dataset.data_y, dataset.times, dataset.feature_models, test_size=1 - train_ratio, random_state=42, stratify=dataset.data_y)
    X_val, X_test, y_val, y_test, times_val, times_test, feature_models_val, feature_models_test = train_test_split(X_test, y_test, times_test, feature_models_test, test_size=test_ratio/(test_ratio + validation_ratio), random_state=42)
    
    verify_if_test_timestamp_in_train(train_times=np.array(times_train), val_times=np.array(times_val), test_times=np.array(times_test), veryfi_test_set_leaks=veryfi_test_set_leaks)
    return DatasetSplitModel(
        X_train = get_set_by_feature(X_train),
        X_test = get_set_by_feature(X_test),
        X_val = get_set_by_feature(X_val),
        y_train = np.array(y_train),
        y_test = np.array(y_test),
        y_val = np.array(y_val),
        feature_models_train=np.array(feature_models_train),
        feature_models_test=np.array(feature_models_test),
        feature_models_val=np.array(feature_models_val),
        sets_names = dataset.sets_names
    )
    
def train_validation_split(dataset: DatasetModel, train_ratio=0.823529412, validation_ratio=0.176470588, dataset_test: DatasetModel=None, veryfi_test_set_leaks=False):
    if round(train_ratio + validation_ratio, 2) != 1:  # round due to float number precision
        raise ValueError("Train test validation split does not sum to 1")
    if dataset_test == None or len(dataset_test.data_X) == 0 or len(dataset_test.data_y) == 0 or len(dataset_test.times) == 0:
        raise ValueError("Test set is required")

    X_train, X_val, y_train, y_val, times_train, times_val = train_test_split(dataset.data_X, dataset.data_y, dataset.times, test_size=1 - train_ratio, random_state=42, stratify=dataset.data_y)

    verify_if_test_timestamp_in_train(train_times=np.array(times_train), val_times=np.array(times_val), test_times=np.array(dataset_test.times), veryfi_test_set_leaks=veryfi_test_set_leaks)
    return DatasetSplitModel(
        X_train = get_set_by_feature(X_train),
        X_test = get_set_by_feature(dataset_test.data_X),
        X_val = get_set_by_feature(X_val),
        y_train = np.array(y_train),
        y_test = np.array(dataset_test.data_y),
        y_val = np.array(y_val),
        feature_models_train=None,
        feature_models_test=None,
        feature_models_val=None,
        sets_names = dataset.sets_names
    )


def get_dataset(feature_models: list[FeatureModel], learningModels: list[str]):
    X = []
    for feature_model in feature_models:
        subset = []
        for learningModel in learningModels:
            subset.append(feature_model[learningModel])
        X.append(subset)

    y, times, x, types = zip(*[(x.type_idx, x.time, x, x.type) for x in feature_models])

    return DatasetModel(
        data_X=X, 
        data_y=y,
        times = times,
        feature_models=x,
        types=set(types),
        sets_names=learningModels)

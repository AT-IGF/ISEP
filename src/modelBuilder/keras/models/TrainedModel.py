from dataclasses import dataclass
from typing import Any

from src.modelBuilder.keras.helpers import TfrecordGenerator
from src.modelBuilder.datasetHandler.models import DatasetSplitModel
import tensorflow as tf

@dataclass()
class TrainedModel:
    model: Any
    dataset: TfrecordGenerator
    
    def get_test_dataset(self):
        test_dataset = self.dataset.get_test_dataset()
        return self.dataset.unpack_dataset(test_dataset, input_name="X_test", label_name="y_test")
    
    def get_validation_dataset(self):
        train_dataset = self.dataset.get_validation_dataset()
        return self.dataset.unpack_dataset(train_dataset, input_name="X_val", label_name="y_val")
    
    def get_train_dataset(self):
        train_dataset = self.dataset.get_train_dataset()
        return self.dataset.unpack_dataset(train_dataset, input_name="X_train", label_name="y_test")
    
    def get_set_names(self):
        train_dataset = self.get_train_dataset()
        return train_dataset.X_train.keys()
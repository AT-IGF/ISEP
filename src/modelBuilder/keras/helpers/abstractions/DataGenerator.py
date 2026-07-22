from abc import ABC, abstractmethod
import tensorflow as tf

class DataGenerator(ABC):
    @property
    @abstractmethod
    def extension(self) -> list[str]:
        raise NotImplementedError("Extension type has to be implemented")
    
    @abstractmethod
    def get_train_dataset(self) -> tf.data.TFRecordDataset:
        pass      
            
    @abstractmethod
    def get_validation_dataset(self) -> tf.data.TFRecordDataset:
        pass      

    @abstractmethod
    def verify_validation_set_leaks_if_enabled(self):
        pass
    
    @abstractmethod
    def yield_dataset_from_path(self, path, batch_size, suffixes=['_input', "_decoder"], column_names=None):
        pass

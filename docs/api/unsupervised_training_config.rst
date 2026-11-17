Unsupervised Training Config
============================

Configuration passed to :func:`isep.train_unsupervised_model`.

.. currentmodule:: isep.configs

.. autoclass:: UnsupervisedTrainingConfig

Nested models
-------------

.. currentmodule:: isep.configs.unsupervisedTraining

Training
~~~~~~~~

.. autoclass:: TrainParametersModel

.. autoclass:: EarlyStoppingModel
    :no-index:

.. autoclass:: LearningRateReducerModel
    :no-index:

Verification
~~~~~~~~~~~~

.. autoclass:: VerifyModel

Clustering
~~~~~~~~~~

.. autoclass:: ClusterParameterModel

.. autoclass:: UmapModel

.. autoclass:: HdbscanModel

.. autoclass:: KMeansModel

.. autoclass:: ClustererModel

.. autoclass:: AnomalyDetectorModel
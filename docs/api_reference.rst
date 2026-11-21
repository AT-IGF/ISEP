Python API Reference
====================

This section provides documentation for the Python API of ISEP.
The functions can be used independently of the graphical
user interface in Python scripts and Jupyter notebooks.

All functions are accessible through the ``isep`` module and accept configuration in two ways:

* positional arguments - configuration objects, e.g. ``SupervisedTrainingConfig(...)`` or the general
  configuration, which are saved as a whole,
* keyword arguments - single fields of the configuration of the given function, listed next to it below,
  e.g. ``isep.train_supervised_model(model_save_name="model_1")``.

Configuration is saved between runs, so fields that are not given keep their values from the previous run.
To get repeatable results, pass full configuration objects.

.. note::

   The :doc:`general configuration <api/general_config>` (:class:`~isep.configs.PathsConfig` and
   :class:`~isep.configs.TypesConfig`) is shared by all functions. Pass it together with the first task,
   e.g. ``isep.train_supervised_model(PathsConfig(...), TypesConfig(...), SupervisedTrainingConfig(...))``.

Data Viewer
-----------

Functions for visualizing individual particle measurements
and aggregated particle data.

.. autofunction:: isep.plot_single_sample

   Keyword arguments: fields of :class:`~isep.configs.SingleSampleConfig`, see :doc:`api/single_sample_config`.

.. autofunction:: isep.plot_aggregated_samples

   Keyword arguments: fields of :class:`~isep.configs.MultipleSamplesConfig`, see :doc:`api/multiple_samples_config`.


Model Builder
-------------

Functions for preparing training data and training
supervised and unsupervised models.

.. autofunction:: isep.scale_model_data

   Keyword arguments: fields of :class:`~isep.configs.ModelDataScalerConfig`, see :doc:`api/model_data_scaler_config`.

.. autofunction:: isep.train_supervised_model

   Keyword arguments: fields of :class:`~isep.configs.SupervisedTrainingConfig`, see :doc:`api/supervised_training_config`.

.. autofunction:: isep.train_unsupervised_model

   Keyword arguments: fields of :class:`~isep.configs.UnsupervisedTrainingConfig`, see :doc:`api/unsupervised_training_config`.


Predictions Runner
------------------

Functions for generating predictions using trained models.

.. autofunction:: isep.run_predictions

   Keyword arguments: fields of :class:`~isep.configs.PredictionsRunnerConfig`, see :doc:`api/model_inference_config`.


Predictions Mapper
------------------

Functions for summarizing predictions over time spans and presenting them as plots.

.. autofunction:: isep.map_predictions

   Keyword arguments: fields of :class:`~isep.configs.PredictionsMapperConfig`, see :doc:`api/predictions_mapper_config`.

.. _python-api-configs:

Configs
-------

Configuration classes passed to the functions above. Every page lists all fields with their types,
default values and descriptions.

.. toctree::
   :maxdepth: 1
   :hidden:

   api/general_config
   api/single_sample_config
   api/multiple_samples_config
   api/model_data_scaler_config
   api/supervised_training_config
   api/unsupervised_training_config
   api/model_inference_config
   api/predictions_mapper_config

* :doc:`api/general_config` - pollen types and the path to the labeled samples.
* :doc:`api/single_sample_config` - which pollen types and modalities to plot.
* :doc:`api/multiple_samples_config` - modality to aggregate.
* :doc:`api/model_data_scaler_config` - samples and filter used to fit the scaler.
* :doc:`api/supervised_training_config` - model name, scaler and training parameters.
* :doc:`api/unsupervised_training_config` - training, verification and clustering.
* :doc:`api/model_inference_config` - model, pollen types and measurements to predict.
* :doc:`api/predictions_mapper_config` - time spans, thresholds and plots.
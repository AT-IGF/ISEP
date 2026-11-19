.. _python-api-entry-points:

Public Python Entry Points
==========================

The ``isep`` package exposes seven public task functions. Import them from ``isep``; the related
configuration classes are exported from ``isep.configs``.

.. list-table:: Public task functions and configurations
   :header-rows: 1
   :widths: 28 35 37

   * - Task
     - Python function
     - Configuration class
   * - Single-sample inspection
     - ``isep.plot_single_sample``
     - ``isep.configs.SingleSampleConfig``
   * - Aggregated-sample inspection
     - ``isep.plot_aggregated_samples``
     - ``isep.configs.MultipleSamplesConfig``
   * - Model-data scaling
     - ``isep.scale_model_data``
     - ``isep.configs.ModelDataScalerConfig``
   * - Supervised training
     - ``isep.train_supervised_model``
     - ``isep.configs.SupervisedTrainingConfig``
   * - Unsupervised training
     - ``isep.train_unsupervised_model``
     - ``isep.configs.UnsupervisedTrainingConfig``
   * - Model inference
     - ``isep.run_predictions``
     - ``isep.configs.PredictionsRunnerConfig``
   * - Prediction mapping
     - ``isep.map_predictions``
     - ``isep.configs.PredictionsMapperConfig``

The general configuration (``isep.configs.PathsConfig`` and ``isep.configs.TypesConfig``) is shared by all
tasks and should be passed together with the first task.

Calling a task
--------------

All functions have the signature ``(*configs, **kwargs)``. Configuration objects are passed as positional
arguments, and single fields of the task configuration as keyword arguments.

.. code-block:: python

   import isep
   from isep.configs import Config, PredictionsRunnerConfig

   config = Config.get(PredictionsRunnerConfig)
   print(config)  # Inspect paths, model selections, and processing options.

   isep.run_predictions(config)

The functions return no value; results are saved to the paths given in the configuration.

How configuration works
-----------------------

Each task reads the current settings, applies the given configuration objects and field overrides, saves the updated configuration in the configuration files in the *resources* directory, and runs. The saved settings are used by the following tasks, also in later sessions, see :doc:`reproducibility <reproducibility>`.
Reproducible Analysis Workflows
===============================

ISEP tasks read their settings from configuration files in the *resources* directory, e.g. *resources/general.json* and *resources/modelBuilder/config.json*. Configuration objects and field overrides passed to a task are saved in these files before the task runs, so the settings are kept between runs and Python sessions.

Every field has a default value, so only the fields that differ from the defaults have to be given. A configuration object replaces the saved configuration as a whole, fields not set in the object take their default values. Keyword arguments change only the given fields, the remaining ones keep their values from the previous run. The log of every task, saved in *resources/<module>/logs*, records the input data paths, the main settings and the output paths of the run.

Tasks exchange data through files, e.g. the scaler fitted by :func:`isep.scale_model_data` is read by :func:`isep.train_supervised_model` from ``scaler_path``. A complete workflow, from data visualization to prediction mapping, is available in ``sample/sample_flow.py``. It runs on the bundled ``sample/PKL_Test.zip`` data (86 particles of two pollen types) and serves as a quick check that the installation works; the obtained results are not a model evaluation.
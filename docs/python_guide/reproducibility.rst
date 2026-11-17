Reproducible Analysis Workflows
===============================

ISEP tasks read their settings from configuration files. By default, a temporary configuration directory is created when ``isep`` is imported, so settings passed to one task are kept for the following tasks in the same Python session, but not between sessions.

To keep the configuration of an experiment together with its results, set the ``ISEP_CONFIG_DIR`` environment variable **before importing** ISEP:

.. code-block:: python

   import os
   from pathlib import Path

   config_dir = Path("experiments/run_001/config").resolve()
   config_dir.mkdir(parents=True, exist_ok=True)
   os.environ["ISEP_CONFIG_DIR"] = str(config_dir)

   import isep

The directory then holds the exact configuration used by every task. In a Jupyter notebook, restart the kernel to start from a clean configuration.

Tasks exchange data through files, e.g. the scaler fitted by :func:`isep.scale_model_data` is read by :func:`isep.train_supervised_model` from ``scaler_path``. A complete workflow, from scaling to prediction mapping, is available in ``samples/main.py``.
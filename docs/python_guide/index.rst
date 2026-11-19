Python User Guide
=================

This guide explains how to use the ISEP Python interface in scripts and Jupyter notebooks. It covers the
public, task-oriented functions exposed by the ``isep`` package.

The public functions in ``isep`` call the corresponding ISEP processing modules. Public functions
should be understood as individual tasks that read configured input files and write results or model
artifacts to disk. The :doc:`API Reference <../api_reference>` should be consulted before running the tasks.

Familiarity with the ISEP GUI may help users understand the available processing workflows, but it is not required to use the Python interface.

Prerequisites
-------------

* ISEP is installed according to the :doc:`installation <../getting_started/installation>` guide.
* You have input data available, either from ``sample/PKL_Test.zip`` or prepared using the ``sample/pklConverter`` utility.
* Run notebook examples with a kernel attached to the same Python environment as specified in the `Running from Source <https://github.com/AT-IGF/ISEP#running-from-source>`_ section of the ISEP repository.

Configuration and task execution
--------------------------------

ISEP exposes task-level functions such as ``isep.scale_model_data()`` and
``isep.run_predictions()``. Each accepts optional configuration objects and
keyword overrides. Without explicit overrides, execution uses the default configuration.

Logging
-------
Information about the processing steps and execution status is logged to the terminal, as shown in the example below. Users can easily locate output directories and identify potential errors.

.. code-block:: text

   2026-11-06 20:34:51,325 | INFO | Logging in: '<root>\ISEP\resources\dataViewer\logs\20261106.log'
   2026-11-06 20:34:51,325 | INFO | Python version='3.11.4 | packaged by Anaconda, Inc. | (main, Jul  5 2023, 13:47:18) [MSC v.1916 64 bit (AMD64)]'. (Implemented in 3.11.4)
   2026-11-06 20:34:51,325 | INFO | Current Python interpreter path: 'z:\Miniconda3\envs\myenv\python.exe'
   2026-11-06 20:34:51,326 | INFO | Configs cache on save is NOT invalidated
   2026-11-06 20:34:51,331 | INFO |  filter not set.
   2026-11-06 20:34:51,331 | INFO | should append callback is None, all types will read from raw files without filtering it
   2026-11-06 20:34:51,332 | INFO | Same type particles count is set to=2 with mode=STOP_ON_COUNT. If set to 'None' all particles will be taken
   2026-11-06 20:34:51,333 | INFO | Searching for files under path='E:\PKL_Test'
   2026-11-06 20:34:51,340 | INFO | Alnus: Started to process count=1
   2026-11-06 20:34:51,340 | INFO | Alnus: processed, count=2
   2026-11-06 20:34:51,341 | INFO | Alnus: left count=2
   2026-11-06 20:34:51,344 | INFO | ArrhinateRum: Started to process count=1
   2026-11-06 20:34:51,344 | INFO | ArrhinateRum: processed, count=2
   2026-11-06 20:34:51,344 | INFO | ArrhinateRum: left count=2
   2026-11-06 20:34:51,345 | INFO | Pollen types processing finished, excluded = []
   2026-11-06 20:34:51,345 | INFO | Random pickup frequency is set to=0. Value range=[0-1], 0-every particle, 0.5-every 2nd, etc.
   2026-11-06 20:34:51,345 | INFO | Same type particles to show count = 2
   2026-11-06 20:34:51,346 | INFO | Plotting: Alnus0
   2026-11-06 20:34:53,384 | INFO | (1/4) proceeded

Using ISEP from Jupyter
-----------------------

The same imports and task calls can be used in a Jupyter notebook. Settings passed to a task are saved in the configuration files, so they are also used after restarting the kernel, see :doc:`reproducibility <reproducibility>`.

Recommended workflow
--------------------

#. **Setup general settings** Set ``TypesConfig`` and ``PathsConfig`` to define pollen type classes and path to them. 
#. **Inspect measurements:** Visualize the input data and prefilter it if needed.
#. **Prepare training data:** Prepare the data and run the data-scaling task.
#. **Train a model:** Train, evaluate, and calibrate the model.
#. **Run predictions:** Run predictions on unseen measurements using the trained model.
#. **Visualize predictions:** Use the predictions mapper to visualize the outputs of the prediction task.

.. toctree::
   :maxdepth: 2

   api_entry_points
   data_preprocessing
   model_training
   model_inference
   prediction_mapping
   reproducibility

Where to find lower-level details
---------------------------------

The :doc:`API Reference <../api_reference>` describes the internal Python
modules, functions, and classes. For task-level usage, start with
:ref:`python-api-entry-points`. If your workflow requires direct manipulation
of arrays or intermediate model outputs, verify the corresponding lower-level
``src`` modules.
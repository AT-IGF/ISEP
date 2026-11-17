Quickstart
==========

This guide introduces the basic usage of ISEP through its
Python API. ISEP modules can be used directly in Python scripts
or Jupyter notebooks, without launching the graphical user
interface (GUI).

Prerequisites
-------------

Before proceeding, make sure that:

- ISEP is installed according to the :doc:`installation` guide.
- You have input data available, either from the ``sample/PKL_Test.zip`` archive or prepared using the
  ``sample/pklConverter`` utility.

Using the Python API
--------------------

ISEP provides a public Python API that exposes the main
functionalities of the application.

To verify that the API is accessible, run:

.. code-block:: bash

   python -c "import isep; print(isep.__all__)"

Alternatively, import the available functions directly
in a Python script or Jupyter notebook:

.. code-block:: python

   from isep import (
       plot_single_sample,
       plot_aggregated_samples,
       scale_model_data,
       train_supervised_model,
       train_unsupervised_model,
       run_predictions,
       map_predictions,
   )

Each function provides access to a specific ISEP module.
The complete list of functions and their configuration
is available in the :doc:`API Reference <../api_reference>`.


Running Your First Analysis
---------------------------

Required Directory Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before running an analysis, organize your input data
into the following directory structure:

.. code-block:: text

   <dataset_directory>/
   ├── pollen_type_1/
   │   ├── ...
   │   └── ...
   └── pollen_type_2/
       ├── ...
       └── ...

The root directory can have any name. Each subdirectory represents a pollen class and contains its
corresponding particle measurements. Subdirectory names are used as pollen type names in the configuration.
The ``sample/PKL_Test.zip`` archive already has this structure, with the ``Alnus`` and ``ArrhinateRum``
subdirectories.

Running analysis
~~~~~~~~~~~~~~~~

The following example plots the fluorescence spectrum of two particles of every pollen type. Extract
``sample/PKL_Test.zip`` to the *resources* directory, so that the samples are available under
*resources/PKL_Test*, and run:

.. code-block:: python

   from isep import plot_single_sample
   from isep.configs import PathsConfig, TypesConfig, SingleSampleConfig
   from isep.configs.singleSample import SingleSamplePlotModel

   if __name__ == "__main__":
       plot_single_sample(
           PathsConfig(zip_files_rel_path="PKL_Test"),
           TypesConfig(pollen_types=["Alnus", "ArrhinateRum"]),
           SingleSampleConfig(
               pollen_types_to_show=["Alnus", "ArrhinateRum"],
               same_type_count=2,
               spectrum_plot=SingleSamplePlotModel(show=True),
           ),
       )

The general configuration (``PathsConfig`` and ``TypesConfig``) defines where the labeled samples are
located and which pollen types are used. The function executes the corresponding ISEP workflow
without requiring interaction with the GUI. The plots are displayed and saved in *resources/dataViewer/out*.

For all available configuration options, see :doc:`Single Sample Config <../api/single_sample_config>`.


Using the Graphical Interface
-----------------------------

ISEP can also be launched through its graphical user
interface:

.. code-block:: bash

   python -m isep.ui

The GUI provides predefined workflows for data visualization,
model training, prediction, and result analysis.


Next Steps
----------

After completing this guide, explore the following sections:

- **Python User Guide** - step-by-step examples of ISEP workflows.
- **API Reference** - public functions and their configuration.
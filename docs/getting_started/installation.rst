Installation
============

Requirements
------------

- Python 3.11 or 3.12 - `download <https://www.python.org/downloads/>`_
- pip (Python package installer) - installed with Python

Training on a GPU requires CUDA. On Windows, TensorFlow does not support CUDA natively, so WSL2 is required;
see the `TensorFlow installation guide <https://www.tensorflow.org/install/pip>`_. Without CUDA, all tasks
run on the CPU.

It is recommended to install ISEP in a virtual environment:

.. code-block:: bash

   python -m venv isep-env

Activate it with ``isep-env\Scripts\activate`` on Windows or ``source isep-env/bin/activate`` on Linux.

Installing with pip
-------------------

.. code-block:: bash

   pip install ISEP

Installing from Source
----------------------

Clone the ISEP repository and install it in editable mode, so that changes in the code take effect
without reinstalling:

.. code-block:: bash

   git clone https://github.com/AT-IGF/ISEP.git
   cd ISEP
   python -m pip install -e .

Verify Installation
-------------------

.. code-block:: bash

   python -c "import isep; print(isep.__all__)"

The command prints the available :ref:`Python API functions <python-api-entry-points>`.

Launching the GUI
-----------------

.. code-block:: bash

   python -m isep.ui
..
   solo-sis-loader documentation master file, created by
   sphinx-quickstart on Mon Jan 9 00:22:34 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

*****************************
SolO-SIS-Loader Documentation
*****************************


Installing and Running
======================

To install and run this package, Python >=3.10 or later is required. We recommend creating and working with this package in a virtual environment and installing the package with pip.

.. code-block:: bash

  # Create the virtual environment using conda
  conda create --name solo-sis-loader python=3.10

  # Activate the environment
  conda activate solo-sis-loader

  # Install the required packages using pip
  pip install solo-sis-loader

The package can also be installed directly from the github repository using the latest developed version (not recomended).

.. code-block:: bash

    pip install git+https://github.com/AthKouloumvakos/SolO-SIS-Loader


.. toctree::
   :caption: Getting Started
   :maxdepth: 1

   installing

.. toctree::
   :caption: Examples
   :maxdepth: 1

   _examples/index.rst

Package materials_commons
=========================

The package **materials_commons** consists of three parts: the Python AIP, **materials_commons.api**,
the Command Line Interface, **materials_commons.cli**, and a newly developend set of scripts for
Extraction Transformation and Loading (ETL) of experiment workflows from well formatted Excel
spreadsheets, **materials_commons.etl**. The ETL part is in pre-alpha development, subject to
frequent change and (therefore) excluded from this documentation. Contact the developers and/or
review the code at the GitHub site, if you are interested in details.

This package relates to the original Materials Commons service running at MaterialsCommons.org,
that is https://materialscommons.org. The server code is available on
GitHub at https://github.com/materials-commons/materialscommons.org.
Full documentation is also available: https://materials-commons.github.io/ .

To Install
----------

The Materials Commons package is available as a PyPI package, and therefore can easily be installed:

.. code-block:: sh

    pip install materials_commons


The Python API (materials_commons.api)
--------------------------------------

The Materials Commons Python API is an
interface to the REST server on an host running the
Materials Commons service. As above, the original Materials Commons
service is running at https://materialscommons.org .
See the docs at (https://materials-commons.github.io/python-api/) for
an introduction and instructions on how to use this Python API

Documentation for the Python API module:
:doc:`index_api`

The Command Line Interface (materials_commons.cli)
--------------------------------------------------

The Materials Commons CLI program "mc" makes use of the CLI module to
enable project and experiment creation, file upload/download, and searching
for and querying information about samples and processes from the command line.
Developers can also use the CLI module to customize the "mc"
program via plugins that create samples and processes for specific applications.
A tutorial on how to customize the CLI is currently under development.

Documentation for the CLI module:
:doc:`materials_commons.cli`


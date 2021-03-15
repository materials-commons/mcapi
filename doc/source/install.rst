.. install.rst

Installation
============

Requirements
------------

Installation and use of ``materials_commons.api`` requires Python 3, for instance from https://www.python.org.


Install using pip
-----------------

::

    pip install materials-commons-api

or, to install in your user directory:

::

   	pip install --user materials-commons-api



Install from source
-------------------

1. Clone the repository:

::

    cd /path/to/
    git clone https://github.com/materials-commons/mcapi.git
    cd mcapi

2. Checkout the branch/tag containing the version you wish to install. Latest is ``master``:

::

    git checkout master

3. From the root directory of the repository:

::

    pip install .

or, to install in your user directory:

::

   		pip install --user .

If installing to a user directory, you may need to set your ``PATH`` to find the
installed scripts. This can be done using:

::

   		export PATH=$PATH:`python -m site --user-base`/bin

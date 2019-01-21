# mcapi
Materials Commons API [![CI Test Status](https://travis-ci.org/materials-commons/mcapi.svg?branch=master)](https://travis-ci.org/materials-commons/mcapi/branches)

The "mature" version of the API in in the python directory. This 'master' of this directory
has also been released as a package in the Python Software
Foundation's python library: [materials-commons](https://pypi.python.org/pypi/materials-commons).

The other directories ('julia' and 'R') are stubs for exploration and are not viable at this point in time.
API for MaterialsCommons.org
============================

This is the python version of an API to
[MaterialsCommons.org](https://github.com/materials-commons/materialscommons.org). 
The source code is available at 
https://github.com/materials-commons/mcapi/tree/master/python.

It consists of three packages/modules: 
* **mcapi** - the main interface to the API
* **mcapi.cli** - a command line interface (see scripts/mc)
* **demo_project** - a module for building a demo project in a designated 
Materials Commons server, for a given user, using the API
 
In addition there is a distribution package (which includes 
the demo_project and mcapi modules): **mcapi_dist**.

For testing: see **extres/test/RunTests.md**
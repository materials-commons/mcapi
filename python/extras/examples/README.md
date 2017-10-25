Examples using the Python API
=============================

The examples in this folder are intended to illustrate how the Python API might be used.
They are instructive only, basically a starting place, and not meant to be recommendation of
best practices or production code: caveat emptor.

To run these examples, you will need to have access to a materials commons account (or a local
instance of materials commons and an account on that site): see the documentation on running the
examples as part of the Python API documentation:
**https://materials-commons.github.io/python-api/**.

Simple Demo Project
-------------------

This script shows how you might construct a project with one experiment, that has a simple workflow:
create a sample, subject it to low-frequency fatigue, and examine is micro-structure with an SEM scan.
While normally these steps would also have setup or measurement properties, and (possibly) attached
files, in the interest of simplicity, we will forgo these embellishments.

The example is articulated in the file **simple_demo_project.py** and explained
further in the comments therein.

Full Demo Project
-----------------

This script shows how to construct the demo project that is (also) constructed when one
selects the "Build Demo Project" on the projects home page of the Materials Commons site:
https://materialscommons.org/

Note: this example actually uses a module of the Python API project called demo_project,
so the bulk of the code in NOT in this folder (the **examples** folder) but is, instead
in the folder for that modules; in particular see
**https://github.com/materials-commons/mcapi/blob/master/python/demo_project/demo_project.py**
or corresponding local file (in that case that you have download or cloned the content).

Build from Excel Spreadsheet
----------------------------

An interesting use of the Python API, is the automatic building of Materials Commons projects
from structured description of your project. To illustrate this, we build a project from the
input of a spread sheet that described a series of experiments and their measurements.
The data is fake! The process, however, illustrated a useful usage.

This example is shown in the **build_project_from_excel_sheet.py** and explained
further in the comments therein.
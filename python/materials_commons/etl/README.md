Using ETL scripts.
==================

Getting started (rough draft)
-----------------------------

Prerequisites

First, install python3. https://wiki.python.org/moin/BeginnersGuide/Download

Then, use the following to set up and install the materials commons environment
* obtain a copy of your API key
    * log into https://materialscommons.org/
    * click on "Account Settings" in the right-hand pull-down menu (under you name)
    * click on "SHOW API KEY"
    * you will need to copy and save the API key into the configuration file described next
* create an API configuration file
    * the file's location is ~/.materialscommons/config.json
    * the file should contain:
        ```bash
        {
          "apikey": "your-api-key-see-above",
          "mcurl": "https://materialscommons.org/api"
        }
        ``` 
* Test that your configuration is working, but doing the following.
    * create and cd to a test directory
    * install the materials commons package in your python environment
        ```bash
        pip install materials_commons
        pip install openpyxl
        ```
    * create a python script, test.py, with the code in it:
        ```python
        from materials_commons.api import get_all_projects

        for project in get_all_projects:
            print(project.name)

        ```
    * if that code works you are ready to go
    
An example input file can be obtained from this location:
https://github.com/materials-commons/mcapi/blob/master/python/materials_commons/etl/input.xlsx

Just click on "download" link. 

For the commands, in the form illustrated below, I will assume that you have copied
this file, input.xlsx, to a test directory on your Desktop, e.g. ~/Desktop/test

Commands that I used to build project/experiment from spreadsheet and test results:

* To create from an excel spreadsheet, a project/experiment or add an experiment to an existing project
    Note, also creates a metadata file.
    ```bash
    python -m materials_commons.etl.input.main --input ~/Desktop/test/input.xlsx --metadata ~/Desktop/test/metadata.json
    ```

* To create an excel spreadsheet from a project/experiment and a metadata file 
    ```bash
    python -m materials_commons.etl.output.extract_spreadsheet --metadata ~/Desktop/test/metadata.json --file ~/Desktop/test/output.xlsx 
    ```

Using ETL scripts.
==================

Getting started (rough draft)
-----------------------------

Commands that I used to build project/experiment from spreadsheet and test results:

* To create from an excel spreadsheet, a project/experiment or add an experiment to an existing project
    Note, also creates a metadata file.
    ```bash
    python -m materials_commons.etl.input.main --input ~/Desktop/input.xlsx --json /Users/weymouth/Desktop/junk.json
    ```

* To create an excel spreadsheet from a project/experiment and a metadata file 
    ```bash
    python -m materials_commons.etl.output.extract_spreadsheet --metadata ~/Desktop/metadata.json
    ```

* To compare input and output excel spreadsheets using metadata.
    Note: arguments to script are hard coded, in early lines of file, at this time.
    ```bash
    python -m materials_commons.etl.output.compare_spreadsheets
    ```

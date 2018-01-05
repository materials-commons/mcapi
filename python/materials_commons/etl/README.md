Using ETL scripts.
==================

Getting started (rough draft)
-----------------------------

Commands that I used to build project/experiment from spreadsheet and test results:
* python -m materials_commons.etl.input.main --input ~/Desktop/input.xlsx --json /Users/weymouth/Desktop/junk.json
* python -m materials_commons.etl.output.extract_spreadsheet --metadata ~/Desktop/metadata.json
* python -m materials_commons.etl.output.compare_spreadsheets
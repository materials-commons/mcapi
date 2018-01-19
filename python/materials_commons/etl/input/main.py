import datetime
import os
import sys
import argparse
import openpyxl
from pathlib import Path
from .build_project import BuildProjectExperiment
from materials_commons.etl.common.worksheet_data import read_entire_sheet

local_path = '/Users/weymouth/Dropbox/MaterialCommons/Tracy_Jake_ETL/etl-input'
BASE_DIRECTORY = os.path.abspath(local_path)
HOME = str(Path.home())

def main(input, data_dir, json_path):
    wb = openpyxl.load_workbook(filename=input)
    sheet_name = wb.get_sheet_names()[0]
    ws = wb[sheet_name]
    print(wb.get_sheet_names(),sheet_name)
    builder = BuildProjectExperiment()
    builder.set_data(read_entire_sheet(ws))
    wb.close()
    builder.set_project_description("Project from excel spreadsheet: " + input
                            + "; using data from " + data_dir)
    builder.build(data_dir)
    builder.metadata.set_input_information(input, data_dir, json_path)
    builder.metadata.write(json_path)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_input_path = os.path.join(BASE_DIRECTORY, "input.xlsx")
    default_data_path = os.path.join(BASE_DIRECTORY, "data")
    default_json_path = os.path.join(HOME, "etl-data/mc_excel_description.json")

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('--input', type=str, default='',
                        help='Path to input EXCEL file - defaults to ' + default_input_path)
    parser.add_argument('--dir', type=str, default='',
                        help='Path to directory of data files - defaults to ' + default_data_path)
    parser.add_argument('--metadata', type=str, default='',
                        help='Path to metadata JSON file - defaults to' + default_json_path)
    args = parser.parse_args(argv[1:])

    if not args.input:
        args.input = default_input_path
    if not args.dir:
        args.dir = default_data_path
    if not args.metadata:
        args.metadata = default_json_path
    args.input = os.path.abspath(args.input)
    args.dir = os.path.abspath(args.dir)
    args.metadata = os.path.abspath(args.metadata)

    print("Path to input EXCEL file: " + args.input)
    print("Path to data file directory: " + args.dir)
    print("Path to metadata JSON file: " + args.metadata)

    main(args.input, args.dir, args.metadata)

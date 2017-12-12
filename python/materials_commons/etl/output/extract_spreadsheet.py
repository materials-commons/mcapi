from materials_commons.api import get_all_projects
import pprint

import datetime
import os
import sys
import argparse
import openpyxl

local_path = '/Users/weymouth/Dropbox/MaterialCommons/Tracy_Jake_ETL/etl-output'
BASE_DIRECTORY = os.path.abspath(local_path)

class ExtractExperimentSpreadsheet:
    def __init__(self):
        pass

    def extract(self,experiment):
        pass

def main(file_name,output_file_path):
    wb = openpyxl.load_workbook(filename=input)
    ws = wb['EPMA Results (Original)']
    builder = ExtractExperimentSpreadsheet()

    builder.read_entire_sheet(ws)
    wb.close()
    builder.set_description("Project from excel spreadsheet: " + input
                            + "; using data from " + data_dir)
    builder.build(data_dir)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_output_dir_path = os.path.join(BASE_DIRECTORY)

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('--dir', type=str, default='',
                        help='Path to output directory - defaults to ' + default_output_dir_path)
    args = parser.parse_args(argv[1:])

    if not args.input:
        args.input = default_input_path
    if not args.dir:
        args.dir = default_data_path
    args.input = os.path.abspath(args.input)
    args.dir = os.path.abspath(args.dir)

    print("Path to input EXCEL file: " + args.input)
    print("Path to data file directory: " + args.dir)

    main(args.input, args.dir)

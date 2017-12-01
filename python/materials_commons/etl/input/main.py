import datetime
import os
import sys
import argparse
import openpyxl
from .build_project import BuildProjectExperiment

local_path = '/Users/weymouth/Desktop/etl-input/'
BASE_DIRECTORY = os.path.abspath(local_path)


def main(input, data_dir):
    wb = openpyxl.load_workbook(filename=input)
    ws = wb['EPMA Results (Original)']
    builder = BuildProjectExperiment()
    builder.read_entire_sheet(ws)
    wb.close()
    builder.setDescription("Project from excel spreadsheet: " + input
                           + "; using data from " + data_dir)
    builder.build(data_dir)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_input_path = os.path.join(BASE_DIRECTORY, "input.xlsx")
    default_data_path = os.path.join(BASE_DIRECTORY, "data")

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('--input', type=str, default='',
                        help='Path to input EXCEL file - defaults to ' + default_input_path)
    parser.add_argument('--dir', type=str, default='',
                        help='Path to directory of data files - defaults to ' + default_data_path)
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

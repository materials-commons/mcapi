import datetime
import os
import sys
import argparse
from pathlib import Path
from .build_project import BuildProjectExperiment

local_path = '/Users/weymouth/Dropbox/MaterialCommons/Tracy_Jake_ETL/etl-input'
BASE_DIRECTORY = os.path.abspath(local_path)
HOME = str(Path.home())


def _verify_data_dir(dir_path):
    path = Path(dir_path)
    ok = path.exists() and path.is_dir()
    return ok


def _verify_input_path(input_path):
    path = Path(input_path)
    ok = path.exists() and path.is_file()
    return ok

def main(spread_sheet_path, data_dir, rename_flag):
    if not _verify_data_dir(data_dir):
        print("The Path to data file directory does not point to a user directory; exiting.")
        exit(-1)
    if not _verify_input_path(spread_sheet_path):
        print("The Path to the input Excel spreadsheet does not point to a file; exiting.")
        exit(-1)
    builder = BuildProjectExperiment()
    if (rename_flag):
        builder.set_rename_is_ok(rename_flag)
    builder.build(spread_sheet_path, data_dir)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_input_path = os.path.join(BASE_DIRECTORY, "input.xlsx")
    default_data_path = os.path.join(BASE_DIRECTORY, "data")
    default_json_path = os.path.join(HOME, "etl-data/mc_excel_description.json")

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('--input', type=str, default=default_input_path,
                        help='Path to input EXCEL file - defaults to ' + default_input_path)
    parser.add_argument('--dir', type=str, default=default_data_path,
                        help='Path to directory of data files - defaults to ' + default_data_path)
    parser.add_argument('--rename', action='store_true',
                        help='A flag that indicates that the experiment should be renamed when a name collision occurs')
    args = parser.parse_args(argv[1:])

    args.input = os.path.abspath(args.input)
    args.dir = os.path.abspath(args.dir)

    print("Path to input EXCEL file: " + args.input)
    print("Path to data file directory: " + args.dir)
    print("Flag indicating that previous experiments given name sould be renamed: " + str(args.rename))

    main(args.input, args.dir, args.rename)



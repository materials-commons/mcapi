import argparse
import datetime
import os
import sys
from pathlib import Path

from .build_project import BuildProjectExperiment


def _verify_data_dir(dir_path):
    path = Path(dir_path)
    ok = path.exists() and path.is_dir()
    return ok


def _verify_input_path(input_path):
    path = Path(input_path)
    ok = path.exists() and path.is_file()
    return ok


def main(spread_sheet_path, data_dir, rename_flag):
    if data_dir and (not _verify_data_dir(data_dir)):
        print("The Path to data file directory does not point to a user directory; exiting.")
        exit(-1)
    if not _verify_input_path(spread_sheet_path):
        print("The Path to the input Excel spreadsheet does not point to a file; exiting.")
        exit(-1)
    builder = BuildProjectExperiment()
    if rename_flag:
        builder.set_rename_is_ok(rename_flag)
    builder.build(spread_sheet_path, data_dir)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('input', type=str,
                        help='Path to input EXCEL file')
    parser.add_argument('--upload', type=str,
                        help='Path to directory of data files to upload - optional')
    parser.add_argument('--rename', action='store_true',
                        help='A flag that indicates that the experiment should be renamed when a name collision occurs')
    args = parser.parse_args(argv[1:])

    args.input = os.path.abspath(args.input)

    print("Path to input EXCEL file: " + args.input)
    if args.upload:
        args.upload = os.path.abspath(args.upload)
        print("Path to directory as sources of file upload: " + args.upload)
    else:
        print("Path to directory as sources of file upload, not specified. File upload suppressed")
    print("Flag indicating if there is a previous experiment with same name, it should be renamed: " + str(args.rename))

    main(args.input, args.upload, args.rename)

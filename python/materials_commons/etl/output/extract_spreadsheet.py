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

def main(args):
    builder = ExtractExperimentSpreadsheet()
    if not builder.setUpSpreadsheet(args.dir, args.file):
        print("Unable to create spreadsheet, " + args.file + ", in directory " + args.dir)
        exit(-1)
    builder.buildExperimentArray()
    builder.writeSpreadsheet()

if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_output_dir_path = os.path.join(BASE_DIRECTORY)
    default_file_name = "workflow.xlsx"

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Dump a project-experiment to a spreadsheer')
    parser.add_argument('--project', type=str, help="Project name")
    parser.add_argument('--experiment', type=str, help="Experiment name")
    parser.add_argument('--dir', type=str, default=default_output_dir_path,
                        help='Path to output directory')
    parser.add_argument('--file', type=str, default=default_file_name)
    args = parser.parse_args(argv[1:])

    if not args.project:
        print("Project name (--project) is required")
        exit(-1)
    if not args.experiment:
        print("Experiment name (--experiment) is required")
        exit(-1)
    args.dir = os.path.abspath(args.dir)

    if not os.path.isdir(args.dir):
        print("The given output file path, " + args.dir + ", is not a directory. Please fix.")
        exit(-1)

    if not args.file.endswith(".xlsx"):
        file = args.file + ".xlsx"

    print("Set up: Writing spreadsheet, " + args.file + ", to directory " + args.dir)
    print("From experiment '" + args.experiment + "' in project '" + args.project + "'")

    main(args)

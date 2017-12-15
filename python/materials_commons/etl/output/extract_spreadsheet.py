import argparse
import datetime
import os
import sys

import openpyxl

from materials_commons.api import get_all_projects

local_path = '/Users/weymouth/Desktop/etl-output'
BASE_DIRECTORY = os.path.abspath(local_path)


class ExtractExperimentSpreadsheet:
    def __init__(self, setup_args):
        self.dir = setup_args.dir
        self.file = setup_args.file
        self.output_path = None
        self.project_name = setup_args.project
        self.project = None
        self.experiment_name = setup_args.experiment
        self.experiment = None
        self.worksheet = None
        self.workbook = None
        self.data_row_list = []
        self.number_of_rows = 0
        self.number_of_cols = 0

    def build_experiment_array(self):
        print("Building data array")
        print("    " + self.project.name)
        print("    " + self.experiment.name)
        self.make_initial_left_col()

    def make_initial_left_col(self):
        self.data_row_list = [
            ["PROJ: " + self.project.name],
            ["EXP: " + self.experiment.name],
            [""],
            ["BEGIN_DATA"]
        ]

    def write_spreadsheet(self):
        print("Writing spreadsheet")
        print("    " + self.output_path)
        self.write_data_to_sheet()
        self.workbook.save(filename=self.output_path)
        self.workbook.close()

    def write_data_to_sheet(self):
        for row in range(0, len(self.data_row_list)):
            data_row = self.data_row_list[row]
            for col in range(0, len(data_row)):
                print("data: ", row, col, data_row[col])
                data_item = data_row[col]
                self.worksheet.cell(column=col+1, row=row+1, value=data_item)

    def verify_worksheet_creation(self):
        dir_path = os.path.abspath(self.dir)
        if not os.path.isdir(dir_path):
            print("The given path, " + self.dir + ", is not a directory")
            print("Resolved to: " + dir_path)
            return None
        ws = None
        try:
            dir_path = os.path.join(dir_path, self.file)
            wb = openpyxl.Workbook()
            ws = wb.worksheets[0]
            ws['A1'] = "PROJ: " + self.project.name
            ws['A2'] = "EXP: " + self.experiment.name
            wb.save(filename=dir_path)
            self.output_path = dir_path
        except:
            print("Unexpected error:", sys.exc_info()[0])
            ws = None
        self.worksheet = ws
        self.workbook = wb
        return ws

    def verify_experiment_exists(self):
        self._get_project_if_exits()
        if not self.project:
            print("Project not found in database: " + self.project_name)
            return None
        self._get_experiment_if_exits()
        if not self.experiment:
            print("Experiment not found in database: " + self.experiment_name)
            return None
        return self.experiment

    def _get_project_if_exits(self):
        projects = get_all_projects()
        probe = None
        for project in projects:
            if project.name == self.project_name:
                probe = project
        if not probe:
            return
        self.project = probe

    def _get_experiment_if_exits(self):
        if not self.project:
            return
        experiments = self.project.get_all_experiments()
        probe = None
        count = 0
        for experiment in experiments:
            if experiment.name == self.experiment_name:
                probe = experiment
        if not probe:
            return
        if count > 1:
            print("Exit! Found more the one experiment with name = ", self.experiment_name)
            return
        self.experiment = probe


def main(main_args):
    builder = ExtractExperimentSpreadsheet(main_args)
    if not builder.verify_experiment_exists():
        print("Unable to locate project and/or experiment: '"
              + main_args.project + "', '" + main_args.experiment + "'")
        exit(-1)
    if not builder.verify_worksheet_creation():
        print("Unable to open spreadsheet and/or worksheet, "
              + main_args.file + ", in directory " + main_args.dir)
        exit(-1)
    builder.build_experiment_array()
    builder.write_spreadsheet()


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

    print("Set up: writing spreadsheet, " + args.file)
    print("        to directory " + args.dir)
    print("Data from experiment '" + args.experiment + "' in project '" + args.project + "'")

    main(args)

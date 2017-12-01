import openpyxl
import argparse
import datetime
import os.path
from os import walk
import sys
from materials_commons.api import create_project, get_all_projects, get_all_templates

local_path = '/Users/weymouth/Desktop/etl-input/'
BASE_DIRECTORY = os.path.abspath(local_path)

class BuildProjectExperiment:
    def build(self, sheet, data_path):
        self.sheet = sheet
        self.source = self._readEntireSheet(sheet)

        self._setNames()
        if (self.project_name):
            print("Project: ",self.project_name)
        else:
            print("No project name found; check format. Quiting.")

        if (self.experiment_name):
            print("Experiment: ",self.experiment_name)
        else:
            print("No project name found; check format. Quiting.")

        self._setRowPositions()
        self._set_col_positions()

        print(self.start_sweep_col)
        print(self.end_sweep_col)

    def _setNames(self):
        self.project_name = ""
        self.experiment_name = ""
        text = self.source[0][0]
        if len(text) > 6 and text.startswith("PROJ: "):
            text = text[6:]
            text = text.strip("'")
            text = text.strip('"')
            self.project_name = text
        text = self.source[1][0]
        if len(text) > 5 and text.startswith("EXP: "):
            text = text[5:]
            text = text.strip("'")
            text = text.strip('"')
            self.experiment_name = text

    def _setRowPositions(self):
        self.header_end_row = 0
        self.data_start_row = 0
        index = 0
        for row in self.source:
            if len(row) > 0 and row[0] and row[0].startswith("BEGIN_DATA"):
                self.data_start_row = index
                break
            index += 1
        if self.data_start_row == 0:
            return
        index = 0
        for row in self.source:
            if len(row) > 0 and row[0] \
                    and (row[0].startswith("BEGIN_DATA") or row[0].startswith("COL_LABEL")):
                self.header_end_row = index
                break
            index += 1

    def _set_col_positions(self):
        self.start_sweep_col = 1
        self.end_sweep_col = 0
        first_row = self.source[0]
        index = 0
        for col in first_row:
            if str(col).startswith("END"):
                self.end_sweep_col = index
                break
            index += 1

    def _readEntireSheet(self, sheet):
        data = []
        for row in sheet.iter_rows():
            values = []
            for cell in row:
                values.append(cell.value)
            data.append(values)
        return data

def main(args):
    wb = openpyxl.load_workbook(filename=args.input, read_only=True)
    ws = wb['EPMA Results (Original)']
    builder = BuildProjectExperiment()
    builder.build(ws, args.dir)

#    print("Built project(s)...")
#    for project in builder.projects:
#        print(project.name)
    # builder.pp()

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

    main(args)

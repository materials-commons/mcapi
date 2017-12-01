import openpyxl
import argparse
import datetime
import os.path
import sys
from materials_commons.api import create_project, get_all_projects, get_all_templates

local_path = '/Users/weymouth/Desktop/etl-input/'
BASE_DIRECTORY = os.path.abspath(local_path)


class BuildProjectExperiment:
    def build(self, sheet, data_path):
        self.sheet = sheet
        self.source = self._readEntireSheet(sheet)

        self.data_path = data_path

        self._setNames()
        if (self.project_name):
            print("Project name: ", self.project_name)
        else:
            print("No project name found; check format. Quiting.")
            return

        if (self.experiment_name):
            print("Experiment name:", self.experiment_name)
        else:
            print("No experiment name found; check format. Quiting.")
            return

        self._setRowPositions()
        self._set_col_positions()

        print(self.start_sweep_col)
        print(self.end_sweep_col)

        if not self.description:
            self.description = "Project from excel spreadsheet"
        self.project = create_project(self.project_name, self.description)
        self.experiment = self.project.create_experiment(self.experiment_name, "")

        self.sweep()

        print("Created project:", self.project.name)

    def sweep(self):
        self._makeTemplateTable()
        col_index = self.start_sweep_col
        while col_index < self.end_sweep_col:
            process_name = self.source[0][col_index]
            if process_name and str(process_name).startswith("PROC:"):
                process_name = self._pruneEntry(process_name, "PROC:")
                template_id = self._getTemplateIdFor(process_name)
                if template_id:
                    col_index = self.sweepProcess(template_id, col_index)
            col_index += 1

    def sweepProcess(self, template_id, col_index):
        process = self.experiment.create_process_from_template(template_id)
        print(template_id, process.experiment.project.name)
        return col_index

    def setDescription(self, description):
        self.description = description

    def _pruneEntry(self, entry, prefix):
        entry = str(entry)
        if entry.startswith(prefix):
            entry = entry[len(prefix):].strip(" ").strip("'").strip('"')
        else:
            entry = None
        return entry

    def _setNames(self):
        self.project_name = self._pruneEntry(self.source[0][0], "PROJ:")
        self.experiment_name = self._pruneEntry(self.source[1][0], "EXP:")

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

    def _makeTemplateTable(self):
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        self.template_table = table

    def _getTemplateIdFor(self, match):
        found_id = None
        for key in self.template_table:
            if match in key:
                found_id = key
        return found_id


def main(args):
    wb = openpyxl.load_workbook(filename=args.input, read_only=True)
    ws = wb['EPMA Results (Original)']
    builder = BuildProjectExperiment()
    builder.setDescription("Project from excel spreadsheet: " + args.input
                           + "; using data from " + args.dir)
    builder.build(ws, args.dir)


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

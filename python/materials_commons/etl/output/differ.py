import argparse
import datetime
import sys
import tempfile
from pathlib import Path

import openpyxl

from materials_commons.api import get_all_projects
from materials_commons.etl.common.worksheet_data import read_entire_sheet
from materials_commons.etl.input.metadata import Metadata
from .meta_data_verify import MetadataVerification


class Differ:
    def __init__(self):
        self.metadata = Metadata()
        self.project = None
        self.experiment = None
        self.input_data = []
        self.missing_process_list = []
        self.added_process_list = []

    def compute_deltas(self):
        metadata = self.metadata
        process_table = metadata.process_table
        data = self.input_data
        delta_list = []
        print("Computing deltas for experiment:", self.experiment.name)
        print("excel spreadsheet...")
        print("  number of rows:", len(data))
        print("  length of first row", len(data[0]))
        print("metadata...")
        print("  data rows, start and end:", metadata.data_row_start, metadata.data_row_end)
        print("  data cols, start and end:", metadata.data_col_start, metadata.data_col_end)
        print("  number of process records:", len(metadata.process_metadata))
        print("experiment...")
        print("  number of processes", len(process_table))
        delta_list += self._process_deltas()
        delta_list += self._attribute_deltas()
        delta_list += self._value_deltas()
        return delta_list

    def report_deltas(self, deltas):
        print("Reporting deltas for experiment:", self.experiment.name)
        print("Number of deltas:", len(deltas))
        for delta in deltas:
            print("  ", delta['type'], delta['data'])

    def set_up_project_experiment_metadata(self, project_name, experiment_name):
        project_list = get_all_projects()
        for proj in project_list:
            if proj.name == project_name:
                self.project = proj
        if not self.project:
            print("Can not find project with name = " + str(project_name) + ". Quiting.")
            return False
        experiment_list = self.project.get_all_experiments()
        found = []
        for exp in experiment_list:
            if exp.name == experiment_name:
                found.append(exp)
        if not found:
            print("Can not find Experiment with name = " + str(experiment_name) + ". Quiting.")
            return False
        if len(found) > 1:
            print("Found more the one Experiment with name = " + str(experiment_name) + ";")
            print("Rename experiment so that '" + str(experiment_name) + "' is unique.")
            print("Quiting.")
            return False
        self.experiment = found[0]
        ok = self.metadata.read(self.experiment.id)
        if not ok:
            print("There was no ETL metadata for the experiment '" + str(experiment_name) + "';")
            print("This experiment does not appear to have been created using ETL input.")
            print("Quiting.")
            return False
        verify = MetadataVerification()
        metadata = verify.verify(self.metadata)  # Adds metadata.process_table !
        if not metadata:
            if verify.failure == "Project":
                print("Failed to find project for compare. Quiting")
                return False
            if verify.failure == "Experiment":
                print("Failed to find experiment for compare. Quiting")
                return False
            print("Differences detected by metadata verification")
            metadata = verify.metadata
            if verify.missing_process_list:
                self.missing_process_list = verify.missing_process_list
            if verify.added_process_list:
                self.added_process_list = verify.added_process_list
        self.metadata = metadata
        return True

    def set_up_input_data(self):
        print("Setup input data")
        file_id = self.metadata.input_excel_file_id
        print("Excel file id:", file_id)
        if not file_id:
            print("Experiment metadata does not contain id of excel file")
            return False
        with tempfile.TemporaryDirectory() as tmpdirname:
            directory = self.project.add_directory("/Input Excel Spreadsheets")
            print(directory.name)
            file = None
            for child in directory.get_children():
                if child.id == file_id:
                    file = child
                    break
            if not file:
                print("Can not locate file for excel input")
                return False
            else:
                print(file.name)
                local_file_path = str(Path(tmpdirname, file.name))
                print(local_file_path)
                file.download_file_content(local_file_path)
                print(local_file_path, Path(local_file_path).exists())
                wb = openpyxl.load_workbook(filename=local_file_path)
                sheet_name = wb.sheetnames[0]
                ws = wb[sheet_name]
                print("In Excel file, using sheet", sheet_name, "from sheets", wb.sheetnames)
                self.input_data = read_entire_sheet(ws)
                wb.close()
        return True

    def _process_deltas(self):
        deltas = []
        if self.missing_process_list:
            print("Processes that are in original input that are not in the experiment")
            for process_id in self.missing_process_list:
                deltas.append({
                    "type": "missing_process",
                    "data": {
                        "process_id": process_id
                    }
                })
        if self.added_process_list:
            print("Processes that are not in original input that are in the experiment")
            for process_id in self.added_process_list:
                deltas.append({
                    "type": "added_process",
                    "data": {
                        "process_id": process_id
                    }
                })
        return deltas

    def _attribute_deltas(self):
        return []

    def _value_deltas(self):
        return []


def main(project_name, experiment_name):
    differ = Differ()
    ok = differ.set_up_project_experiment_metadata(project_name, experiment_name)
    if not ok:
        print("Invalid configuration of metadata or experiment/metadata mismatch. Quiting")
        exit(-1)
    ok = differ.set_up_input_data()
    if not ok:
        print("Could not locate or read input spreadsheet from experiment")
        exit(-1)
    deltas = differ.compute_deltas()
    if not deltas:
        print("No differences were detected. Done")
    else:
        differ.report_deltas(deltas)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Computer differences in web site and excel spreadsheet data for experiment')
    parser.add_argument('proj', type=str, help="Project Name")
    parser.add_argument('exp', type=str, help="Experiment Name")
    args = parser.parse_args(argv[1:])

    print(
        "Computer differences in web site and excel spreadsheet data for experiment '"
        + args.exp + "' of project '" + args.proj)

    main(args.proj, args.exp)

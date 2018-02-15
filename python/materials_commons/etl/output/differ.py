import argparse
import datetime
import sys
import tempfile
from pathlib import Path

import openpyxl

from materials_commons.api import get_all_projects
from materials_commons.etl.common.worksheet_data import read_entire_sheet
from materials_commons.etl.input.metadata import Metadata
from materials_commons.etl.common.util import _normalise_property_name
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
        print("--------------------")
        process = process_table['36eef9fc-c07f-4180-943e-4935e3109a60']
        print(process.input_data)
        print("--------------------")
        print(process.setup[0].properties[1].input_data)
        print(process.setup[0].properties[1].value)
        print("--------------------")
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
        file_id = self.metadata.input_excel_file_id
        if not file_id:
            print("Experiment metadata does not contain id of excel file")
            return False
        with tempfile.TemporaryDirectory() as tmpdirname:
            directory = self.project.add_directory("/Input Excel Spreadsheets")
            file = None
            for child in directory.get_children():
                if child.id == file_id:
                    file = child
                    break
            if not file:
                print("Can not locate file for excel input")
                return False
            else:
                local_file_path = str(Path(tmpdirname, file.name))
                file.download_file_content(local_file_path)
                wb = openpyxl.load_workbook(filename=local_file_path)
                sheet_name = wb.sheetnames[0]
                ws = wb[sheet_name]
                print("In input Excel file, using sheet", sheet_name, "from sheets", wb.sheetnames)
                self.input_data = read_entire_sheet(ws)
                wb.close()
        return True

    def _process_deltas(self):
        deltas = []
        if self.missing_process_list:
            for process_id in self.missing_process_list:
                deltas.append({
                    "type": "missing_process",
                    "data": {
                        "process_id": process_id
                    }
                })
        if self.added_process_list:
            for process_id in self.added_process_list:
                deltas.append({
                    "type": "added_process",
                    "data": {
                        "process_id": process_id
                    }
                })
        return deltas

    def _attribute_deltas(self):
        deltas = []
        for process_id in self.metadata.process_table:
            if process_id in self.missing_process_list:
                continue
            metadata_attribute_list = self._get_metadata_attributes(process_id)
            process_attribute_list = self._getProcess_attributes(process_id)
            for attribute in metadata_attribute_list:
                if not attribute in process_attribute_list:
                    deltas.append({
                        "type": "missing_attribute",
                        "data": {
                            'process_id': process_id,
                            'attribute': attribute
                        }
                    })
            for attribute in process_attribute_list:
                if not attribute in metadata_attribute_list:
                    deltas.append({
                        "type": "added_attribute",
                        "data": {
                            'process_id': process_id,
                            'attribute': attribute
                        }
                    })
        return deltas

    def _value_deltas(self):
        return []

    def _get_metadata_attributes(self, process_id):
        attribute_list = []
        process_record = self._get_metadata_process_record(process_id)
        types_row = self.input_data[self.metadata.start_attribute_row]
        attributes_row = self._remove_units_spec_from_attributes(
            self.input_data[self.metadata.start_attribute_row + 1])
        attributes_row = self._make_normalized_attribute_names(attributes_row)
        if process_record:
            start_col = process_record['start_col']
            end_col = process_record['end_col']
            for col in range(start_col, end_col):
                if self._is_attribute(types_row[col]):
                    attribute_list.append(attributes_row[col])
        print("  for process id", process_id, "metadata attributes are", attribute_list)
        return attribute_list

    def _getProcess_attributes(self, process_id):
        attribute_list = []
        process = self.metadata.process_table[process_id]
        for s in process.setup:
            for prop in s.properties:
                print(process_id, prop.attribute, prop.value)
                if (prop.value is not None) and (str(prop.value).strip() != ""):
                    attribute_list.append(prop.attribute)
        for m in process.measurements:
            attribute_list.append(m.attribute)
        print("  for process id", process_id, "process attributes are", attribute_list)
        return attribute_list

    def _get_metadata_process_record(self, process_id):
        found = None
        for record in self.metadata.process_metadata:
            if process_id == record['id']:
                found = record
                break
        return found

    def _is_attribute(self, attribute_type):
        return attribute_type in ['PARAM','MEAS']

    @staticmethod
    def _remove_units_spec_from_attributes(attributes):
        update = []
        for attr in attributes:
            if attr and '(' in attr:
                pos = attr.find('(')
                if pos > 2:
                    attr = attr[0:pos - 1]
            update.append(attr)
        return update

    @staticmethod
    def _make_normalized_attribute_names(attributes):
        update = []
        for attr in attributes:
            if attr:
                if isinstance(attr, str):
                    attr = _normalise_property_name(attr)
                else:
                    parts = []
                    for part in attr:
                        if not parts:
                            # only normalize the leading term
                            part = _normalise_property_name(part)
                        parts.append(part)
                    attr = parts
            update.append(attr)
        return update


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

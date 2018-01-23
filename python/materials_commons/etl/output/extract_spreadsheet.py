import argparse
import datetime
import os
import sys

import openpyxl

from materials_commons.etl.common.util import _normalise_property_name
from materials_commons.etl.input.metadata import Metadata
from .meta_data_verify import MetadataVerification

local_path = '/Users/weymouth/Desktop/'
BASE_DIRECTORY = os.path.abspath(local_path)


class ExtractExperimentSpreadsheet:
    def __init__(self, setup_args, metadata):
        self.dir = setup_args.dir
        self.file = setup_args.file
        self.metadata = metadata
        self.output_path = None
        self.project = metadata.project
        self.experiment = metadata.experiment
        self.process_table = metadata.process_table
        self.worksheet = None
        self.workbook = None
        self.data_row_list = []

    def build_experiment_array(self):
        print("Building data array")
        print("    " + self.project.name)
        print("    " + self.experiment.name)
        self.data_row_list = []
        self.set_headers_from_metadata()
        self.set_data_from_metadata()

    def set_headers_from_metadata(self):
        print("    ... setting headers...")
        for row in self.metadata.sheet_headers:
            self.data_row_list.append(row)

    def set_data_from_metadata(self):
        self.initialize_empty_data()
        metadata = self.metadata
        self.data_row_list[metadata.data_row_start][0] = "BEGIN_DATA"
        print("    ... setting data...")
        process_record_list = metadata.process_metadata
        table = metadata.process_table
        type_list = metadata.sheet_headers[metadata.start_attribute_row]
        attribute_list = metadata.sheet_headers[metadata.start_attribute_row + 1]
        attribute_list = self.remove_units_spec_from_attributes(attribute_list)
        attribute_list = self.parse_dotted_attributes(attribute_list)
        attribute_list = self.make_normalized_attribute_names(attribute_list)
        for process_record in process_record_list:
            start_row = process_record["start_row"]
            end_row = process_record["end_row"]
            start_col = process_record["start_col"]
            end_col = process_record["end_col"]
            process = table[process_record['id']]
            self.write_first_data_row_for_process(
                start_row, start_col, end_col, type_list, attribute_list, process)
            if (end_row - start_row) > 1:
                self.copy_duplicate_rows_for_process(
                    start_row, end_row, start_col, end_col)

    def initialize_empty_data(self):
        for row_index in range(len(self.data_row_list), self.metadata.data_row_end):
            self.data_row_list.append([None] * self.metadata.data_col_end)

    def write_first_data_row_for_process(self, row, start, end, types, attributes, process):
        measurements = process.measurements
        setup_parameter_list = process.setup
        for col in range(start, end):
            value_type = types[col]
            attribute = attributes[col]
            if value_type == "MEAS":
                value = self.extract_measurement_for(attribute, measurements)
            elif value_type == "PARAM":
                value = self.extract_parameter_for(attribute, setup_parameter_list)
            elif value_type == "SAMPLES" and process.output_samples:
                value = process.output_samples[0].name
            else:
                value = None
            self.data_row_list[row][col] = value

    def extract_measurement_for(self, attribute, measurements):
        value = None
        measurement = self.find_measurement_for_attribute(attribute, measurements)
        if measurement:
            value = self.get_measurement_value_for_attribute(attribute, measurement)
        return value

    def find_measurement_for_attribute(self, attribute, measurements):
        found_measurement = None
        base = attribute
        if not isinstance(attribute, str):
            base = attribute[0]
        for m in measurements:
            if base == m.attribute:
                found_measurement = m
        return found_measurement

    def get_measurement_value_for_attribute(self, attribute, measurement):
        # print('get_measurement_value_for_attribute', attribute, measurement.value)
        if not isinstance(attribute, list):
            if not isinstance(measurement.value, list):
                return measurement.value
            else:
                return None
        return self.recursive_value_extraction(attribute[0], attribute[1:],measurement.value)

    def recursive_value_extraction(self, name, name_list, probe):
        key = self.key_for_category(name, name_list)
        # print('recursive_value_extraction', name, name_list, key, probe)
        value = None
        if isinstance(probe, dict):
            if key in probe:
                value = probe[key]
        elif len(name_list) > 0:
            part_name = name_list[0]
            for m in probe:
                if key in m and m[key] == part_name:
                    value = m['value']
                    if isinstance(value, dict):
                        value = self.recursive_value_extraction(name_list[1], name_list[2:], value)
        # print('recursive_value_extraction - value', value)
        return value

    @staticmethod
    def key_for_category(name, name_list):
        key = name
        if name == 'composition':
            key = 'element'
        if name == 'stats':
            key = name_list[0]
        return key

    @staticmethod
    def extract_parameter_for(attribute, setup_list):
        value = None
        for s in setup_list:
            for prop in s.properties:
                if attribute.startswith(prop.attribute):
                    value = prop.value
        return value

    def copy_duplicate_rows_for_process(self, start_row, end_row, start_col, end_col):
        for row in range(start_row + 1, end_row):
            for col in range(start_col, end_col):
                self.data_row_list[row][col] = self.data_row_list[start_row][col]

    def write_spreadsheet(self):
        dir_path = os.path.abspath(self.dir)
        if not os.path.isdir(dir_path):
            print("The given path, " + self.dir + ", is not a directory")
            print("Resolved to: " + dir_path)
            return None
        self.output_path = os.path.join(dir_path, self.file)

        print("Writing spreadsheet", self.output_path)
        if self.create_worksheet():
            self.write_data_to_sheet()
            self.workbook.save(filename=self.output_path)
            self.workbook.close()

    def write_data_to_sheet(self):
        for row in range(0, len(self.data_row_list)):
            data_row = self.data_row_list[row]
            for col in range(0, len(data_row)):
                data_item = data_row[col]
                self.worksheet.cell(column=col + 1, row=row + 1, value=data_item)

    def create_worksheet(self):
        wb = openpyxl.Workbook()
        ws = wb.worksheets[0]
        ws['A1'] = "PROJ: " + self.project.name
        ws['A2'] = "EXP: " + self.experiment.name
        wb.save(filename=self.output_path)
        self.worksheet = ws
        self.workbook = wb
        return wb

    @staticmethod
    def remove_units_spec_from_attributes(attributes):
        update = []
        for attr in attributes:
            if attr and '(' in attr:
                pos = attr.find('(')
                if pos > 2:
                    attr = attr[0:pos-1]
            update.append(attr)
        return update

    @staticmethod
    def parse_dotted_attributes(attributes):
        update = []
        for attr in attributes:
            if attr and '.' in attr:
                attr = attr.split('.')
            update.append(attr)
        return update

    @staticmethod
    def make_normalized_attribute_names(attributes):
        update = []
        for attr in attributes:
            if attr:
                if isinstance(attr,str):
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


def main(main_args):
    metadata = Metadata()
    metadata.read(main_args.metadata)
    verify = MetadataVerification()
    updated_metadata = verify.verify(metadata)

    if not updated_metadata:
        print("The verification of the metadata file failed.")
        exit(-1)

    builder = ExtractExperimentSpreadsheet(main_args, updated_metadata)
    print("Set up: writing spreadsheet, " + main_args.file)
    print("        to directory " + main_args.dir)
    print("Data from experiment '" + builder.experiment.name
          + "' in project '" + builder.project.name + "'")
    builder.build_experiment_array()
    builder.write_spreadsheet()


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_output_dir_path = os.path.join(BASE_DIRECTORY)
    default_file_name = "workflow.xlsx"
    default_metadata_file_path = "metadata.json"

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Dump a project-experiment to a spreadsheet')
    parser.add_argument('--metadata', type=str, default=default_metadata_file_path,
                        help="Metadata file path")
    parser.add_argument('--dir', type=str, default=default_output_dir_path,
                        help='Path to output directory')
    parser.add_argument('--file', type=str, default=default_file_name,
                        help="Path to output file")
    args = parser.parse_args(argv[1:])

    args.dir = os.path.abspath(args.dir)

    if not os.path.isdir(args.dir):
        print("The given output directory path, " + args.dir + ", is not a directory. Please fix.")
        exit(-1)

    args.metadata = os.path.abspath(args.metadata)
    if not os.path.isfile(args.metadata):
        print("The given metadata file path, " + args.metadata + ", is not a file. Please fix.")
        exit(-1)

    if not args.file.endswith(".xlsx"):
        file = args.file + ".xlsx"

    main(args)

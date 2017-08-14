import openpyxl
import argparse
import datetime
import os.path
import sys
from mcapi import create_project, get_all_templates


BASE_DIRECTORY = os.path.abspath("input_data/EPMA Raw Data")

# Excel Spreadsheet, from Tracy: ./input_data/EPMA_Melt5b_MC_Demo.xlsx
# meaning of values are hardcoded
# A - ignore
# B - sample name - first time sample/gemoentry/location is hit, defines a sample type, location
# C, D - ignore
# E - sample casting geometry
# F-H - sample location
#     F - along width
#     G - along thickness
#     H - location
# I-Q - measurement values
#     I - reference standard
#     J - number of points sampled
#     K,L - number of good points using two standards of "goodness": 98-101 and 98-100.5
#     M,N - the accumulated measurement value for each goodness set
#     O - judgment of overall quailty
#     P,Q - start row and end row for the points collected
# R - results file(s) name ([name].xlsx and [name].txt)


class WorkflowBuilder:
    def parse_sheet(self, sheet,args):
        self.file_upload_count = 0

        workflow_list = self.build_workflow_list(sheet)

        self.create_project_experiment()
        self.template_table = self.make_template_table()

        print self.template_id_with(self.template_table, 'EPMA')

        self.create_processes = {}
        self.section_processes = {}
        self.project_files = {}

        for workflow in workflow_list:
            self.create_process_name = 'Create ' + workflow["material"]
            self.create_process_output_sample_name = workflow["material"]
            self.section_process_name = 'Section ' + workflow["material"]
            self.section_process_output_sample_name = workflow["material"] + "::" + workflow['geometry']
            self.epma_process_name = 'EPMA - ' \
                                + workflow['geometry'] + ' - ' + workflow['location']

            self.add_create_sample_process_if_needed()
            self.add_sectioning_process_if_needed()
            epma_process = self.add_measurement_process(workflow)

            epma_process = self.ready_process_for_additions(epma_process)

            self.add_setup(epma_process,workflow['location'])
            self.add_data_files(epma_process,workflow['data_file'])
            # TODO: support arbitrary measurements and annotations in process
            # self.add_measurements_and_annotations(epma_process,workflow)

        print self.project.name
        print len(self.project_files)

    # build methods

    def create_project_experiment(self):
        time_stamp = '%s' % datetime.datetime.now()
        project_name = "Example-From-Script: " + time_stamp
        project_description = "Example workflow, created from script on " + time_stamp
        self.project = create_project(project_name, project_description)
        self.project.local_path = BASE_DIRECTORY

        self.experiment = self.project.create_experiment("EPMA-Melt5b", "EPMA measurements of Melt5b samples")


    def build_workflow_list(self,sheet):
        workflow_list = []
        for row in sheet.iter_rows(min_row=2):
            values = []
            for cell in row:
                values.append(cell.value)
            workflow_list.append(
                {
                    'material': values[1],
                    'geometry': values[4],
                    "width": values[5],
                    "thickness": values[6],
                    "location": values[7],
                    "standard": values[8],
                    "points": values[9],
                    "goodpoint_101": values[10],
                    "goodpoint_100p5": values[11],
                    "fg_101": values[12],
                    "fg_100p5": values[13],
                    "quality": values[14],
                    "start_row": values[15],
                    "end_row": values[16],
                    "data_file": values[17]
                }
            )
        return workflow_list

    def add_create_sample_process_if_needed(self):
        if not self.create_process_name in self.create_processes:
            template_id = self.template_id_with(self.template_table, 'Create Samples')
            process = self.experiment.create_process_from_template(template_id)
            process.rename(self.create_process_name)
            samples = process.create_samples(sample_names=[self.create_process_output_sample_name])
            self.create_processes[self.create_process_name] = {
                'process': process,
                'sample': samples[0]
            }

    def add_sectioning_process_if_needed(self):
        if not self.section_process_name in self.section_processes:
            template_id = self.template_id_with(self.template_table, 'Sectioning')
            process = self.experiment.create_process_from_template(template_id)
            process.rename(self.section_process_name)
            samples = process.create_samples(sample_names=[self.section_process_output_sample_name])
            process_and_sample = self.create_processes[self.create_process_name]
            create_sample_output = process_and_sample['sample']
            process.add_input_samples_to_process([create_sample_output])
            section_output_samples = {}
            section_output_samples[self.section_process_output_sample_name] = samples[0]
            self.section_processes[self.section_process_name] = {
                'process': process,
                'samples': section_output_samples
            }
        else:
            process_and_samples = self.section_processes[self.section_process_name]
            samples = process_and_samples['samples']
            if not self.section_process_output_sample_name in samples:
                process = process_and_samples['process']
                section_samples = process.create_samples(sample_names=[self.section_process_output_sample_name])
                process_and_samples['samples'][self.section_process_output_sample_name] = section_samples[0]

    def ready_process_for_additions(self,process):
        updated_process = self.experiment.get_process_by_id(process.id)
        return updated_process

    def add_measurement_process(self,workflow):
        process_and_samples = self.section_processes[self.section_process_name]
        measurement_input_sample = process_and_samples['samples'][self.section_process_output_sample_name]
        template_id = self.template_id_with(self.template_table, 'EPMA')
        process = self.experiment.create_process_from_template(template_id)
        process.rename(self.epma_process_name)
        process.add_input_samples_to_process([measurement_input_sample])
        return process

    def add_setup(self,epma_process,location):
        # TODO: add in error checking for unit in units
        epma_process.set_value_of_setup_property('voltage', 10)
        epma_process.set_unit_of_setup_property('voltage', 'kV')
        epma_process.set_value_of_setup_property('beam_current', 10)
        epma_process.set_unit_of_setup_property('beam_current', 'nA')
        epma_process.set_value_of_setup_property('beam_size', 0)
        # TODO: support setting choice setup properties by type or name
        # this is a problem that needs to be fixed.
        # also should generate informative error message when expected to fail
        # scan_type = 'grid'
        # if location == 'edge':
        #     scan_type = 'line'
        # epma_process.set_value_of_setup_property('scan_type', scan_type)
        scan_type = {"name":"Grid","value":"grid"}
        if location == 'edge':
            scan_type = {"name":"Line","value":"line"}
        epma_process.set_value_of_setup_property('scan_type', scan_type)
        epma_process.set_value_of_setup_property('step_size', 10)
        epma_process.set_value_of_setup_property('grid_dimensions', '20 x 20')
        epma_process.set_value_of_setup_property('location', location)
        epma_process.update_setup_properties([
            'voltage', 'beam_current', 'beam_size', 'scan_type', 'step_size', 'grid_dimensions','location'
        ])

    def add_data_files(self,epma_process, name):
        filename_doc = name + '.docx'
        filename_excel = name + '.xlsx'
        filenames = [filename_doc, filename_excel]
        files = []
        for filename in filenames:
            if not filename in self.project_files:
                path = BASE_DIRECTORY + "/" + filename
                if os.path.isfile(path):
                    file = self.project.add_file_by_local_path(path)
                    self.project_files[filename] = file
            if filename in self.project_files:
                files.append(self.project_files[filename])
        if len(files) > 0:
            epma_process.add_files(files)


    # def add_measurements_and_annotations(self,epma_process,workflow):
    #     measurements = ['goodpoint_101', 'goodpoint_100p5', 'fg_101', 'fg_100p5']
    #     for measurement_name in measurements:
    #         measurement_data = {
    #             "name": measurement_name,
    #             "attribute": measurement_name,
    #             "otype": "number",
    #             "is_best_measure": True
    #         }
    #         measurement = epma_process.create_measurement(data=measurement_data)
    #         measurement_property = {
    #             "name": measurement_name,
    #             "attribute": measurement_name
    #         }
    #         epma_process.set_measurements_for_process_samples(measurement_property, [measurement])


    def make_template_table(self):
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        return table

    def template_id_with(self, table, match):
        found_id = None
        for key in table:
            if match in key:
                found_id = key
        return found_id

def main(args):
    wb = openpyxl.load_workbook(filename='input_data/EPMA_Melt5b_MC_Demo.xlsx', read_only=True)
    ws = wb['Sheet1']
    WorkflowBuilder().parse_sheet(ws,args)


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_project_name = "Project-From-Script: " + time_stamp
    default_experiment_name = "Experiment-From-Script: " + time_stamp

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('--project', type=str, default='', help='Project name - otherwise generated')
    parser.add_argument('--experiment', type=str, default='', help='Experiment name - otherwise generated')
    parser.add_argument('--input', type=str, default='input.xlsx', help='Path to input EXCEL file - defaults to input.xlsx')
    parser.add_argument('--dir', type=str, default='./input_data', help='Path to directory of data files - defaults to ./input_data')
    args = parser.parse_args(argv[1:])

    if not args.project:
        args.project = default_project_name
    if not args.experiment:
        args.experiment = default_experiment_name
    args.input = os.path.abspath(args.input)
    args.dir = os.path.abspath(args.dir)

    print "Project name: " + args.project
    print "Experiment name: " + args.experiment
    print "Path to input EXCEL file: " + args.input
    print "Path to data file directory: " + args.dir

    main(args)

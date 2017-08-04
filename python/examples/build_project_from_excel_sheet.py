import openpyxl
import argparse
import datetime
import os.path
import sys
from mcapi import create_project, get_all_projects, get_all_templates

local_path = './example_data/excel_spreadsheet_files'
BASE_DIRECTORY = os.path.abspath(local_path)


class WorkflowBuilder:
    def build(self, sheet, args):
        self.source = self._read_entire_sheet(sheet)
        self.projects = []
        self._make_template_table()
        row = 0;
        while row < len(self.source):
            action = self.source[row][0]
            if action == 'project':
                row = self.add_project(row)
            elif action == 'experiment':
                row = self.add_experiment(row)
            elif action == 'workflow':
                row = self.add_workflow(row)
            else:
                row += 1

    def add_project(self, row):
        name = self.source[row][1]
        description = self.source[row][2]
        name = self._make_unique_project_name(name)
        print "Adding Project: " + name
        project = create_project(name, description)
        self.current_project = project
        self.projects.append(project)
        return row + 1

    def add_experiment(self, row):
        project = self.current_project
        name = self.source[row][1]
        description = self.source[row][2]
        print "Adding Experiment: " + name
        self.current_experiment = project.create_experiment(name, description)
        self.sample_table = {}
        return row + 1

    def add_workflow(self, row):
        print "Workflow: "
        process = self.add_process(row)
        print "   " + process.name

        row += 1
        while (row < len(self.source)) and (not self.source[row][0]):
            process = self.add_process(row)
            print "   " + process.name
            row += 1
        return row - 1

    def add_process(self, row):
        experiment = self.current_experiment
        name = self.source[row][1]
        template = self.source[row][3]
        sample_in = self.source[row][4]
        sample_out = self.source[row][5]
        process = experiment.create_process_from_template(self._get_template_id(template))
        process.rename(name)

        create_type = (process.process_type == 'create' or process.template_name == 'Sectioning')
        if create_type and sample_out:
            output_sample_name_list = self._parse_sample_name_list(sample_out)
            samples = process.create_samples(output_sample_name_list)
            for i in range(0, len(samples)):
                name = output_sample_name_list[i]
                sample = samples[i]
                self.sample_table[name] = sample

        if sample_in:
            input_sample_name_list = self._parse_sample_name_list(sample_in)
            input_samples = []
            for name in input_sample_name_list:
                if self.sample_table[name]:
                    input_samples.append(self.sample_table[name])
            if len(input_samples) > 0:
                process.add_input_samples_to_process(input_samples)
            if process.process_type == 'transform':
                process = process.decorate_with_output_samples()
                output_samples = process.output_samples
                for sample in output_samples:
                    name = sample.name
                    self.sample_table[name] = sample

        return process

    def pp(self):
        for project in self.projects:
            print "Project..."
            project.pretty_print()
            experiments = project.get_all_experiments()
            for experiment in experiments:
                print "  Experiment..."
                experiment.pretty_print(shift=2)
                processes = experiment.get_all_processes()
                for process in processes:
                    print "    Process..."
                    process.pretty_print(shift=4)

    def _read_entire_sheet(self, sheet):
        data = []
        for row in sheet.iter_rows():
            values = []
            for cell in row:
                values.append(cell.value)
            data.append(values)
        return data

    def _parse_sample_name_list(self, name_string):
        list = [name_string]
        start = name_string.find('[')
        end = name_string.find(']', start + 1)
        if (start > -1) and (end > start):
            slice = name_string[start + 1:end]
            parts = slice.split(",")
            list = parts
        for i in range(0, len(list)):
            list[i] = list[i].strip()
        return list

    def _make_unique_project_name(self, name):
        probe = name
        count = 0
        while (self._projects_exists(probe)):
            count += 1
            probe = name + " " + str(count)
        return probe

    def _projects_exists(self, name):
        projects = get_all_projects()
        project = None
        for p in projects:
            if p.name == name:
                return True
        return False

    def _make_template_table(self):
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        self.template_table = table

    def _get_template_id(self, match):
        table = self.template_table
        found_id = None
        for key in table:
            if match in key:
                found_id = key
        print match, found_id
        return found_id


def main(args):
    wb = openpyxl.load_workbook(filename=args.input, read_only=True)
    ws = wb['Sheet1']
    builder = WorkflowBuilder()
    builder.build(ws, args)

    print "Built project..."
    builder.pp()


if __name__ == '__main__':
    time_stamp = '%s' % datetime.datetime.now()
    default_input_path = os.path.join(BASE_DIRECTORY, "input.xlsx")
    default_data_path = os.path.join(BASE_DIRECTORY, "data")

    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('--input', type=str, default='', help='Path to input EXCEL file - defaults to input.xlsx')
    parser.add_argument('--dir', type=str, default='',
                        help='Path to directory of data files - defaults to ./input_data')
    args = parser.parse_args(argv[1:])

    if not args.input:
        args.input = default_input_path
    if not args.dir:
        args.dir = default_data_path
    args.input = os.path.abspath(args.input)
    args.dir = os.path.abspath(args.dir)

    print "Default Path to input EXCEL file: " + args.input
    print "Default Path to data file directory: " + args.dir

    main(args)

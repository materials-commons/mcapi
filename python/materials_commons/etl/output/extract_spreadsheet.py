import argparse
import datetime
import os
import sys

from materials_commons.api import get_all_projects

local_path = '/Users/weymouth/Dropbox/MaterialCommons/Tracy_Jake_ETL/etl-output'
BASE_DIRECTORY = os.path.abspath(local_path)


class ExtractExperimentSpreadsheet:
    def __init__(self, setup_args):
        self.dir = setup_args.dir
        self.file = setup_args.file
        self.project_name = setup_args.project
        self.project = None
        self.experiment_name = setup_args.experiment
        self.experiment = None

    def verify_output_paths(self):
        pass

    def build_experiment_array(self):
        pass

    def write_spreadsheet(self):
        pass

    def verify_experiment_exists(self):
        self._get_project_if_exits()
        if not self.project:
            print("Project not found in database: " + self.project_name)
            return None
        self._get_experiment_if_exits()
        if not self.experiment:
            print("Experiment not found in database: " + self.experiment_name)

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
    if not builder.verify_output_paths():
        print("Unable to open spreadsheet, "
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

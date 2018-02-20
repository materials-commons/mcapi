import argparse
import os
import sys
from pathlib import Path

from materials_commons.etl.input.build_project import BuildProjectExperiment
from .differ import Differ
from .modify_workflow import Modifier


class Tester:
    def __init__(self, spread_sheet_path, data_dir):
        self.spread_sheet_path = spread_sheet_path
        self.data_dir = data_dir
        self.project = None
        self.experiment = None

    def run(self):
        print("================== input ==========================")
        print("================== input ==========================")
        print("================== input ==========================")
        builder = BuildProjectExperiment()
        builder.set_rename_is_ok(True)
        print("calling build")
        builder.build(self.spread_sheet_path, self.data_dir)
        self.project = builder.project
        self.experiment = builder.experiment
        project_name = "Generic Testing"
        experiment_name = "Test1"

        print("================== modify ==========================")
        print("================== modify ==========================")
        print("================== modify ==========================")
        modifier = Modifier()
        project = modifier.get_project(project_name)
        if not project:
            print("Could not find project", project_name)
            exit(-1)
        print("Project", project.name, project.id)
        experiment = modifier.get_experiment(experiment_name)
        if not experiment:
            print("Count not find experiment:", experiment_name)
            exit(-1)
        print("Experiment", experiment.name, experiment.id)
        modifier.modify()

        print("================== differ ==========================")
        print("================== differ ==========================")
        print("================== differ ==========================")
        differ = Differ()
        ok = differ.set_up_project_experiment_metadata(project.name, experiment.name)
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

    def verify_data_dir(self):
        path = Path(self.data_dir)
        ok = path.exists() and path.is_dir()
        return ok

    def verify_input_path(self):
        path = Path(self.spread_sheet_path)
        ok = path.exists() and path.is_file()
        return ok


def main(spread_sheet_path, data_dir):
    tester = Tester(spread_sheet_path, data_dir)
    if not tester.verify_input_path():
        print("The Path to the input Excel spreadsheet does not point to a file; exiting.")
        exit(-1)
    if data_dir and (not tester.verify_data_dir()):
        print("The Path to data file directory does not point to a user directory; exiting.")
        exit(-1)
    tester.run()


if __name__ == '__main__':
    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('input', type=str,
                        help='Path to input EXCEL file')
    parser.add_argument('--upload', type=str,
                        help='Path to directory of data files to upload - optional')
    args = parser.parse_args(argv[1:])

    args.input = os.path.abspath(args.input)

    print("Path to input EXCEL file: " + args.input)
    if args.upload:
        args.upload = os.path.abspath(args.upload)
        print("Path to directory as sources of file upload: " + args.upload)
    else:
        print("Path to directory as sources of file upload, not specified. File upload suppressed")

    main(args.input, args.upload)

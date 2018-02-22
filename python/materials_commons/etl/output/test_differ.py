import argparse
import os
import sys
from pathlib import Path

from materials_commons.etl.input.build_project import BuildProjectExperiment
from .differ import Differ
from .modify_workflow import Modifier
from .extract_spreadsheet_with_changes import ExtractExperimentSpreadsheetWithChanges


class Tester:
    def __init__(self, spread_sheet_path, output_file_path, upload_data_dir, download_data_dir):
        self.spread_sheet_path = spread_sheet_path
        self.data_dir = upload_data_dir
        self.output_file_path = output_file_path
        self.download_data_dir = download_data_dir
        self.project = None
        self.experiment = None

    def run(self):
        print("================== input ==========================")
        print("================== input ==========================")
        print("================== input ==========================")
        builder = BuildProjectExperiment()
        builder.set_rename_is_ok(True)
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
            print("Could not find experiment:", experiment_name)
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
        print("================== output ==========================")
        print("================== output ==========================")
        print("================== output ==========================")
        output = self.output_file_path
        builder = ExtractExperimentSpreadsheetWithChanges(output)
        builder = register_deltas(deltas)
        ok = builder.set_up_project_experiment_metadata(project_name, experiment_name)
        download = self.download_data_dir
        if not ok:
            print("Invalid configuration of metadata or experiment/metadata mismatch. Quiting")
        else:
            print("Writing experiment '" + builder.experiment.name
                  + "' in project, '" + builder.project.name + ", to")
            print("spreadsheet at " + builder.output_path)
            builder.build_experiment_array()
            builder.write_spreadsheet()
            if download:
                print("Downloading process files to " + download)
                builder.download_process_files(download)

    def verify_data_dir(self):
        path = Path(self.data_dir)
        ok = path.exists() and path.is_dir()
        return ok

    def verify_input_path(self):
        path = Path(self.spread_sheet_path)
        ok = path.exists() and path.is_file()
        return ok

    def verify_output_path(self):
        path = Path(self.output_file_path)
        dir = path.parent
        print("This is parent dir of output file??: ",dir)
        ok = dir.exists() and dir.is_dir()
        return ok

    def verify_download_data_dir(self):
        path = Path(self.download_data_dir)
        ok = path.exists() and path.is_dir()
        return ok

def main(input_path, output_path, upload_dir, download_dir):
    tester = Tester(input_path, output_path, upload_dir, download_dir)
    if not tester.verify_input_path():
        print("The Path to the input Excel spreadsheet does not point to a file; exiting.")
        exit(-1)
    if not tester.verify_output_path():
        print("The Path to the output Excel spreadsheet is not available; exiting.")
        exit(-1)
    if upload_dir and (not tester.verify_data_dir()):
        print("The Path to the file file directory for upload does not point to a user directory; exiting.")
        exit(-1)
    if download_dir and (not tester.verify_download_data_dir()):
        print("The Path to the file file directory for download does not point to a user directory; exiting.")
        exit(-1)
    tester.run()

if __name__ == '__main__':
    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('input', type=str,
                        help='Path to input EXCEL file')
    parser.add_argument('output', type=str,
                        help='Path to output EXCEL file')
    parser.add_argument('--upload', type=str,
                        help='Path to directory of data files to upload - optional')
    parser.add_argument('--download', type=str,
                        help="Path to dir for downloading files; if none, files are not downloaded")

    args = parser.parse_args(argv[1:])

    args.input = os.path.abspath(args.input)

    print("Path to input EXCEL file: " + args.input)
    if args.upload:
        args.upload = os.path.abspath(args.upload)
        print("Path to directory as sources of file upload: " + args.upload)
    else:
        print("Path to directory as sources of file upload, not specified. File upload suppressed")

    if args.download:
        args.download = os.path.abspath(args.download)
        print("Path to directory as sources of file upload: " + args.download)
    else:
        print("Path to directory as sources of file upload, not specified. File upload suppressed")


    print("Output excel spreadsheet using path: " + args.output)
    if args.download:
        print("  and with file downloads going to " + args.download)

    main(args.input, args.output, args.upload, args.download)

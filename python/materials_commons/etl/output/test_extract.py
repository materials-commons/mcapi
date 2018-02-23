import sys
import argparse
import os
import json
from pathlib import Path
from pprint import pprint
from .extract_spreadsheet_with_changes import ExtractExperimentSpreadsheetWithChanges

class TestExtract:
    def __init__(self):
        self.output = None
        self.download = None
        self.project_name = None
        self.experiment_name = None
        self.deltas = None

    def run(self):
        print("================== output ==========================")
        print("================== output ==========================")
        print("================== output ==========================")
        output = self.output
        builder = ExtractExperimentSpreadsheetWithChanges(output)
        if (self.deltas):
            builder.register_deltas(self.deltas)
            # pprint(self.deltas)
        ok = builder.set_up_project_experiment_metadata(self.project_name, self.experiment_name)
        download = self.download
        if not ok:
            print("Invalid configuration of metadata or experiment/metadata mismatch. Quiting")
            exit(-1)
        else:
            print("Writing experiment '" + builder.experiment.name
                  + "' in project, '" + builder.project.name + ", to")
        print("spreadsheet at " + output)
        builder.build_experiment_array()
        builder.write_spreadsheet()
        if download:
            print("Downloading process files to " + download)
            builder.download_process_files(download)

def _verify_data_dir(dir_path):
    path = Path(dir_path)
    ok = path.exists() and path.is_dir()
    return ok

def main(project_name, experiment_name, output, download, delta_list_path):
    tester = TestExtract()
    tester.project_name = project_name
    tester.experiment_name = experiment_name
    tester.output =  output
    tester.download = download
    if (delta_list_path):
        with open(delta_list_path, "r") as f:
            tester.deltas = json.load(f)
    tester.run()

if __name__ == '__main__':
    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Test of building Excel spreadsheet after changes')
    parser.add_argument('proj', type=str, help="Project Name")
    parser.add_argument('exp', type=str, help="Experiment Name")
    parser.add_argument('output', type=str,
                        help='Path to output file')
    parser.add_argument('--deltas', type=str,
                        help="Path to file with json of delta-list; if none, no deltas are applied")
    parser.add_argument('--download', type=str,
                        help="Path to dir for downloading files; if none, files are not downloaded")
    args = parser.parse_args(argv[1:])

    args.output = os.path.abspath(args.output)

    if not args.output.endswith(".xlsx"):
        file = args.output + ".xlsx"

    if args.download:
        args.download = os.path.abspath(args.download)
        if not _verify_data_dir(args.download):
            print("Path for file download directory does not exist, ignoring: ", args.download)
            args.download = None

    if args.deltas:
        args.deltas = os.path.abspath(args.deltas)

    print("Output excel spreadsheet for experiment '" + args.exp + "' of project '" + args.proj + "'...")
    print("  to spreadsheet at " + args.output)
    if args.download:
        print("  with downloaded data going to " + args.download)
    if args.deltas:
        print("  applying the delta records in " + args.deltas)
    main(args.proj, args.exp, args.output, args.download, args.deltas)

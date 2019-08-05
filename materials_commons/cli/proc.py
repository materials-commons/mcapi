import json
import os
import requests
import sys

from materials_commons.cli.list_objects import ListObjects
import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs

from ..api import __api as mc_raw_api

def add_files_to_process(project_id, process_id, files, remote=None):
    """
    Arguments
    ---------
    project_id: str, Project ID
    process_id: str, Process ID
    files: list of objects

        Ex: files: [
                {"file_id":<id>, "direction": <'in', 'out', or ''>},
                ...
            ]

    Notes
    -----
    If file direction == 'in' or 'out', then the file is included in both 'files' and 'input_files' or 'output_files', respectively.

    If file direction == '' (empty string), then the file is only included in 'files'.

    """
    result = clifuncs.post_v3(
        "addFilesToProcess",
        {
            'project_id': project_id,
            'process_id': process_id,
            'files': [{'file_id':id, 'direction':''} for id in file_ids]
        },
        remote=remote,
        use_data=True)
    return mcapi.Process(result['data'])

def remove_files_from_process(project_id, process_id, file_ids, remote=None):
    """
    Arguments
    ---------
    project_id: str, Project ID
    process_id: str, Process ID
    file_ids: list of str, List of File IDs

    Notes
    -----
    Files are stored with a direction, one of 'in', 'out', or '' (empty string). A file with
    direction 'in' or 'out' is listed both in "input_files" and "files", or "output_files"
    and "files", respectively. Removing a file removes it from all lists.
    """
    result = clifuncs.post_v3(
        "removeFilesFromProcess",
        {
            'project_id': project_id,
            'process_id': process_id,
            'files': file_ids
        },
        remote=remote)
    print(json.dumps(result['data'], indent=2))
    return mcapi.Process(result['data'])

class ProcSubcommand(ListObjects):

    def __init__(self):
        super(ProcSubcommand, self).__init__(
            ["proc"], "Process", "Processes", expt_member=True,
            list_columns=['name', 'owner', 'template_name', 'id', 'mtime'],
            deletable=True,
            custom_selection_actions=['link_files', 'use_files', 'create_files', 'unlink_files']
        )

    def get_all_from_experiment(self, expt):
        return expt.get_all_processes()

    def get_all_from_project(self, proj):
        return proj.get_all_processes()

    def list_data(self, obj):
        return {
            'name': clifuncs.trunc(obj.name, 40),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': clifuncs.format_time(obj.mtime)
        }

    def print_details(self, obj, out=sys.stdout):
        obj.pretty_print(shift=0, indent=2, out=out)

    def delete(self, objects, args, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting processes.\n')
            out.write('Aborting\n')
            return
        for obj in objects:
            # if getattr(obj, 'experiment', None) is None:
            #     out.write('Could not delete processes.\n')
            #     out.write('Currently, processes must be deleted via an experiment.\n')
            #     out.write('Please include the --expt option.\n')
            #     out.write('Aborting\n')
            #     return

            try:
                result = obj.delete()
            except requests.exceptions.HTTPError as e:
                try:
                    print(e.response.json()['error'])
                except:
                    print("  FAILED, for unknown reason")
                result = None

            if result is None:
                out.write('Could not delete process: ' + obj.name + ' ' + obj.id + '\n')
                out.write('At present, a process can not be deleted via the mcapi if ')
                out.write('any of the following are true: \n')
                out.write('  (1) it is not a leaf node in the workflow,\n')
                out.write('  (2) is is in a dataset, \n')
                out.write('  (3) it is a create sample (type) process with one or more output samples.\n')
            else:
                out.write('Deleted process: ' + obj.name + ' ' + obj.id + '\n')

    def add_custom_options(self, parser):

        # linking files
        parser.add_argument('--link-files', nargs="*", help='List of files to link to selected process(es).')
        parser.add_argument('--use-files', nargs="*", help='List of input files to link to selected process(es).')
        parser.add_argument('--create-files', nargs="*", help='List of output files to link to selected process(es).')
        parser.add_argument('--unlink-files', nargs="*", help='List of files to unlink from selected process(es).')


    def _link_files(self, objects, args, direction=None, out=sys.stdout):
        """Link files to processes (any direction)"""
        if direction is None:
            print("Error using _link_files: no direction provided")
        elif direction not in ['in', 'out', '']:
            print("Error using _link_files: unsupported direction: '" + direction + "'")

        proj = clifuncs.make_local_project()

        if not args.link_files:
            print("No files")
            return

        # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
        refpath = os.path.dirname(proj.local_path)
        paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.link_files]
        files = [clifuncs.get_file_by_path(proj, p) for p in paths]
        file_ids = [file.id for file in files]

        resulting_objects = []
        for obj in objects:
            try:
                files = [{"file_id":id, "direction":direction} for id in file_ids]
                resulting_objects.append(add_files_to_process(proj.id, obj.id, files, proj.remote))
            except requests.exceptions.HTTPError as e:
                try:
                    print(json.dumps(e.response.json(), indent=2))
                    print(e.response.json()["error"])
                except:
                    print("  FAILED, for unknown reason")
                return False
        self.output(resulting_objects, args, out=out)
        return

    def link_files(self, objects, args, out=sys.stdout):
        """Link files to processes (direction == '')

        Using:
            mc proc --id <proc_id> --link-files <file1> ...
            mc proc <process_name_search> --link-files <file1> ...
        """
        self._link_files(objects, args, out, direction='')

    def use_files(self, objects, args, out=sys.stdout):
        """Link files 'used by' processes (direction == 'in')

        Using:
            mc proc --id <proc_id> --use-files <file1> ...
            mc proc <process_name_search> --use-files <file1> ...
        """
        self._link_files(objects, args, out, direction='in')

    def create_files(self, objects, args, out=sys.stdout):
        """Link files 'created by' processes (direction == 'out')

        Using:
            mc proc --id <proc_id> --create-files <file1> ...
            mc proc <process_name_search> --create-files <file1> ...
        """
        self._link_files(objects, args, out, direction='out')

    def unlink_files(self, objects, args, out=sys.stdout):
        """Unlink files to processes

        Using:
            mc proc --id <proc_id> --unlink-files <file1> ...
            mc proc <process_name_search> --unlink-files <file1> ...
        """
        proj = clifuncs.make_local_project()

        if not args.unlink_files:
            print("No files")
            return

        # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
        refpath = os.path.dirname(proj.local_path)
        paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.unlink_files]
        files = [clifuncs.get_file_by_path(proj, p) for p in paths]
        file_ids = [file.id for file in files]

        resulting_objects = []
        for obj in objects:
            try:
                resulting_objects.append(remove_files_from_process(proj.id, obj.id, file_ids, proj.remote))
            except requests.exceptions.HTTPError as e:
                try:
                    print(json.dumps(e.response.json(), indent=2))
                    print(e.response.json()["error"])
                except:
                    print("  FAILED, for unknown reason")
                return False
        self.output(resulting_objects, args, out=out)
        return

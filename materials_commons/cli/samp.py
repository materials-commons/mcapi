import json
import requests
import sys

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs
from materials_commons.api import __api as mc_raw_api
from materials_commons.cli.list_objects import ListObjects
from materials_commons.api.mc_object_utility import make_object

def get_sample_v2(project_id, sample_id, remote=None):
    return mc_raw_api.get_sample_by_id(project_id, sample_id, remote=remote, apikey=None)

def get_sample_v3(sample_id, remote=None):
    result = clifuncs.post_v3(
        "getSample",
        {
            'sample_id': sample_id
        },
        remote=remote,
        use_data=True)
    return result

# def add_samples_to_dataset(project_id, sample_id, files, remote=None):
#     """
#     Arguments
#     ---------
#     project_id: str, Project ID
#     sample_id: str, Sample ID
#     files: list of objects
#
#         Ex: files: [
#                 {"file_id":<id>, "direction": <'in', 'out', or ''>},
#                 ...
#             ]
#
#     Notes
#     -----
#     If file direction == 'in' or 'out', then the file is included in both 'files' and 'input_files' or 'output_files', respectively.
#
#     If file direction == '' (empty string), then the file is only included in 'files'.
#
#     """
#     result = clifuncs.post_v3(
#         "addFilesToProcess",
#         {
#             'project_id': project_id,
#             'process_id': process_id,
#             'files': [{'file_id':id, 'direction':''} for id in file_ids]
#         },
#         remote=remote,
#         use_data=True)
#     return mcapi.Process(result['data'])
#
# def remove_samples_from_dataset(project_id, process_id, file_ids, remote=None):
#     """
#     Arguments
#     ---------
#     project_id: str, Project ID
#     process_id: str, Process ID
#     file_ids: list of str, List of File IDs
#
#     Notes
#     -----
#     Files are stored with a direction, one of 'in', 'out', or '' (empty string). A file with
#     direction 'in' or 'out' is listed both in "input_files" and "files", or "output_files"
#     and "files", respectively. Removing a file removes it from all lists.
#     """
#     result = clifuncs.post_v3(
#         "removeFilesFromProcess",
#         {
#             'project_id': project_id,
#             'process_id': process_id,
#             'files': file_ids
#         },
#         remote=remote)
#     print(json.dumps(result['data'], indent=2))
#     return mcapi.Process(result['data'])


class SampSubcommand(ListObjects):
    def __init__(self):
        super(SampSubcommand, self).__init__(
            ["samp"], "Sample", "Samples",
            expt_member=True,
            list_columns=['name', 'owner', 'id', 'mtime'],
            deletable=True,
            custom_selection_actions=['add_to_dataset', 'remove_from_dataset', 'create_dataset'],
            request_confirmation_actions={
                'add_to_dataset': 'Are you sure you want to add these samples to the dataset?',
                'remove_from_dataset': 'Are you sure you want to remove these samples from the dataset?',
                'create_dataset': 'Create a new dataset with these samples?'
            }
        )

    def get_all_from_experiment(self, expt):
        return expt.get_all_samples()

    def get_all_from_project(self, proj):
        return proj.get_all_samples()

    def get_all_from_dataset(self, dataset):
        return dataset.get_all_samples()

    def list_data(self, obj):
        return {
            'name': clifuncs.trunc(obj.name, 40),
            'owner': obj.owner,
            'id': obj.id,
            'mtime': clifuncs.format_time(obj.mtime)
        }

    def print_details(self, obj, out=sys.stdout):
        obj.pretty_print(shift=0, indent=2, out=out)

    def delete(self, objects, args, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting samples.\n')
            out.write('Aborting\n')
            return
        for obj in objects:

            try:
                result = obj.delete()
            except requests.exceptions.HTTPError as e:
                try:
                    print(e.response.json()['error'])
                except:
                    print("  FAILED, for unknown reason")
                result = None

            if result is None:
                out.write('Could not delete sample: ' + obj.name + ' ' + obj.id + '\n')
                out.write('At present, a sample can not be deleted via the mcapi if ')
                out.write('any of the following are true: \n')
                out.write('  (1) it is input to a process,\n')
                out.write('  (2) is is in a dataset \n')
            else:
                out.write('Deleted sample: ' + obj.name + ' ' + obj.id + '\n')

    def add_custom_options(self, parser):

        # add/remove samples to dataset
        parser.add_argument('--add-to-dataset', type=str, default="", metavar='DATASET_ID', help='Add selected samples to the dataset with given ID.')
        parser.add_argument('--remove-from-dataset', type=str, default="", metavar='DATASET_ID', help='Remove selected samples to the dataset with given ID.')
        parser.add_argument('--create-dataset', type=str, default="", metavar='DATASET_NAME', help='Create a new dataset with the selected samples.')
        parser.add_argument('--desc', type=str, default='', help='For use with --create-dataset, set dataset description')


    def add_to_dataset(self, objects, args, out=sys.stdout):
        """Add samples to a dataset"""

        proj = clifuncs.make_local_project()
        dataset_id = args.add_to_dataset
        dataset = mcapi.add_samples_to_dataset(proj.id, dataset_id, [samp.id for samp in objects], remote=proj.remote)

        #TODO
        print("Warning: Related processes are not currently being added to the dataset along with the samples.")
        print("To clone a new dataset that updates the processes based on the current samples, use:")
        print("    mc dataset --proj --id " + dataset.id + " --clone --refresh-processes")

        return

    def remove_from_dataset(self, objects, args, out=sys.stdout):
        """Remove samples from a dataset"""

        proj = clifuncs.make_local_project()
        dataset_id = args.remove_from_dataset
        dataset = mcapi.remove_samples_from_dataset(proj.id, dataset_id, [samp.id for samp in objects], remote=proj.remote)

        #TODO
        print("Warning: Related processes that are only included in the dataset due to the samples that were removed are not currently being removed.")
        print("To clone a new dataset that updates the processes based on the current samples, use:")
        print("    mc dataset --proj --id " + dataset.id + " --clone --refresh-processes")

        return

    def create_dataset(self, objects, args, out=sys.stdout):
        """Create a dataset with the selected samples"""

        proj = clifuncs.make_local_project()
        dataset_name = args.create_dataset
        dataset_desc = ""
        if args.desc:
            dataset_desc = args.desc
        dataset = mcapi.create_dataset(proj.id, dataset_name, dataset_desc, sample_ids=[samp.id for samp in objects], remote=proj.remote)

        return

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

class SampSubcommand(ListObjects):
    def __init__(self):
        super(SampSubcommand, self).__init__(
            ["samp"], "Sample", "Samples",
            expt_member=True,
            list_columns=['name', 'owner', 'id', 'mtime'],
            deletable=True
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

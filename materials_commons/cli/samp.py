import sys
from .list_objects import ListObjects
from .functions import _trunc_name, _format_mtime


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

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }

    def delete(self, objects, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting samples.\n')
            out.write('Aborting\n')
            return
        for obj in objects:
            result = obj.delete()
            if result is None:
                out.write('Could not delete sample: ' + obj.name + ' ' + obj.id + '\n')
                out.write('At present, a sample can not be deleted via the mcapi if ')
                out.write('any of the following are true: \n')
                out.write('  (1) it is input to a process,\n')
                out.write('  (2) is is in a dataset \n')
            else:
                out.write('Deleted sample: ' + obj.name + ' ' + obj.id + '\n')

import sys
from .list_objects import ListObjects
from .functions import _trunc_name, _format_mtime


class ProcSubcommand(ListObjects):

    def __init__(self):
        super(ProcSubcommand, self).__init__(
            ["proc"], "Process", "Processes", expt_member=True,
            list_columns=['name', 'owner', 'template_name', 'id', 'mtime'],
            deletable=True
        )

    def get_all_from_experiment(self, expt):
        return expt.get_all_processes()

    def get_all_from_project(self, proj):
        return proj.get_all_processes()

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }

    def delete(self, objects, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting processes.\n')
            out.write('Aborting\n')
            return
        for obj in objects:
            if getattr(obj, 'experiment', None) is None:
                out.write('Could not delete processes.\n')
                out.write('Currently, processes must be deleted via an experiment.\n')
                out.write('Please include the --expt option.\n')
                out.write('Aborting\n')
                return
            result = obj.delete()
            if result is None:
                out.write('Could not delete process: ' + obj.name + ' ' + obj.id + '\n')
                out.write('At present, a process can not be deleted via the mcapi if ')
                out.write('any of the following are true: \n')
                out.write('  (1) it is not a leaf node in the workflow,\n')
                out.write('  (2) is is in a dataset, \n')
                out.write('  (3) it is a create sample (type) process with one or more output samples.\n')
            else:
                out.write('Deleted process: ' + obj.name + ' ' + obj.id + '\n')

from mcapi.cli.list_objects import ListObjects
from mcapi.cli.functions import _trunc_name, _format_mtime

class SampSubcommand(ListObjects):
    def __init__(self):
        super(SampSubcommand, self).__init__(["samp"], "Sample", "Samples", 
            expt_member=True, list_columns=['name', 'owner', 'id', 'mtime'])
    
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

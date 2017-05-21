from mcapi.cli.list_objects import ListObjects
from mcapi.cli.functions import _trunc_name

class ProcSubcommand(ListObjects):
    def __init__(self):
        super(ProcSubcommand, self).__init__("proc", "Process", "Processes", 
            expt_member=True, list_columns=['name', 'template_name', 'id', 'mtime'])
    
    def get_all_from_experiment(self, expt):
        return expt.get_all_processes()
    
    def get_all_from_project(self, proj):
        return proj.get_all_processes()
    
    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': obj.mtime.strftime("%b %Y %d %H:%M:%S")
        }
    
    
    


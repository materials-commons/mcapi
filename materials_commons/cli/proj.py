import sys
import json
from ..api import get_all_projects
from .list_objects import ListObjects
from .functions import _trunc_name, _proj_path, _format_mtime, _proj_config


class ProjSubcommand(ListObjects):
    def __init__(self):
        super(ProjSubcommand, self).__init__(
            ["proj"], "Project", "Projects",
            requires_project=False, proj_member=False, expt_member=False,
            list_columns=['current', 'name', 'owner', 'id', 'mtime'],
            headers=['', 'name', 'owner', 'id', 'mtime'],
            deletable=True
        )

    def get_all_from_experiment(self, expt):
        raise Exception("Projects are not members of experiments")

    def get_all_from_project(self, proj):
        raise Exception("Projects are not members of projects")

    def get_all(self):
        projs = get_all_projects()
        # TODO: not sure why this is happening?
        for p in projs:
            if p.input_data['id'] is id:
                p.input_data['id'] = p.id
        return projs

    def list_data(self, obj):
        _is_current = ' '
        if _proj_path() is not None:
            with open(_proj_config()) as f:
                j = json.load(f)
            if obj.id == j['project_id']:
                _is_current = '*'

        return {
            'current': _is_current,
            'owner': obj.owner,
            'name': _trunc_name(obj),
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }

    def delete(self, objects, dry_run, out=sys.stdout):
        for obj in objects:
            obj.delete(dry_run=dry_run)
            out.write('Deleted project: ' + obj.name + ' ' + obj.id + '\n')
            for key, val in obj.delete_tally.__dict__.items():
                out.write(str(key) + ' ' + str(val) + '\n')
            out.write('\n')

from ..api import get_all_templates
from .list_objects import ListObjects
from .functions import _trunc_name, _format_mtime


class TemplatesSubcommand(ListObjects):
    def __init__(self):
        super(TemplatesSubcommand, self).__init__(
            ["templates"], "Template", "Templates",
            requires_project=False, proj_member=False, expt_member=False,
            list_columns=['name', 'id'], has_owner=False
        )

    def get_all_from_experiment(self, expt):
        raise Exception("Templates are not members of experiments")

    def get_all_from_project(self, proj):
        raise Exception("Templates are not members of projects")

    def get_all(self):
        return get_all_templates()

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }

import sys

import materials_commons.api as mcapi
from materials_commons.cli.list_objects import ListObjects
import materials_commons.cli.functions as clifuncs


class TemplatesSubcommand(ListObjects):
    def __init__(self):
        super(TemplatesSubcommand, self).__init__(
            ["templates"], "Template", "Templates",
            requires_project=False, non_proj_member=True, proj_member=False, expt_member=False,
            list_columns=['name', 'id'], has_owner=False
        )

    def get_all_from_experiment(self, expt):
        raise Exception("Templates are not members of experiments")

    def get_all_from_project(self, proj):
        raise Exception("Templates are not members of projects")

    def get_all_from_remote(self, remote):
        return clifuncs.get_all_templates_or_exit(remote=remote)

    def list_data(self, obj):
        return {
            'name': clifuncs.trunc(obj.name, 40),
            'id': obj.id,
            'mtime': clifuncs.format_time(obj.mtime)
        }

    def print_details(self, obj, out=sys.stdout):
        obj.pretty_print(shift=0, indent=2, out=out)

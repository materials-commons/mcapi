import sys
import json

import materials_commons.api as mcapi
from materials_commons.cli.exceptions import MCCLIException
from materials_commons.cli.list_objects import ListObjects
import materials_commons.cli.functions as clifuncs


class ProjSubcommand(ListObjects):
    def __init__(self):
        super(ProjSubcommand, self).__init__(
            ["proj"], "Project", "Projects",
            requires_project=False, non_proj_member=True, proj_member=False, expt_member=False,
            remote_help='Remote to get projects from',
            list_columns=['current', 'name', 'owner', 'id', 'mtime'],
            headers=['', 'name', 'owner', 'id', 'mtime'],
            deletable=True
        )

    def get_all_from_experiment(self, expt):
        raise MCCLIException("Projects are not members of experiments")

    def get_all_from_project(self, proj):
        raise MCCLIException("Projects are not members of projects")

    def get_all_from_remote(self, remote):

        # projs = clifuncs.v2_get_all_projects_or_exit(remote=remote)
        # # TODO: not sure why this is happening?
        # for p in projs:
        #     if p.input_data['id'] is id:
        #         p.input_data['id'] = p.id
        # return projs

        return clifuncs.post_v3("ui:getProjectsForUser", remote=remote)['data']

    def list_data(self, obj):
        from materials_commons.cli.functions import getit, trunc, format_time

        _is_current = ' '
        pconfig = clifuncs.read_project_config()
        if pconfig and getit(obj, 'id') == pconfig.project_id:
            _is_current = '*'

        return {
            'current': _is_current,
            'owner': getit(obj, 'owner'),
            'name': trunc(getit(obj, 'name'), 40),
            'id': getit(obj, 'id'),
            'mtime': format_time(getit(obj, 'mtime'))
        }

    def print_details(self, obj, out=sys.stdout):
        if isinstance(obj, mcapi.Project):
            obj.pretty_print(shift=0, indent=2, out=out)
        else:
            print("name:", obj['name'])
            print("  description:", obj['description'])
            print("  id:", obj['id'])
            print("  owner:", obj['owner'])

    def delete(self, objects, args, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting projects.\n')
            out.write('Aborting\n')
            return
        remote = self.get_remote(args)
        for obj in objects:
            try:
                params = {'project_id': clifuncs.getit(obj, 'id')}
                result = clifuncs.post_v3("deleteProject", params, remote=remote)
                msg = result['data']['success']
                print("Deleted project: ", clifuncs.getit(obj, 'name'), "(" + clifuncs.getit(obj, 'id') + ")")
            except MCCLIException:
                print("Delete of project failed: ", clifuncs.getit(obj, 'name'), "(" + clifuncs.getit(obj, 'id') + ")")

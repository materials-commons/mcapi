import sys
import json
import yaml
from collections import OrderedDict

import materials_commons2.models as models
from materials_commons2_cli.exceptions import MCCLIException
from materials_commons2_cli.list_objects import ListObjects
from materials_commons2_cli.functions import read_project_config, getit, trunc, format_time, \
    remove_hidden_project_files


class ProjSubcommand(ListObjects):
    def __init__(self):
        super(ProjSubcommand, self).__init__(
            ["proj"], "Project", "Projects",
            requires_project=False, non_proj_member=True, proj_member=False, expt_member=False,
            remote_help='Remote to get projects from',
            list_columns=['current', 'name', 'owner', 'id', 'uuid', 'mtime'],
            headers=['', 'name', 'owner', 'id', 'uuid', 'mtime'],
            deletable=True
        )

    def get_all_from_experiment(self, expt):
        raise MCCLIException("Projects are not members of experiments")

    def get_all_from_project(self, proj):
        raise MCCLIException("Projects are not members of projects")

    def get_all_from_remote(self, remote):
        return remote.get_all_projects()

    def list_data(self, obj):
        _is_current = ' '
        project_config = read_project_config()
        if project_config and getit(obj, 'id') == project_config.project_id:
            _is_current = '*'

        return {
            'current': _is_current,
            'owner': getit(obj, 'owner_id'),    # TODO: owner email
            'name': trunc(getit(obj, 'name'), 40),
            'id': getit(obj, 'id'),
            'uuid': getit(obj, 'uuid'),
            'mtime': format_time(getit(obj, 'updated_at'))
        }

    def print_details(self, obj, out=sys.stdout):
        description = None
        if obj.description:
            description = obj.description
        data = [
            {"name": obj.name},
            {"description": description},
            {"id": obj.id},
            {"uuid": obj.uuid},
            {"owner": obj.owner_id}
        ]
        for d in data:
            out.write(yaml.dump(d, width=70, indent=4))

    def delete(self, objects, args, dry_run, out=sys.stdout):
        # TODO: this needs testing
        if dry_run:
            out.write('Dry-run is not yet possible when deleting projects.\n')
            out.write('Aborting\n')
            return
        remote = self.get_remote(args)
        for obj in objects:
            try:
                # params = {'project_id': clifuncs.getit(obj, 'id')}
                # result = clifuncs.post_v3("deleteProject", params, remote=remote)
                project_id = getit(obj, 'id')
                result = remote.delete_project(project_id)
                # TODO: check return value
                out.write('Deleted project: ' + obj.name + ' ' + str(obj.id) + '\n')
                out.write('Note that this only deletes the project remotely and does not delete any '
                    'local files.\n')
            except:
                out.write('Delete of project failed: ' + obj.name + ' ' + str(obj.id) + '\n')

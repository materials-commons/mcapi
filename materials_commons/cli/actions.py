import json
import os.path
import requests
import sys
import materials_commons.api as mcapi
from ..api import __api as mc_raw_api

from materials_commons.cli.list_objects import ListObjects
import materials_commons.cli.functions as clifuncs

def show_documentation_from_remote(remote=None):
    remote = mc_raw_api.configure_remote(remote, None)
    api_url = "showDocumentation"
    return clifuncs.post_v3(api_url, remote=remote)

class ActionsSubcommand(ListObjects):
    def __init__(self):
        super(ActionsSubcommand, self).__init__(
            ["actions"], "Action", "Actions",
            requires_project=False, non_proj_member=True, proj_member=False, expt_member=False,
            remote_help='Remote to call actions at',
            list_columns=['name', 'version', 'description'],
            headers=['name', 'version', 'description'],
            custom_actions=['post'],
            deletable=False
        )

    def get_all_from_experiment(self, expt):
        raise Exception("Actions are not members of experiments")

    def get_all_from_project(self, proj):
        raise Exception("Actions are not members of projects")

    def get_all_from_remote(self, remote):
        actions = show_documentation_from_remote(remote=remote)["documentation"]
        actionlist = []
        for action_name, action in actions.items():
            for version_name, action_version in actions[action_name].items():
                actionlist.append(action_version)
        return actionlist

    def list_data(self, obj):
        return {
            'name': obj['name'],
            'version': obj['version'],
            'description': clifuncs.trunc(obj['description'], 80),
        }

    def add_custom_options(self, parser):

        # for --create, add experiment description
        parser.add_argument('--post', nargs='*', metavar=('ACTION', 'PARAMSFILE'), help='Call with POST at optional (--remote) or standard remote (local project remote, else default remote). Parameters can be read from optional file. If not specified, will insert apikey, local project id, and current experiment id into params automatically.')

        # for --create, add experiment description
        parser.add_argument('--v4', action="store_true", default=False, help='Call with POST v4')

    def post(self, args, out=sys.stdout):
        """Download dataset zipfile, --down

        .. note:: The downloaded dataset is named <dataset_id>.zip
        """

        # action name
        name = args.post[0]

        # make params, from specified file or use {}
        params = {}
        if len(args.post) == 2:
            with open(args.post[1], 'r') as f:
                params = json.load(f)

        # check for local project
        config = mcapi.Config()
        pconfig = clifuncs.read_project_config()
        project_id = None
        experiment_id = None
        if pconfig:
            project_id = pconfig.project_id
            experiment_id = pconfig.experiment_id

        # auto insert project_id
        if project_id and 'project_id' not in params:
            params['project_id'] = project_id

        # auto insert experiment_id
        if experiment_id and 'experiment_id' not in params:
            params['experiment_id'] = experiment_id

        # get standard remote (--remote, else local project remote, else default remote)
        default_remote = None
        if pconfig and pconfig.remote:
            rconfig = pconfig.remote
            if rconfig not in config.remotes:
                print("Could not make Remote, failed to find remote config: {0} {1}".format(rconfig.email, rconfig.mcurl))
                print_help()
                exit(1)
            rconfig_with_apikey = config.remotes[config.remotes.index(rconfig)]
            default_remote = mcapi.Remote(rconfig_with_apikey)
        remote = clifuncs.optional_remote(args, default_remote=default_remote)

        try:
            if args.v4:
                result = clifuncs.post_v4(name, params, remote)
            else:
                result = clifuncs.post_v3(name, params, remote)
        except requests.exceptions.HTTPError as e:
            try:
                print(e.response.json()["error"])
            except:
                try:
                    print(json.dumps(e.response.json(), indent=2))
                except:
                    print("  FAILED, for unknown reason")
            return

        out.write(json.dumps(result, indent=2))
        out.write("\n")

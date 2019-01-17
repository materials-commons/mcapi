import sys
import os
import json
import argparse
from ..api import create_project
from .functions import _mc_remotes, _print_projects, _proj_config, \
    make_local_project


def init_subcommand(argv=sys.argv):
        """
        Initialize a new project

        mc init [--remote <remote>] [--desc <description>]

        """
        parser = argparse.ArgumentParser(
            description='Initialize current working directory as a new project',
            prog='mc init')
        parser.add_argument('--remote', type=str, default='origin', help='Remote name')
        parser.add_argument('--desc', type=str, default='', help='Project description')

        # ignore 'mc init'
        args = parser.parse_args(argv[2:])

        remotes = _mc_remotes()
        if args.remote not in remotes:
            print("unrecognized remote:", args.remote)
            parser.print_help()
            exit(1)
        remote = remotes[args.remote]

        if os.path.exists(".mc"):
            try:
                proj = make_local_project()
                print("Already in project.  name:", proj.name, "  id:", proj.id)
                return
            except Exception:
                raise Exception(".mc directory exists, but could not find existing project")

        name = os.path.basename(os.getcwd())

        project = create_project(name, args.desc)

        print("Created new project at:", remote.config.mcurl)
        _print_projects([project], project)

        if not os.path.exists('.mc'):
            os.mkdir('.mc')
        with open(_proj_config(), 'w') as f:
            # set a default current experiment?
            data = {'remote_url': remote.config.mcurl, 'project_id': project.id, 'experiment_id': None}
            json.dump(data, f)

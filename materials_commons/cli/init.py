import sys
import os
import json
import argparse

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs


def init_subcommand(argv=sys.argv):
    """
    Initialize a new project

    mc init [--remote <remote>] [--desc <description>]

    """
    parser = argparse.ArgumentParser(
        description='Initialize current working directory as a new project',
        prog='mc init')
    clifuncs.add_remote_option(parser, 'Remote to create project at')
    parser.add_argument('--desc', type=str, default='', help='Project description')

    # ignore 'mc init'
    args = parser.parse_args(argv[2:])

    proj_path = os.getcwd()
    pconfig = clifuncs.read_project_config(proj_path)

    # if .mc directory already exists, print error message
    if pconfig:
        try:
            proj = clifuncs.make_local_project(proj_path)
        except mcapi.MCNotFoundException as e:
            print(e)
            print("A .mc directory already exists, but could not find existing project.")
            print("This may mean the project was deleted.")
            print("If you wish to create a new project here, first delete the .mc directory.")
            return

        print("Already in project.  name:", proj.name, "  id:", proj.id)
        return

    # get remote, from command line option or default
    remote = clifuncs.optional_remote(args)

    # create new project
    name = os.path.basename(proj_path)
    proj = clifuncs.create_project_or_exit(name, args.desc, remote=remote)
    proj.local_path = proj_path
    proj.remote = remote

    print("Created new project at:", remote.config.mcurl)
    clifuncs.print_projects([proj], proj)

    # create project config directory and file
    pconfig = clifuncs.ProjectConfig(proj.local_path)
    pconfig.remote = proj.remote.config
    pconfig.project_id = proj.id
    pconfig.save()

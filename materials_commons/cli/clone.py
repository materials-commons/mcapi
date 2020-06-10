import argparse
import json
import os
import sys

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs


def clone_subcommand(argv=sys.argv):
    """
    'Clone' a project, i.e. set the local directory tree where files should
    be uploaded/downloaded. Creates a '.mc/config.json'.

    mc clone <projid> [--remote <remotename>]

    """
    parser = argparse.ArgumentParser(
        description='Clone an existing project',
        prog='mc clone')
    parser.add_argument('id', help='Project id')
    clifuncs.add_remote_option(parser, 'Remote to clone project from')

    # ignore 'mc clone'
    args = parser.parse_args(argv[2:])

    # get remote, from command line option or default
    remote = clifuncs.optional_remote(args)

    # check if in a project directory
    if clifuncs.project_exists():
        print("mc project already exists at", clifuncs.project_path())
        exit(1)

    # get Project
    proj = clifuncs.get_project_by_id_or_exit(args.id, remote=remote)

    # check if project already exists
    dest = os.path.join(os.getcwd(), proj.name)
    if clifuncs.project_path(dest):
        print("mc project already exists at", clifuncs.project_path(dest))
        exit(1)

    proj.local_path = dest
    proj.remote = remote

    # create project directory
    if not os.path.exists(proj.local_path):
        os.mkdir(proj.local_path)

    pconfig = clifuncs.ProjectConfig(proj.local_path)
    pconfig.remote = proj.remote.config
    pconfig.project_id = proj.id
    pconfig.project_uuid = proj.uuid
    pconfig.save()

    # done
    print("Cloned project from", remote.config.mcurl, "to", dest)
    clifuncs.print_projects([proj])

import argparse
import json
import os
import sys
import time

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs
import materials_commons.cli.tree_functions as treefuncs
from materials_commons.cli.treedb import RemoteTree


def mkdir_subcommand(argv=sys.argv):
    """
    Make remote directories.

    mc mkdir [<pathspec> ...]

    """
    parser = argparse.ArgumentParser(
        description='Make remote directories',
        prog='mc mkdir')
    parser.add_argument('paths', nargs='*', default=[os.getcwd()], help='Directory names')
    parser.add_argument('-p', action="store_true", default=False, help='Create intermediate directories as necessary')
    parser.add_argument('--remote-only', action="store_true", default=False,
                        help='Make remote directories only. Does not compare to local tree.')

    # ignore 'mc ls'
    args = parser.parse_args(argv[2:])

    proj = clifuncs.make_local_project()
    pconfig = clifuncs.read_project_config()

    # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
    refpath = os.path.dirname(proj.local_path)
    paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.paths]

    remotetree = None
    if pconfig.remote_updatetime:
        remotetree = RemoteTree(proj, pconfig.remote_updatetime)

    for path in paths:
        path = os.path.relpath(os.path.abspath(p), refpath)
        treefuncs.mkdir(proj, path, remote_only=args.remote_only, create_intermediates=args.p, remotetree=remotetree)

    return

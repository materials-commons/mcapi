
import argparse
import os
import requests
import shutil
import sys
import time

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs
import materials_commons.cli.tree_functions as treefuncs
from materials_commons.cli.treedb import LocalTree, RemoteTree

def rm_subcommand(argv=sys.argv):
    """
    Remove files and directories from Materials Commons and locally

    mc rm [--local] [--remote] [--force] [<pathspec> ...]

    """
    parser = argparse.ArgumentParser(
        description='remove files and directories',
        prog='mc down')
    parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
    parser.add_argument('-r', '--recursive', action="store_true", default=False,
                        help='Remove recursively')
    parser.add_argument('--remote-only', action="store_true", default=False,
                        help='Remove remote files only. Does not compare to local files.')
    parser.add_argument('--no-compare', action="store_true", default=False,
                        help='Remove even if local and remote files differ.')

    # needs re-working:
    # parser.add_argument('-n', '--dry-run', action="store_true", default=False,
    #                     help='Show what would be removed, without actually removing.')

    # ignore 'mc rm'
    args = parser.parse_args(argv[2:])

    proj = clifuncs.make_local_project()
    pconfig = clifuncs.read_project_config()

    # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
    refpath = os.path.dirname(proj.local_path)
    paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.paths]

    localtree = None
    if args.no_compare == False:
        localtree = LocalTree(proj)

    remotetree = None
    if pconfig.remote_updatetime:
        remotetree = RemoteTree(proj, pconfig.remote_updatetime)

    remover = treefuncs.remove(proj, paths, recursive=args.recursive, no_compare=args.no_compare, remote_only=args.remote_only, localtree=localtree, remotetree=remotetree)

    return

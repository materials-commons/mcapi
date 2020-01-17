import argparse
import json
import os
import requests
import sys
import time

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs
import materials_commons.cli.tree_functions as treefuncs
import materials_commons.cli.exceptions as cliexcept
from materials_commons.cli.treedb import RemoteTree

from ..api import __api as mc_raw_api

def mv_subcommand(argv=sys.argv):
    """
    Move files

    mc move <src> <target>
    mc move <src> ... <directory>

    """

    desc = "Move files. Use `mc move <src> <target>` to move and/or rename a file or directory. Use `mc move <src> ... <directory>` to move a list of files or directories into an existing directory."

    parser = argparse.ArgumentParser(
        description=desc,
        prog='mc mv')
    parser.add_argument('paths', nargs="*", help='Sources and target or directory destination')
    parser.add_argument('--remote-only', action="store_true", default=False,
                        help='Move remote files only. Does not compare to local files.')

    # ignore 'mc ls'
    args = parser.parse_args(argv[2:])

    proj = clifuncs.make_local_project()
    pconfig = clifuncs.read_project_config()

    localtree = None

    remotetree = None
    if pconfig.remote_updatetime:
        remotetree = RemoteTree(proj, pconfig.remote_updatetime)

    # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
    refpath = os.path.dirname(proj.local_path)
    paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.paths]

    treefuncs.move(proj, paths, remote_only=args.remote_only, localtree=localtree, remotetree=remotetree)

    return

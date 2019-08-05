import argparse
import os
import sys
import time

import materials_commons.cli.functions as clifuncs
import materials_commons.cli.globus as cliglobus
import materials_commons.cli.tree_functions as treefuncs
from materials_commons.cli.treedb import LocalTree, RemoteTree

def up_subcommand(argv=sys.argv):
    """
    upload files to Materials Commons

    mc up [-r] [<pathspec> ...]

    """
    parser = argparse.ArgumentParser(
        description='upload files',
        prog='mc up')
    parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
    parser.add_argument('-r', '--recursive', action="store_true", default=False,
                        help='Upload directory contents recursively')
    parser.add_argument('--limit', nargs=1, type=float, default=[50],
                        help='File size upload limit (MB). Default=50MB.')
    parser.add_argument('-g', '--globus', action="store_true", default=False,
                        help='Use globus to upload files.')
    parser.add_argument('--label', nargs=1, type=str,
                        help='Globus transfer label to make finding tasks simpler.')
    # parser.add_argument('--batchsize', nargs=1, type=int, default=[50],
    #                     help='Maximum number of files per globus transfer. Default=0 (all files).')

    # ignore 'mc up'
    args = parser.parse_args(argv[2:])

    proj = clifuncs.make_local_project()

    pconfig = clifuncs.read_project_config(proj.local_path)
    remotetree = None
    if pconfig.remote_updatetime:
        remotetree = RemoteTree(proj, pconfig.remote_updatetime)

    paths = treefuncs.clipaths_to_mcpaths(proj.local_path, args.paths)

    if args.globus:
        label = proj.name
        if args.label:
            label = args.label[0]

        globus_ops = cliglobus.GlobusOperations()
        globus_ops.upload_v0(proj, paths, recursive=args.recursive, label=label)

    else:
        treefuncs.standard_upload(proj, paths, recursive=args.recursive, limit=args.limit[0], remotetree=remotetree)

    return

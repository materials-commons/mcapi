import argparse
import copy
import os
import sys
import time

import pandas
from sortedcontainers import SortedSet
from tabulate import tabulate

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs
import materials_commons.cli.tree_functions as treefuncs
from materials_commons.cli.treedb import LocalTree, RemoteTree

#  Want to print() something like:
#
#  warning! file0 is a local file and remote dir!
#  warning! file1 is a local directory and remote file!
#
#  remote_owner local_mtime local_size remote_mtime remote_size file0
#             - local_mtime local_size            -           - file1
#  remote_owner           -          - remote_mtime remote_size file2
#
#  dir1:
#  remote_owner local_mtime local_size remote_mtime remote_size file0
#             - local_mtime local_size            -           - file1
#  remote_owner           -          - remote_mtime remote_size file2
#
#  dir2:
#  remote_owner local_mtime local_size remote_mtime remote_size file0
#             - local_mtime local_size            -           - file1
#  remote_owner           -          - remote_mtime remote_size file2
#

def _make_printing_df(proj, data, refpath=None, checksum=False):
    """
    Construct DataFrame with 'mc ls' results for paths. Also outputs
    the sets of paths that are files or directories (either local or remote).

    Arguments
    ---------
    proj: mcapi.Project
        Project instance with proj.local_path indicating local project location

    data: dict
        Output from `materials_commons.cli.tree_functions.ls_data`

    refpath: str or None
        Local absolute path that names are printed relative to. If None, uses os.getcwd().

    checksum: bool (optional, default=False)
        If True, include 'eq' in the output data.

    Returns
    -------
    df: pandas.DataFrame containing:
        'l_mtime', 'l_size', 'l_type', 'r_mtime', 'r_size', 'r_type', 'eq' (optionally), 'name', 'id'
    """
    path_data = []

    # import json
    # for record in data:
    #     print(json.dumps(record, indent=2))
    #     print("-------------------")

    if checksum:
        columns = ['l_mtime', 'l_size', 'l_type', 'r_mtime', 'r_size', 'r_type', 'eq', 'name', 'id']
    else:
        columns = ['l_mtime', 'l_size', 'l_type', 'r_mtime', 'r_size', 'r_type', 'name', 'id']

    record_init = {k: '-' for k in columns}
    if refpath is None:
        refpath = os.getcwd()

    def _get_name(path):
        from os.path import abspath, dirname, join, relpath
        local_abspath=abspath(join(dirname(proj.local_path), path))
        return relpath(local_abspath, refpath)

    for path in sorted(data.keys()):
        record = copy.deepcopy(record_init)
        rec = data[path]

        if not rec['l_type'] and not rec['r_type']:
            continue

        if rec['l_mtime'] is not None:
            record['l_mtime'] = clifuncs.format_time(rec['l_mtime'])
        if rec['l_size'] is not None:
            record['l_size'] = clifuncs.humanize(rec['l_size'])
        if rec['l_type'] is not None:
            record['l_type'] = rec['l_type']
        if rec['r_mtime'] is not None:
            record['r_mtime'] = clifuncs.format_time(rec['r_mtime'])
        if rec['r_size'] is not None:
            record['r_size'] = clifuncs.humanize(rec['r_size'])
        if rec['r_type'] is not None:
            record['r_type'] = rec['r_type']
        if 'eq' in rec and rec['eq'] is not None:
            record['eq'] = rec['eq']
        record['name'] = _get_name(path)
        if 'id' in rec and rec['id'] is not None:
            record['id'] = rec['id']

        path_data.append(record)

    return pandas.DataFrame(path_data, columns=columns).sort_values(by='name')

def _ls_print(proj, data, refpath=None, printjson=False, checksum=False):
    """Print treecompare output for a set of files, or directory children"""

    # print warnings for type mismatches
    treefuncs.warn_for_type_mismatches(data)

    if printjson:
        for path, record in data.items():
            if record['r_obj']:
                print(record['r_obj'].input_data)
    else:
        df = _make_printing_df(proj, data, refpath=refpath, checksum=checksum)
        if refpath:
            print(os.path.relpath(refpath, os.getcwd()) + ":")
        if df.shape[0]:
            #print(df.to_string(index=False))
            print(tabulate(df, showindex=False, headers=df.columns, tablefmt="plain"))
            print("")

def ls_subcommand(argv=sys.argv):
    """
    'ls' a project directory to see local and remote files and directories.

    mc ls [<pathspec> ...]

    """
    parser = argparse.ArgumentParser(
        description='List local & remote directory contents',
        prog='mc ls')
    parser.add_argument('paths', nargs='*', default=[os.getcwd()], help='Files or directories')
    parser.add_argument('--checksum', action="store_true", default=False, help='Calculate MD5 checksum for local files')
    parser.add_argument('--json', action="store_true", default=False, help='Print JSON exactly')

    # ignore 'mc ls'
    args = parser.parse_args(argv[2:])
    updatetime = time.time()

    proj = clifuncs.make_local_project()
    pconfig = clifuncs.read_project_config()

    # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
    refpath = os.path.dirname(proj.local_path)
    paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.paths]

    if args.checksum:
        localtree = LocalTree(proj)
    else:
        localtree = None

    if args.json:
        remotetree = None
    else:
        remotetree = RemoteTree(proj, pconfig.remote_updatetime)

    # compare local and remote tree
    files_data, dirs_data, child_data, not_existing = treefuncs.treecompare(
        proj, paths, checksum=args.checksum,
        localtree=localtree, remotetree=remotetree)

    if pconfig.remote_updatetime:
        print("** Fetch lock ON at:", clifuncs.format_time(pconfig.remote_updatetime), "**")

    if not_existing:
        for path in not_existing:
            local_abspath = os.path.join(refpath, path)
            print(os.path.relpath(local_abspath) + ": No such file or directory")
        print("")

    # print files
    _ls_print(proj, files_data, refpath=None, printjson=args.json, checksum=args.checksum)

    # print directory children
    for d in child_data:
        local_dirpath = os.path.join(refpath, d)
        _ls_print(proj, child_data[d], refpath=local_dirpath, printjson=args.json, checksum=args.checksum)


    return

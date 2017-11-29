import sys
import os
import argparse
from .functions import make_local_project
from ..api import File, Directory
import copy
import time
import hashlib
import pandas
from tabulate import tabulate
from sortedcontainers import SortedSet


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


def _ls_group(proj, paths, files_only=True, checksum=False, json=False, id=False):
    """
    Construct DataFrame with 'mc ls' results for paths. Also outputs
    the sets of paths that are files or directories (either local or remote).

    Arguments:
        files_only: If True, only include files in output DataFrame
        checksum: If True, calculate MD5 checksum of local files and compared to remote

    Results:
        (df, files, dirs, remotes):

        df: pandas.DataFrame containing:
            'l_mtime', 'l_size', 'l_type', 'r_mtime', 'r_size', 'r_type', 'eq', 'name'
        files: set of local and remote paths that are files
        dirs: set of local and remote paths that are directories
        remotes: set of remote File and Directory objects

    """
    path_data = []
    columns = [
        'l_mtime', 'l_size', 'l_type',
        'r_mtime', 'r_size', 'r_type',
        'eq', 'name', 'id']
    data_init = {k: '-' for k in columns}
    files = SortedSet(key=_name_key)
    dirs = SortedSet(key=_name_key)
    remotes = SortedSet(key=_name_key)

    for path in paths:

        data = copy.deepcopy(data_init)
        data['name'] = os.path.relpath(path, os.getcwd())
        l_checksum = None

        # locals
        if os.path.exists(path):
            data['l_mtime'] = time.strftime("%b %Y %d %H:%M:%S", time.localtime(os.path.getmtime(path)))
            data['l_size'] = _humanize(os.path.getsize(path))
            if os.path.isfile(path):
                data['l_type'] = 'file'
                if checksum:
                    with open(path, 'rb') as f:
                        l_checksum = hashlib.md5(f.read()).hexdigest()
                files.add(path)
            elif os.path.isdir(path):
                data['l_type'] = 'dir'
                dirs.add(path)

        # remotes
        obj = proj.get_by_local_path(path)
        if obj is not None:
            data['r_size'] = _humanize(obj.size)
            if isinstance(obj, File):
                if obj.mtime:
                    data['r_mtime'] = obj.mtime.strftime("%b %Y %d %H:%M:%S")
                data['r_type'] = 'file'
                if checksum and l_checksum is not None:
                    data['eq'] = (obj.checksum == l_checksum)
                files.add(path)
                remotes.add(obj)
            elif isinstance(obj, Directory):
                if obj.mtime:
                    data['r_mtime'] = obj.time.strftime("%b %Y %d %H:%M:%S")
                data['r_type'] = 'dir'
                dirs.add(path)
                if not files_only:
                    remotes.add(obj)
            data['id'] = obj.id

        if not files_only or ('file' in [data['l_type'], data['r_type']]):
            path_data.append(data)

    return pandas.DataFrame.from_records(path_data, columns=columns) \
        .sort_values(by='name'), files, dirs, remotes


def _humanize(file_size_bytes):
    abbrev = [("B", 0), ("K", 10), ("M", 20), ("G", 30), ("T", 40)]
    for key, val in abbrev:
        _size = (file_size_bytes >> val)
        if _size < 1000 or key == "T":
            return str(_size) + key


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
    parser.add_argument('--json', action="store_true", default=False, help='Print() JSON exactly')

    # ignore 'mc ls'
    args = parser.parse_args(argv[2:])

    local_abspaths = [os.path.abspath(p) for p in args.paths]

    proj = make_local_project()

    # act on local paths
    (df, files, dirs, remotes) = _ls_group(proj, local_abspaths,
                                           files_only=True, checksum=args.checksum, json=args.json)

    # print() warnings for type mismatches
    for file in files:
        if file in dirs and os.path.isfile(file):
            print("warning!", file, "is a local file and remote directory!")
        if file in dirs and os.path.isdir(file):
            print("warning!", file, "is a local directory and remote file!")

    if args.json:
        for r in remotes:
            print(r.input_data)
    else:
        if df.shape[0]:
            print(df.to_string(index=False))
            print("")

    for d in dirs:

        _locals = []
        if os.path.exists(d):
            _locals = [os.path.join(d, f) for f in os.listdir(d)]

        if os.path.abspath(d) == proj.local_path:
            remote_dir = proj.get_top_directory()
        else:
            remote_dir = proj.get_by_local_path(d)

        _remotes = []
        if remote_dir is not None:
            _remotes = [os.path.join(d, child.name) for child in remote_dir.get_children()]

        _local_abspaths = SortedSet(_locals + _remotes)

        (df, files, dirs, remotes) = _ls_group(
            proj, _local_abspaths,
            files_only=False, checksum=args.checksum, json=args.json
        )

        if args.json:
            for r in remotes:
                print(r.input_data)
        else:
            if df.shape[0]:
                print(os.path.relpath(d, os.getcwd()) + ":")
                # print(df.to_string(index=False)
                print(tabulate(df, showindex=False, headers=df.columns, tablefmt="plain"))
                print("")

    return


def _name_key(obj):
    try:
        return obj.name
    except Exception:
        return ""

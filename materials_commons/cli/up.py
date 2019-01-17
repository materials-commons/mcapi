import sys
import os
import argparse
from .functions import make_local_project


def _local_to_remote_relpath(proj, local_path):
    """
    Arguments:
        proj: mcapi.Project, with proj.local_path indicating local project location
        local_path: path to file or directory in local tree

    Returns:
        remote_path: relative path from the 'top' directory
    """
    remote_relpath = os.path.relpath(local_path, proj.local_path)
    if remote_relpath == ".":
        remote_relpath = "/"
    return remote_relpath


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

    # ignore 'mc up'
    args = parser.parse_args(argv[2:])

    limit = args.limit[0]
    proj = make_local_project()

    local_abspaths = set([os.path.abspath(p) for p in args.paths])
    if not args.recursive:
        dirs = [p for p in local_abspaths if os.path.isdir(p)]
        for d in dirs:
            local_abspaths.remove(d)
            files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
            local_abspaths.update(files)

    if args.recursive and proj.local_path in local_abspaths:
        # treat upload of everything specially
        local_abspaths = set([os.path.join(proj.local_path, f) for f in os.listdir(proj.local_path) if f != ".mc"])

    for p in local_abspaths:
        if os.path.isfile(p):
            # print("uploading:", p)
            try:
                result = proj.add_file_by_local_path(p, verbose=True, limit=limit)
            except Exception as e:
                print("Could not upload:", p)
                print("Error:")
                print(e)

        elif os.path.isdir(p) and args.recursive:
            # print("uploading:", p)
            result, error = proj.add_directory_tree_by_local_path(p, verbose=True, limit=limit)
            if len(error):
                for file in error:
                    print("Could not upload:", file)
                    print("Error:")
                    print(error[file])

    return

import sys
import os
import argparse
from ..api import File, Directory
# TODO: we should not be using the RAW api interface!
from ..api import __api as raw_api
from .functions import make_local_project


def _obj_path_to_local_path(proj, obj_path):
    """
    Arguments:
        proj: mcapi.Project, with proj.local_path indicating local project location
        obj_path: Directory.path or File.path
            currently this begins with 'top', instead of being relative to 'top'

    Returns:
        local_path: absolute path to file or directory locally
    """
    return os.path.join(os.path.dirname(proj.local_path), obj_path)


def _check_download(proj_id, file_id, local_path, remote, force=False):
    if not os.path.exists(local_path) or force:
        dir = os.path.dirname(local_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return raw_api.file_download(proj_id, file_id, local_path, remote)
    else:
        print("Overwrite '" + os.path.relpath(local_path, os.getcwd()) + "'?")
        while True:
            ans = raw_input('y/n: ')
            if ans == 'y':
                return raw_api.file_download(proj_id, file_id, local_path, remote)
            elif ans == 'n':
                break
    return None


def _download(proj, dir, recursive=False, force=False):
    results = []
    children = dir.get_children()
    for child in children:

        if isinstance(child, File):
            # p = _obj_path_to_local_path(proj, os.path.join(child.parent().path, child.name))
            p = child.local_path()
            if not os.path.exists(os.path.dirname(p)):
                os.makedirs(os.path.dirname(p))
            result_path = _check_download(proj.id, child.id, p, proj.remote, force=force)
            if result_path is not None:
                print("downloaded:", os.path.relpath(result_path, os.getcwd()))
            results.append(result_path)

        elif isinstance(child, Directory) and recursive:
            _download(proj, child, recursive=recursive, force=force)

    return results


def down_subcommand(argv=sys.argv):
    """
    download files from Materials Commons

    mc down [-r] [<pathspec> ...]

    """
    parser = argparse.ArgumentParser(
        description='download files',
        prog='mc down')
    parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
    parser.add_argument('-r', '--recursive', action="store_true", default=False,
                        help='Download directory contents recursively')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help='Force overwrite of existing files')

    # ignore 'mc down'
    args = parser.parse_args(argv[2:])

    local_abspaths = [os.path.abspath(p) for p in args.paths]

    proj = make_local_project()

    for p in local_abspaths:

        if os.path.abspath(p) == proj.local_path:
            obj = proj.get_top_directory()
        else:
            obj = proj.get_by_local_path(p)

        if isinstance(obj, File):
            # (project_id, file_id, output_file_path, remote=use_remote())
            result_path = _check_download(proj.id, obj.id, p, proj.remote, force=args.force)
            if result_path is not None:
                print("downloaded:", os.path.relpath(result_path, os.getcwd()))

        elif isinstance(obj, Directory):
            _download(proj, obj, force=args.force, recursive=args.recursive)

    return

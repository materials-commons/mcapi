import argparse
import os
import sys
import time

import materials_commons.api as mcapi
from ..api import __api as mc_raw_api
import materials_commons.cli.functions as clifuncs
import materials_commons.cli.tree_functions as treefuncs
import materials_commons.cli.globus as cliglobus
from materials_commons.cli.treedb import LocalTree, RemoteTree



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
        return mc_raw_api.file_download(proj_id, file_id, local_path, remote)
    else:
        print("Overwrite '" + os.path.relpath(local_path, os.getcwd()) + "'?")
        while True:
            ans = input('y/n: ')
            if ans == 'y':
                return mc_raw_api.file_download(proj_id, file_id, local_path, remote)
            elif ans == 'n':
                break
    return None


def _download(proj, dir, dirpath=None, recursive=False, force=False):

    if dirpath is None:
        dirpath = dir.path
    results = []
    children = dir.get_children()
    for child in children:

        if isinstance(child, mcapi.File):
            # p = _obj_path_to_local_path(proj, os.path.join(child.get_parent().path, child.name))
            # p = child.local_path()
            p = os.path.join(dirpath, child.name)
            if not os.path.exists(os.path.dirname(p)):
                os.makedirs(os.path.dirname(p))
            result_path = _check_download(proj.id, child.id, p, proj.remote, force=force)
            if result_path is not None:
                print("downloaded:", os.path.relpath(result_path, os.getcwd()))
            results.append(result_path)

        elif isinstance(child, mcapi.Directory) and recursive:
            _download(proj, child, dirpath=os.path.join(dirpath, child.name), recursive=recursive, force=force)

    return results

def standard_download(proj, path, force=False, output=None, recursive=False, no_compare=False, localtree=None, remotetree=None):
    print("begin standard_download:", path)

    refpath = os.path.dirname(proj.local_path)
    local_abspath = os.path.join(refpath, path)
    printpath = os.path.relpath(local_abspath)

    if output is None:
        output = local_abspath

    checksum = True
    if no_compare:
        checksum = False

    files_data, dirs_data, child_data, non_existing = treefuncs.treecompare(proj, [path], checksum=checksum, localtree=localtree, remotetree=remotetree)

    # if remote file:
    if path in files_data and files_data[path]['r_type'] == 'file':
        print("is a remote file")

        if files_data[path]['l_type'] == 'directory':
            print(printpath + ": is local directory and remote file")
            return False
        elif 'eq' in files_data[path] and files_data[path]['eq']:
            print(printpath + ": local is equivalent to remote (skipping)")
            return True
        else:
            result_path =  _check_download(proj.id, files_data[path]['id'], output, remote=proj.remote, force=force)
            if result_path:
                print("downloaded:", os.path.relpath(result_path, os.getcwd()))
                return True
            else:
                return False

    # if directory:
    elif path in dirs_data and dirs_data[path]['r_type'] == 'directory':
        print("is a remote directory")

        if not recursive:
            print(printpath + ": is a directory")
            return False

        if dirs_data[path]['l_type'] == 'file':
            print(printpath + ": is local file and remote directory")
            return False

        print("begin recursive downloading:\n", child_data[path])
        success = True
        for childpath, record in child_data[path].items():
            print(childpath, record)
            childoutput = os.path.join(output, os.path.basename(childpath))
            print(output)
            success &= standard_download(proj, childpath, force=force, output=childoutput, recursive=recursive, no_compare=no_compare, localtree=localtree, remotetree=remotetree)
        return success

    else:
        print(printpath + ": does not exist on remote")
        return False

def print_file(proj, path):
    refpath = proj.local_path
    local_abspath = os.path.join(refpath, path)
    printpath = os.path.relpath(local_abspath)
    obj = clifuncs.get_by_path(proj, path)
    if not obj:
        print(printpath + ": No such file or directory on remote")
        return False
    if isinstance(obj, mcapi.Directory):
        print(printpath + ": Is a directory on remote")
        return False
    if not isinstance(obj, mcapi.File):
        print(printpath + ": Not a file on remote")
        return False

    s = clifuncs.download_file_as_string(proj.id, obj.id, proj.remote)
    print(printpath + ":")
    print(s)

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
    parser.add_argument('-p', '--print', action="store_true", default=False,
                        help='Print file, do not write')
    parser.add_argument('-o', '--output', nargs=1, default=None, help='Download file name')
    parser.add_argument('-g', '--globus', action="store_true", default=False,
                        help='Use globus to upload files.')
    parser.add_argument('--label', nargs=1, type=str,
                        help='Globus transfer label to make finding tasks simpler.')
    parser.add_argument('--no-compare', action="store_true", default=False,
                        help='Download remote without checking if local is equivalent.')


    # ignore 'mc down'
    args = parser.parse_args(argv[2:])

    proj = clifuncs.make_local_project()

    refpath = os.path.dirname(proj.local_path)
    paths = [os.path.relpath(os.path.abspath(p), refpath) for p in args.paths]

    # validate
    if args.print and len(args.paths) != 1:
        print("--print option acts on 1 file, received", len(args.paths))
        exit(1)
    if args.output and len(args.paths) != 1:
        print("--output option acts on 1 file or directory, received", len(args.paths))
        exit(1)

    if args.globus:
        label = proj.name
        if args.label:
            label = args.label[0]

        cliglobus.globus_download_v0(proj, paths, recursive=args.recursive, label=label)

    elif args.print:

        print_file(proj, path)

    else:


        localtree = None
        if not args.no_compare:
            localtree = LocalTree(proj)

        remotetree = None
        pconfig = clifuncs.read_project_config()
        if pconfig.remote_updatetime:
            remotetree = RemoteTree(proj, pconfig.remote_updatetime)

        output=None
        if args.output:
            output = os.path.abspath(args.output[0])

        for path in paths:
            standard_download(proj, path, output=output, recursive=args.recursive, no_compare=args.no_compare, localtree=localtree, remotetree=remotetree)

    return

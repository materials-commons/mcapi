import argparse
import difflib
import os
import sys

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs


def diff_subcommand(argv=sys.argv):
    """
    Compare a file

    mc diff <pathspec>

    """
    parser = argparse.ArgumentParser(
        description='Compare a file',
        prog='mc diff')
    parser.add_argument('path', nargs=1, help='File to diff')
    parser.add_argument('--context', action="store_true", default=False, help='Print using \'context diff\' method')

    # ignore 'mc ls'
    args = parser.parse_args(argv[2:])

    proj = clifuncs.make_local_project()
    pconfig = clifuncs.read_project_config()

    # convert cli input to materials commons path convention: <projectname>/path/to/file_or_dir
    refpath = os.path.dirname(proj.local_path)

    for p in args.path:
        local_abspath = os.path.abspath(p)
        path = os.path.relpath(local_abspath, refpath)

        obj = clifuncs.get_by_path(proj, path)

        if not obj:
            print(p + ": No such file or directory on remote")
            exit(1)
        if isinstance(obj, mcapi.Directory):
            print(p + ": Is a directory on remote")
            exit(1)
        if not isinstance(obj, mcapi.File):
            print(p + ": Not a file on remote")
            exit(1)

        if not os.path.exists(local_abspath):
            print(local_abspath + ": No such file or directory locally")
            exit(1)
        if os.path.isdir(local_abspath):
            print(p + ": Is a directory locally")
            exit(1)
        if not os.path.isfile(local_abspath):
            print(p + ": Not a file locally")
            exit(1)

        remotefile = clifuncs.download_file_as_string(proj.id, obj.id, proj.remote)
        localfile = open(local_abspath, 'r').read()

        if args.context:
            method = difflib.context_diff
        else:
            method = difflib.unified_diff

        result = method(remotefile.splitlines(keepends=True), localfile.splitlines(keepends=True), fromfile="remote", tofile="local")
        sys.stdout.writelines(result)

    return

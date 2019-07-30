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
from materials_commons.cli.treedb import LocalTree, RemoteTree

def print_fetch_status(pconfig):
    if pconfig.remote_updatetime:
        print("Fetch lock set at:", clifuncs.format_time(pconfig.remote_updatetime))
        print("Project data will at least reflect remote changes that happened before this time.")
        print("**Changes that happen after this time may not be reflected in CLI output**.")
        print("Do `mc fetch --unlock` to turn off the fetch lock.")
    else:
        print("Fetch lock off")
        print("Project data will always be fetched from remote.")

def fetch_subcommand(argv=sys.argv):
    """
    Fetch remote data

    mc fetch [--recursive] [<path>...]
    mc fetch --lock
    mc fetch --unlock
    mc fetch --status

    """

    desc = "By default, remote data is fetched for every request. To be more efficient, some remote data can be fetched and cached using `mc fetch --lock`. When 'locked', remote data is recovered from a local cache if it has been updated since the lock was put in place. Any data fetched before the lock was put in place is still updated as necessary. To the extent possible, the cache will be updated when the remote is modified via the `mc` command line. While the lock is in place, use `mc fetch <path>` to force the update of data for particular files or directories. To reset the lock time, use `mc fetch --lock` again. To stop caching, use `mc fetch --unlock`."

    parser = argparse.ArgumentParser(
        description=desc,
        prog='mc fetch')
    parser.add_argument('paths', nargs='*', default=[], help='Files or directories')
    parser.add_argument('-r', '--recursive', action="store_true", default=False, help='Fetch data recursively for specified paths.')
    parser.add_argument('--verbose', action="store_true", default=False, help='Print verbosely.')
    parser.add_argument('--no-children', action="store_true", default=False, help='Do not update data for children of directories.')
    parser.add_argument('--lock', action="store_true", default=False, help='Only fetch data to replace records older than now.')
    parser.add_argument('--unlock', action="store_true", default=False, help='Always fetch data.')
    parser.add_argument('--status', action="store_true", default=False, help='Display fetch lock status.')

    # ignore 'mc ls'
    args = parser.parse_args(argv[2:])

    if not clifuncs.project_exists():
        print("No current project.")

    if args.lock:
        pconfig = clifuncs.read_project_config()
        pconfig.remote_updatetime = time.time()
        pconfig.save()
        print_fetch_status(pconfig)

    elif args.unlock:
        pconfig = clifuncs.read_project_config()
        pconfig.remote_updatetime = None
        pconfig.save()
        print_fetch_status(pconfig)

    elif args.status:
        pconfig = clifuncs.read_project_config()
        print_fetch_status(pconfig)

    else:
        if not args.paths:
            print("Nothing to fetch")
            return

        proj = clifuncs.make_local_project()
        remotetree = RemoteTree(proj, time.time())
        pconfig = clifuncs.read_project_config()
        refpath = os.path.dirname(proj.local_path)

        get_children = True
        if args.no_children:
            get_children = False

        remotetree.connect()
        for p in args.paths:
            print("fetch:", p)
            remotetree.update(
                os.path.relpath(os.path.abspath(p), refpath),
                get_children=get_children,
                recurs=args.recursive,
                verbose=args.verbose)
        remotetree.close()

    return

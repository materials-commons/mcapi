import os
import sys
import argparse
import contextlib
import json
import re

import materials_commons2_cli.functions as clifuncs
from materials_commons2_cli.exceptions import MCCLIException

@contextlib.contextmanager
def output_method(file=None, force=False):
    if file is None:
        out = sys.stdout
    elif os.path.exists(file) and not force:
        msg = "The file '" + file + "' exists and --force option not given."
        raise MCCLIException(msg)
    else:
        out = open(file, 'w')

    try:
        yield out
    finally:
        if out is not sys.stdout:
            out.close()

class ListObjects(object):
    """
    Base class to create an 'mc X' CLI command for listing objects of type X.

    Expects derived class members:
        get_all_from_experiment(self, expt), if expt_member
        get_all_from_dataset(self, dataset), if dataset_member
        get_all_from_project(self, proj), if proj_member
        get_all(self), if non_proj_member
        list_data(self, obj)
        print_details(self, obj, out=sys.stdout)

    Optional derived class members:
        create(self, args), should be implemented if type is createable
        delete(self, objects, dry_run, out=sys.stdout), should be implemented if type is createable
        add_create_options(self, parser), called if exists in derived class
        add_custom_options(self, parser), called if exists in derived class

    Custom derived class actions should have the form:
        <name>(self, args, out=sys.stdout)

    Custom derived class "selection" actions should have the form:
        <name>(self, objects, args, out=sys.stdout)

    See ProcSubcommand for an example.

    """

    def __init__(self, cmdname, typename, typename_plural, desc=None, requires_project=True,
                 non_proj_member=False, proj_member=True, expt_member=True, dataset_member=False,
                 remote_help='Select remote',
                 list_columns=None, headers=None,
                 deletable=False, dry_runable=False, has_owner=True, creatable=False,
                 custom_actions=[], custom_selection_actions=[], request_confirmation_actions={}):
        """

        Arguments:
            cmdname: List[str]
                Names to use for 'mc X Y ...', for instance: ["casm", "prim"] for "mc casm prim"
            typename: str
                With capitalization, for instance: "Process"
            typename_plural: str
                With capitalization, for instance: "Processes"
            desc: str
                Used for help command description
            requires_project: bool
                If True and not in current project, raise MCCLIException
            non_proj_member: bool
                Enable get_all_from_remote. If non_proj_member and proj_member, enable --proj
                option to restrict queries to the current project.
            proj_member: bool
                Enable get_all_from_project. Restrict queries to current project by default
            expt_member: bool
                Enable get_all_from_experiment. Include --expt option to restrict queries to
                current experiment
            dataset_member: bool
                Enable get_all_from_dataset. Includes --dataset option to restrict queries to
                specified dataset
            list_columns: List[str]
                List of column names
            headers: List[str]
                List of column header names, use list_columns if None
            deletable: bool
                If true, enable --delete
            dry_runable: bool
                If true, enable --dry-run
            has_owner: bool
                If true, enable --owner
            creatable: bool
                If true, object can be created via derived class 'create' function
            custom_actions: List of str
                Custom action names which are called via:
                    `<name>(self, args, outout=sys.stdout)`
            custom_selection_actions: List of str
                Custom action names which are called via:
                    `<name>(self, objects, args, outout=sys.stdout)`
            request_confirmation_actions: Dict of name:msg
                Dictionary of names of custom_selection_actions which require prompting the user
                for confirmation before executing. The value is the message shown at the prompt.
                Delete is always confirmed and is not included here.
        """
        if list_columns is None:
            list_columns = []
        self.cmdname = cmdname
        self.typename = typename
        self.typename_plural = typename_plural
        self.desc = desc
        self.requires_project = requires_project
        self.non_proj_member = non_proj_member
        self.proj_member = proj_member
        self.expt_member = expt_member
        self.dataset_member = dataset_member
        self.remote_help = remote_help
        self.list_columns = list_columns
        if headers is None:
            headers = list_columns
        self.headers = headers
        self.deletable = deletable
        self.has_owner = has_owner
        self.creatable = creatable
        self.dry_runable = dry_runable
        self.custom_actions = custom_actions
        self.custom_selection_actions = custom_selection_actions
        self.request_confirmation_actions = request_confirmation_actions

    def parse_args(self, argv):
        """
        Parse CLI arguments, returning result of argparse.ArgumentParser.parse_args(argv)
        """

        expr_help = 'select ' + self.typename_plural + ' that match the given regex (default matches name)'
        uuid_help = 'match uuid instead of name'
        owner_help = 'match owner instead of name'
        details_help = 'print detailed information'
        regxsearch_help = 'use regular expression search instead of match'
        sort_by_help = 'columns to sort by'
        json_help = 'print JSON data'
        proj_help = 'restrict to ' + self.typename_plural + ' in the current project'
        expt_help = 'restrict to ' + self.typename_plural + ' in the current experiment'
        dataset_help = 'restrict to ' + self.typename_plural + ' in the specified (by uuid) dataset'
        output_help = 'output to file'
        force_help = 'force overwrite of existing output file'
        create_help = 'create a ' + self.typename
        delete_help = 'delete a ' + self.typename + ', specified by uuid'
        dry_run_help = 'dry run deletion'

        if self.desc is None:
            if self.creatable:
                self.desc = 'List and create ' + self.typename_plural
            else:
                self.desc = 'List ' + self.typename_plural.lower()

        cmd = "mc "
        for n in self.cmdname:
            cmd += n + " "

        parser = argparse.ArgumentParser(
            description=self.desc,
            prog=cmd)
        parser.add_argument('expr', nargs='*', default=None, help=expr_help)
        parser.add_argument('--uuid', action="store_true", default=False, help=uuid_help)
        if self.has_owner:
            parser.add_argument('--owner', action="store_true", default=False, help=owner_help)
        parser.add_argument('-d', '--details', action="store_true", default=False, help=details_help)
        parser.add_argument('--regxsearch', action="store_true", default=False, help=regxsearch_help)
        parser.add_argument('--sort-by', nargs='*', default=['name'], help=sort_by_help)
        parser.add_argument('--json', action="store_true", default=False, help=json_help)
        parser.add_argument('-o', '--output', nargs=1, default=None, help=output_help)
        parser.add_argument('-f', '--force', action="store_true", default=False, help=force_help)
        if self.non_proj_member:
            clifuncs.add_remote_option(parser, self.remote_help)
        if self.non_proj_member and self.proj_member:
            parser.add_argument('--proj', action="store_true", default=False, help=proj_help)
        if self.expt_member:
            parser.add_argument('--expt', action="store_true", default=False, help=expt_help)
        if self.dataset_member:
            parser.add_argument('--dataset', nargs=1, default=None, metavar='DATASET_ID', help=dataset_help)
        if self.creatable:
            parser.add_argument('--create', action="store_true", default=False, help=create_help)
        if self.deletable:
            parser.add_argument('--delete', action="store_true", default=False, help=delete_help)
        if self.dry_runable:
            parser.add_argument('-n', '--dry-run', action="store_true", default=False, help=dry_run_help)

        if hasattr(self, 'add_create_options'):
            self.add_create_options(parser)
        if hasattr(self, 'add_custom_options'):
            self.add_custom_options(parser)

        # ignore 'mc proc'
        args = parser.parse_args(argv[2:])
        if not self.dry_runable:
            args.dry_run = False
        return args

    def __call__(self, argv):
        """
        Execute Materials Commons CLI command.

        mc proc [--proj] [--expt] [--dataset] [--details | --json] [--uuid] [<name> ...]

        """
        args = self.parse_args(argv)

        output = None
        if args.output:
            output = args.output[0]

        # check for --create and other custom actions
        for name in ['create'] + self.custom_actions:
            if hasattr(args, name) and getattr(args, name):
                with output_method(output, args.force) as out:
                    # interfaces 'mc casm monte --create ...'
                    getattr(self, name)(args, out=out)
                return

        # otherwise, perform a 'selection' action
        with output_method(output, args.force) as out:
            objects = self.get_all_objects(args, out)
            if not len(objects):
                return

            # if --delete
            if self.deletable and args.delete:

                if not args.force:
                    self.output(objects, args, out)
                    if args.dry_run:
                        out.write("** Dry run **\n")
                    msg = "Are you sure you want to permanently delete these? ('Yes'/'No'): "
                    input_str = input(msg)
                    if input_str != 'Yes':
                        out.write("Aborting\n")
                        return
                    else:
                        self.delete(objects, args, dry_run=args.dry_run, out=out)
                else:
                    if args.dry_run:
                        out.write("** Dry run **\n")
                    self.output(objects, args, out)
                    out.write("Permanently deleting with --force...\n")
                    self.delete(objects, args, dry_run=args.dry_run, out=out)
                return

            else:

                # default action is to output a list of objects
                name = 'output'

                # check for if a custom selection actions has been requested, via --<name>
                for _name in self.custom_selection_actions:
                    if hasattr(args, _name) and getattr(args, _name):
                        name = _name
                        break

                # check if user confirmation is required
                if name in self.request_confirmation_actions and not args.force:
                    self.output(objects, args, out)
                    if clifuncs.request_confirmation(self.request_confirmation_actions[name]):
                        getattr(self, name)(objects, args, out)
                    else:
                        out.write("Aborting\n")
                        return
                else:
                    getattr(self, name)(objects, args, out)

                return

    def get_remote(self, args):
        default_client = None
        if clifuncs.project_exists():
            default_client = clifuncs.make_local_project_client()
        return clifuncs.optional_remote(args, default_client=default_client)

    def get_all_objects(self, args, out=sys.stdout):

        if self.requires_project and not clifuncs.project_exists():
            print("Not a Materials Commons project (or any of the parent directories)")
            exit(1)

        if hasattr(args, 'expt') and args.expt:
            proj = clifuncs.make_local_project()
            expt = clifuncs.make_local_expt(proj)
            data = self.get_all_from_experiment(expt)
            if not len(data):
                out.write("No " + self.typename_plural + " found in experiment\n")
                return []
        # elif hasattr(args, 'dataset') and args.dataset:
        #     # if in project
        #     if clifuncs.project_exists():
        #         proj = clifuncs.make_local_project()
        #         dataset = clifuncs.get_dataset(proj.id, args.dataset[0], remote=proj.remote)
        #         data = self.get_all_from_dataset(dataset)
        #     else:
        #         remote = self.get_remote(args)
        #         dataset = clifuncs.get_published_dataset(args.dataset[0], remote=remote)
        #         data = self.get_all_from_dataset(dataset)
        #     if not len(data):
        #         out.write("No " + self.typename_plural + " found in dataset\n")
        #         return []
        elif hasattr(args, 'proj') and args.proj:
            proj = clifuncs.make_local_project()
            data = self.get_all_from_project(proj)
            if not len(data):
                out.write("No " + self.typename_plural + " found in project\n")
                return []
        elif self.non_proj_member:
            remote = self.get_remote(args)
            data = self.get_all_from_remote(remote=remote)
            if not len(data):
                out.write("No " + self.typename_plural + " found at " + remote.config.mcurl + "\n")
                return []
        else:
            proj = clifuncs.make_local_project()
            data = self.get_all_from_project(proj)
            if not len(data):
                out.write("No " + self.typename_plural + " found in project\n")
                return []

        def _any_match(obj, attrname, remethod):
            value = str(clifuncs.getit(obj, attrname))
            for n in args.expr:
                if remethod(n, value):
                    return True
            return False

        if args.expr:

            if args.regxsearch:
                remethod = re.search
            else:
                remethod = re.match

            if args.uuid:
                objects = [d for d in data if _any_match(d, 'uuid', remethod)]
            elif self.has_owner and args.owner:
                objects = [d for d in data if _any_match(d, 'owner_id', remethod)]
            else:
                objects = [d for d in data if _any_match(d, 'name', remethod)]
        else:
            objects = data

        if not len(objects):
            out.write("No " + self.typename_plural + " found matching specified criteria\n")

        return objects

    def output(self, objects, args, out=sys.stdout):
        if not len(objects):
            out.write("No " + self.typename_plural + " found matching specified criteria\n")
            return
        if args.details:
            if not hasattr(self, 'print_details'):
                out.write("--details not currently possible for this type of object\n")
                return
            for obj in objects:
                self.print_details(obj, out=out)
                out.write("\n")
        elif args.json:
            for obj in objects:
                if hasattr(obj, '_data'):
                    out.write(json.dumps(obj._data, indent=2))
                    out.write("\n")
                elif isinstance(obj, dict):
                    out.write(json.dumps(obj, indent=2))
                    out.write("\n")
                else:
                    out.write("--json not currently possible for this type of object\n")
                    break
        else:
            data = []
            for obj in objects:
                data.append(self.list_data(obj))

            for col in reversed(args.sort_by):
                data = sorted(data, key=lambda k: k[col])

            columns = self.list_columns
            headers = self.headers

            clifuncs.print_table(data, columns=columns, headers=headers, out=out)
            out.write("\n")
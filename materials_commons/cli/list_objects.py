import os
import sys
import argparse
import contextlib
import json
import re
from tabulate import tabulate
from pandas import DataFrame
from .functions import make_local_project, make_local_expt, _proj_path


@contextlib.contextmanager
def output_method(file=None, force=False):
    if file is None:
        out = sys.stdout
    elif os.path.exists(file) and not force:
        msg = "The file '" + file + "' exists and --force option not given."
        raise Exception(msg)
    else:
        out = open(file, 'w')

    try:
        yield out
    finally:
        if out is not sys.stdout:
            out.close()


class ListObjects(object):
    """
    Base class to create an 'mc X' command for listing objects of type X.

    Expects derived class members:
        get_all_from_experiment(self, expt), if expt_member
        get_all_from_project(self, proj), if proj_member
        get_all(self), if non_proj_member
        list_data(self, obj)

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
                 non_proj_member=False, proj_member=True, expt_member=True, list_columns=None, headers=None,
                 deletable=False, dry_runable=False, has_owner=True, creatable=False,
                 custom_actions=[], custom_selection_actions=[]):
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
                If True and not in current project, raise Exception
            non_proj_member: bool
                If non_proj_member and proj_member, enable --proj option to restrict queries to the
                current project.
            proj_member: bool
                Restrict queries to current project by default
            expt_member: bool
                Include --expt option to restrict queries to current experiment
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

    def __call__(self, argv):
        """
        List Materials Commons Objects.

        mc proc [--proj] [--expt] [--details | --json] [--id] [<name> ...]

        """

        expr_help = 'select ' + self.typename_plural + ' that match the given regex (default uses name)'
        id_help = 'match by id instead of name'
        owner_help = 'match by owner instead of name'
        details_help = 'print detailed information'
        sort_by_help = 'columns to sort by'
        json_help = 'print JSON data'
        proj_help = 'restrict to ' + self.typename_plural + ' in the current project'
        expt_help = 'restrict to ' + self.typename_plural + ' in the current experiment'
        output_help = 'output to file'
        force_help = 'force overwrite of existing output file'
        create_help = 'create a ' + self.typename
        delete_help = 'delete a ' + self.typename + ', specified by id'
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
        parser.add_argument('--id', action="store_true", default=False, help=id_help)
        if self.has_owner:
            parser.add_argument('--owner', action="store_true", default=False, help=owner_help)
        parser.add_argument('-d', '--details', action="store_true", default=False, help=details_help)
        parser.add_argument('--sort-by', nargs='*', default=['name'], help=sort_by_help)
        parser.add_argument('--json', action="store_true", default=False, help=json_help)
        parser.add_argument('-o', '--output', nargs=1, default=None, help=output_help)
        parser.add_argument('-f', '--force', action="store_true", default=False, help=force_help)
        if self.non_proj_member and self.proj_member:
            parser.add_argument('--proj', action="store_true", default=False, help=proj_help)
        if self.expt_member:
            parser.add_argument('--expt', action="store_true", default=False, help=expt_help)
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

        output = None
        if args.output:
            output = args.output[0]

        # check for --create, or other custom primiary option command --<name>
        for name in ['create'] + self.custom_actions:
            if hasattr(args, name) and getattr(args, name) == True:
                with output_method(output, args.force) as out:
                    # interfaces 'mc casm monte --create ...'
                    getattr(self, name)(args, out=out)
                return

        # otherwise, perform a 'selection' action
        with output_method(output, args.force) as out:
            objects = self.get_all_objects(args)
            if not len(objects):
                out.write("No " + self.typename_plural + " found matching specified criteria\n")
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
                        self.delete(objects, dry_run=args.dry_run, out=out)
                else:
                    if args.dry_run:
                        out.write("** Dry run **\n")
                    self.output(objects, args, out)
                    out.write("Permanently deleting with --force...\n")
                    self.delete(objects, dry_run=args.dry_run, out=out)
                return

            else:

                # default action is to output a list of objects
                name = 'output'

                # check for if a custom selection actions has been requested, via --<name>
                for _name in self.custom_selection_actions:
                    if hasattr(args, _name) and getattr(args, _name) == True:
                        name = _name
                        break
                getattr(self, name)(objects, args, out)
                return

    def get_all_objects(self, args):

        if self.requires_project and _proj_path() is None:
            raise Exception("Not in any Materials Commons project directory")

        if hasattr(args, 'expt') and args.expt:
            proj = make_local_project()
            expt = make_local_expt(proj)
            data = self.get_all_from_experiment(expt)
        elif hasattr(args, 'proj') and args.proj:
            proj = make_local_project()
            data = self.get_all_from_project(proj)
        elif self.non_proj_member:
            data = self.get_all()
        else:
            proj = make_local_project()
            data = self.get_all_from_project(proj)

        def _any_match(obj, attrname):
            if isinstance(obj, dict):
                value = obj[attrname]
            else:
                value = getattr(obj, attrname)
            for n in args.expr:
                if re.match(n, value):
                    return True
            return False

        if args.expr:
            if args.id:
                objects = [d for d in data if _any_match(d, 'id')]
            elif self.has_owner and args.owner:
                objects = [d for d in data if _any_match(d, 'owner')]
            else:
                objects = [d for d in data if _any_match(d, 'name')]
        else:
            objects = data

        return objects

    def output(self, objects, args, out=sys.stdout):
        if not len(objects):
            out.write("No " + self.typename_plural + " found matching specified criteria\n")
            return
        if args.details:
            for obj in objects:
                if isinstance(obj, dict):
                    out.write("--details not currently possible for this type of object\n")
                    break
                else:
                    obj.pretty_print(shift=0, indent=2, out=out)
                    out.write("\n")
        elif args.json:
            for obj in objects:
                if hasattr(obj, 'input_data'):
                    out.write(json.dumps(obj.input_data, indent=2))
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
                df = DataFrame.from_records(data, columns=self.list_columns)
                df.sort_values(inplace=True, by=args.sort_by)
            out.write(tabulate(df, showindex=False, headers=self.headers))
            out.write("\n")

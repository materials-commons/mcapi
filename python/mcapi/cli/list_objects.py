import os
import sys
import argparse
import contextlib
import json
import re
from tabulate import tabulate
from pandas import DataFrame
from mcapi.cli.functions import make_local_project, make_local_expt, _proj_path


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
        get_all_from_experiment(self, expt)
        get_all_from_project(self, proj)
        list_data(self, obj)
        
    See ProcSubcommand for an example.
    
    """
    
    def __init__(self, cmdname, typename, typename_plural, requires_project=True,
                 proj_member=True, expt_member=True, list_columns=[], headers=None,
                 deletable=False, has_owner=True):
        """
        
        Arguments:
            cmdname: str
                Name to use for 'mc X', for instance: "proc" for "mc proc"
            typename: str
                With capitalization, for instance: "Process"
            typename_plural: str
                With capitalization, for instance: "Processes"
            requires_project: bool
                If True and not in current project, raise Exception
            proj_member: bool
                Restrict queries to current project
            expt_member: bool
                Include --expt option to restrict queries to current experiment
            list_columns: List[str]
                List of column names
            headers: List[str]
                List of column header names, use list_columns if None
            deletable: bool
                If true, enable --delete and --dry-run
            has_owner: bool
                If true, enable --owner
        
        """
        self.cmdname = cmdname
        self.typename = typename
        self.typename_plural = typename_plural
        self.requires_project = requires_project
        self.proj_member = proj_member
        self.expt_member = expt_member
        self.list_columns = list_columns
        if headers is None:
            headers = list_columns
        self.headers = headers
        self.deletable = deletable
        self.has_owner = has_owner
    
    def __call__(self, argv):
        """
        List Materials Commons Objects.
        
        mc proc [--expt] [--details | --json] [--id] [<name> ...]
        
        """
        
        expr_help = 'select ' + self.typename_plural.lower() + ' that match the given regex (default uses name)'
        id_help = 'match by ' + self.typename.lower() + ' id instead of name'
        owner_help = 'match by ' + self.typename.lower() + ' owner instead of name'
        details_help = 'print detailed information'
        json_help = 'print JSON data'
        expt_help = 'restrict to ' + self.typename_plural.lower() + ' in the current experiment, rather than entire project'
        output_help = 'output to file'
        force_help = 'force overwrite of existing output file'
        delete_help = 'delete a ' + self.typename.lower() + ', specified by id'
        dry_run_help = 'dry run deletion'
        
        parser = argparse.ArgumentParser(
            description='List ' + self.typename_plural.lower(),
            prog='mc ' + self.cmdname)
        parser.add_argument('expr', nargs='*', default=None, help=expr_help)
        parser.add_argument('--id', action="store_true", default=False, help=id_help)
        if self.has_owner:
            parser.add_argument('--owner', action="store_true", default=False, help=owner_help)
        parser.add_argument('-d', '--details', action="store_true", default=False, help=details_help)
        parser.add_argument('--json', action="store_true", default=False, help=json_help)
        parser.add_argument('-o', '--output', nargs=1, default=None, help=output_help)
        parser.add_argument('-f', '--force', action="store_true", default=False, help=force_help)
        if self.expt_member:
            parser.add_argument('--expt', action="store_true", default=False, help=expt_help)
        if self.deletable:
            parser.add_argument('--delete', action="store_true", default=False, help=delete_help)
            parser.add_argument('-n', '--dry-run', action="store_true", default=False, help=dry_run_help)
        
        # ignore 'mc proc'
        args = parser.parse_args(argv[2:])
        
        output = None
        if args.output:
            output = args.output[0]
        
        with output_method(output, args.force) as out:
            if self.deletable and args.delete:
                objects = self.get_all_objects(args)
                self.delete(objects, args.dry_run, out=out)
            else:
                objects = self.get_all_objects(args)
                self.output(out, args, objects)
        return


    def get_all_objects(self, args):
        
        if self.requires_project and _proj_path() is None:
            raise Exception("Not in any Materials Commons project directory")
        
        if not self.proj_member:
            data = self.get_all()
        else:
            proj = make_local_project()
                
            if self.expt_member and args.expt:
                expt = make_local_expt(proj)
                data = self.get_all_from_experiment(expt)
            else:
                data = self.get_all_from_project(proj)
        
        def _any_match(value):
            for n in args.expr:
                if re.match(n, value):
                    return True
            return False
        
        if args.expr:
            if args.id:
                objects = [d for d in data if _any_match(d.id)]
            elif self.has_owner and args.owner:
                objects = [d for d in data if _any_match(d.owner)]
            else:
                objects = [d for d in data if _any_match(d.name)]
        else:
            objects = data
        
        return objects
    
    
    def output(self, out, args, objects):
        if not len(objects):
            out.write("No " + self.typename_plural.lower() + " found matching specified criteria\n")
            return
        if args.details:
            for obj in objects:
                obj.pretty_print(shift=0, indent=2, out=out)
                out.write("\n")
        elif args.json:
            out.write(json.dumps([obj.input_data for obj in objects], indent=2))
            out.write("\n")
        else:
            data = []
            for obj in objects:
                data.append(self.list_data(obj))
                df = DataFrame.from_records(data, columns=self.list_columns)
            out.write(tabulate(df, showindex=False, headers=self.headers))
            out.write("\n")
            


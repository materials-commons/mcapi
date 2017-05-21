import os
import sys
import argparse
import contextlib
import json
import re
from tabulate import tabulate
from pandas import DataFrame
from mcapi.cli.functions import make_local_project, make_local_expt


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
    
    def __init__(self, cmdname, typename, typename_plural, expt_member=True,
                 list_columns=[]):
        """
        
        Arguments:
            cmdname: str
                Name to use for 'mc X', for instance: "proc" for "mc proc"
            typename: str
                With capitalization, for instance: "Process"
            typename_plural: str
                With capitalization, for instance: "Processes"
            expt_member: bool
                Include --expt option to restrict queries to current experiment
            list_columns: List[str]
                List of column names
        
        """
        self.cmdname = cmdname
        self.typename = typename
        self.typename_plural = typename_plural
        self.expt_member = expt_member
        self.list_columns = list_columns
    
    def __call__(self, argv):
        """
        List Materials Commons Objects.
        
        mc proc [--expt] [--details | --json] [--id] [<name> ...]
        
        """
        
        expr_help = self.typename + 'Select objects whose names (or id if --id given) match the given regex'
        id_help = 'Input ' + self.typename.lower() + ' id instead of name'
        details_help = 'Print detailed information'
        json_help = 'Print JSON data'
        expt_help = 'Restrict to ' + self.typename_plural.lower() + ' in the current experiment, rather than entire project'
        output_help = 'Name of output file'
        force_help = 'Force overwrite of existing output file'
        
        parser = argparse.ArgumentParser(
            description='List ' + self.typename_plural.lower(),
            prog='mc ' + self.cmdname)
        parser.add_argument('expr', nargs='*', default=None, help=expr_help)
        parser.add_argument('--id', action="store_true", default=False, help=id_help)
        parser.add_argument('-d', '--details', action="store_true", default=False, help=details_help)
        parser.add_argument('--json', action="store_true", default=False, help=json_help)
        parser.add_argument('-o', '--output', nargs='*', default=None, help=output_help)
        parser.add_argument('-f', '--force', action="store_true", default=False, help=force_help)
        if self.expt_member:
            parser.add_argument('--expt', action="store_true", default=False, help=expt_help)
        
        # ignore 'mc proc'
        args = parser.parse_args(argv[2:])
        
        output = None
        if args.output:
            output = args.output[0]
        
        with output_method(output, args.force) as out:
            objects = self.get_all_objects(args)
            self.output(out, args, objects)
        return


    def get_all_objects(self, args):
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
            else:
                objects = [d for d in data if _any_match(d.name)]
        else:
            objects = data
        
        return objects
    
    
    def output(self, out, args, objects):
        
        if args.details:
            for obj in objects:
                obj.pretty_print(shift=0, indent=2)
        elif args.json:
            for obj in objects:
                json.dump(out, p.input_data, indent=2)
        else:
            data = []
            for obj in objects:
                data.append(self.list_data(obj))
                df = DataFrame.from_records(data, columns=self.list_columns)
            out.write(tabulate(df, showindex=False, headers=self.list_columns))   

import sys
import argparse
import mcapi
from mcapi.cli.functions import _proj_path, make_local_project, _print_projects

def proj_subcommand():
    """
    Show list of projects
    
    Goal: 
        mc proj [--details] [--remote <remotename> ...] [<projname> ...]
    
    Current: 
        mc proj
    """
    parser = argparse.ArgumentParser(
        description='Projects',
        prog='mc proj')
    parser.add_argument('-d', '--delete', nargs=1, help='Delete a project, specified by id')
    parser.add_argument('-n', '--dry-run', action="store_true", default=False, help='Dry run deletion')
    
    # ignore 'mc proj'
    args = parser.parse_args(sys.argv[2:])
    
    if args.delete:
        print "delete:", args.delete
        print "dry_run:", args.dry_run
        proj = mcapi.get_project_by_id(args.delete[0])
        print "name:", proj.name
        proj.delete(dry_run=args.dry_run)
        print "delete_tally:"
        for key, val in proj.delete_tally.__dict__.iteritems():
            print key, val
            
    else:
        projects = mcapi.get_all_projects()
        
        current = None
        if _proj_path() is not None:
            current = make_local_project()
        
        _print_projects(projects, current)
    
    

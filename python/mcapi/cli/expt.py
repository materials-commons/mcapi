import sys
import argparse
from mcapi.cli.functions import make_local_project, _get_experiments, \
    set_current_experiment, _print_experiments

def expt_subcommand():
    """
    List, create, delete, and modify experiments
    
    mc expt
    mc expt [-c] <exptname>
    
    """
    parser = argparse.ArgumentParser(
        description='List, create, delete, and modify experiments',
        prog='mc expt')
    parser.add_argument('expts', nargs='*', default=None, help='Experiment names (or id if --id given)')
    parser.add_argument('-l', '--list', action="store_true", default=True, help='List experiments (default)')
    parser.add_argument('-c', '--create', action="store_true", default=False, help='Create experiments')
    parser.add_argument('-d', '--delete', action="store_true", default=False, help='Delete experiments')
    parser.add_argument('-s', '--set', action="store_true", default=False, help='Set current experiment')
    parser.add_argument('--id', action="store_true", default=False, help='Input experiment id instead of name')
    parser.add_argument('--desc', type=str, default="", help='Experiment description')
    #parser.add_argument('-m', '--rename', type=str, default='origin', help='Rename experiment')
    
    # ignore 'mc expt'
    args = parser.parse_args(sys.argv[2:])
    
    proj = make_local_project()
    expt_list = _get_experiments(proj)
    expts = {e.name:e for e in expt_list}
    expt_ids = {e.id:e for e in expt_list}
    
    if args.create:
        if len(args.expts) != 1:
            print 'create one experiment at a time'
            print 'example: mc expt -c ExptName --desc "short description"'
            parser.print_help()
            exit(1)
        for name in args.expts:
            if name not in expts:
                expt = proj.create_experiment(name, args.desc)
                print 'Created experiment:', expt.name
                set_current_experiment(proj, expt)
            else:
                print 'experiment: \'' + name + '\' already exists'
    
    elif args.delete:
        for name in args.expts:
            if args.id:
                _delete_experiment(proj.id, expt_ids[name])
            else:
                _delete_experiment(proj.id, expts[name])
            print 'Deleted experiment:', name
    
    elif args.set:
        if len(args.expts) != 1:
            print 'set one current experiment at a time'
            print 'example: mc expt -s ExptName'
            parser.print_help()
            exit(1)
        
        if args.id:
            set_current_experiment(proj, expt_ids[args.expts[0]])
        else:
            set_current_experiment(proj, expts[args.expts[0]])
    
    elif args.list:
        
        _print_experiments(_get_experiments(proj), make_local_expt(proj))
    
    return


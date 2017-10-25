import sys
import argparse
from .functions import make_local_project, make_local_expt, \
    set_current_experiment, _print_experiments


def expt_subcommand(argv=sys.argv):
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
    # parser.add_argument('-m', '--rename', type=str, default='origin', help='Rename experiment')

    # ignore 'mc expt'
    args = parser.parse_args(argv[2:])

    proj = make_local_project()
    expt_list = proj.get_all_experiments()
    expts = {e.name: e for e in expt_list}
    expt_ids = {e.id: e for e in expt_list}

    if args.create:
        if len(args.expts) != 1:
            print('create one experiment at a time')
            print('example: mc expt -c ExptName --desc "short description"')
            parser.print_help()
            exit(1)
        for name in args.expts:
            if name not in expts:
                expt = proj.create_experiment(name, args.desc)
                print('Created experiment:', expt.name)
                set_current_experiment(proj, expt)
                print("Set current experiment: '" + expt.name + "'")
            else:
                print('experiment: \'' + name + '\' already exists')

    elif args.delete:
        for name in args.expts:
            if args.id:
                _expts = expt_ids
            else:
                _expts = expts
            _expts[name].delete()
            # Note Delete tally depreciated
            # print('Deleted experiment:', name)
            # for key, val in _expts[name].delete_tally.__dict__.items():
            #    print(key, val)
            # print("")

    elif args.set:
        if len(args.expts) != 1:
            print('set one current experiment at a time')
            print('example: mc expt -s ExptName')
            parser.print_help()
            exit(1)

        if args.id:
            set_current_experiment(proj, expt_ids[args.expts[0]])
            print("Set current experiment: '" + expt_ids[args.expts[0]].name + "'")
        else:
            set_current_experiment(proj, expts[args.expts[0]])
            print("Set current experiment: '" + expts[args.expts[0]].name + "'")

    elif args.list:

        _print_experiments(proj.get_all_experiments(), make_local_expt(proj))

    return

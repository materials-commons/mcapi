import json
import sys
from .functions import make_local_project, make_local_expt, current_experiment_id, \
    set_current_experiment, _print_experiments, _proj_path, _trunc_name, _trunc_desc, _proj_config
from .list_objects import ListObjects

class ExptSubcommand(ListObjects):
    """
    List, create, delete, and modify experiments

    mc expt
    mc expt [-c] <exptname>

    """
    def __init__(self):
        super(ExptSubcommand, self).__init__(
            ["expt"], "Experiment", "Experiments",
            requires_project=True, proj_member=True, expt_member=False,
            list_columns=['current', 'name', 'description', 'owner', 'id', 'mtime'],
            headers=['', 'name', 'owner', 'description', 'id', 'mtime'],
            creatable=True,
            deletable=True,
            custom_selection_actions=['set']
        )

    def get_all_from_experiment(self, expt):
        raise Exception("Experiments are not members of experiments")

    def get_all_from_project(self, proj):
        return proj.get_all_experiments()

    def list_data(self, obj):
        _is_current = ' '
        if _proj_path() is not None:
            with open(_proj_config()) as f:
                j = json.load(f)
            if obj.id == j.get('experiment_id', None):
                _is_current = '*'

        return {
            'current': _is_current,
            'name': _trunc_name(obj),
            'description': _trunc_desc(obj),
            'owner': obj.owner,
            'id': obj.id,
            'mtime': obj.mtime.strftime("%b %Y %d %H:%M:%S")
        }

    def create(self, args, out=sys.stdout):
        proj = make_local_project()
        expt_list = proj.get_all_experiments()
        expt_names = {e.name: e for e in expt_list}

        if len(args.expr) != 1:
            print('create one experiment at a time')
            print('example: mc expt ExptName --create --desc "short description"')
            parser.print_help()
            exit(1)
        for name in args.expr:
            if name not in expt_names:
                expt = proj.create_experiment(name, args.desc)
                print('Created experiment:', expt.name)
                set_current_experiment(proj, expt)
                print("Set current experiment: '" + expt.name + "'")
            else:
                print('experiment: \'' + name + '\' already exists')
        return

    def delete(self, objects, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting experiments.\n')
            out.write('Aborting\n')
            return

        for obj in objects:
            if obj.id == current_experiment_id(obj.project):
                set_current_experiment(obj.project, None)
                print("Unset current experiment")
            obj.delete()
            # out.write('Deleted experiment: ' + obj.name + ' ' + obj.id + '\n')
            # for key, val in obj.delete_tally.__dict__.items():
            #     out.write(str(key) + ' ' + str(val) + '\n')
            out.write('\n')

    def set(self, objects, args, out=sys.stdout):
        if len(objects) != 1:
            print('set one current experiment at a time')
            print('example: mc expt -s ExptName')
            exit(1)

        for expt in objects:
            set_current_experiment(expt.project, expt)
            out.write("Set current experiment: '" + expt.name + "'\n")
        return

    def add_custom_options(self, parser):

        # for --create, add experiment description
        parser.add_argument('--desc', type=str, default="", help='Experiment description')

        # custom action --set
        parser.add_argument('-s', '--set', action="store_true", default=False, help='Set current experiment')


# def expt_subcommand(argv=sys.argv):
#     """
#     List, create, delete, and modify experiments
#
#     mc expt
#     mc expt [-c] <exptname>
#
#     """
#     parser = argparse.ArgumentParser(
#         description='List, create, delete, and modify experiments',
#         prog='mc expt')
#     parser.add_argument('expts', nargs='*', default=None, help='Experiment names (or id if --id given)')
#     parser.add_argument('-l', '--list', action="store_true", default=True, help='List experiments (default)')
#     parser.add_argument('-c', '--create', action="store_true", default=False, help='Create experiments')
#     parser.add_argument('-d', '--delete', action="store_true", default=False, help='Delete experiments')
#     parser.add_argument('-s', '--set', action="store_true", default=False, help='Set current experiment')
#     parser.add_argument('--id', action="store_true", default=False, help='Input experiment id instead of name')
#     parser.add_argument('--desc', type=str, default="", help='Experiment description')
#     # parser.add_argument('-m', '--rename', type=str, default='origin', help='Rename experiment')
#
#     # ignore 'mc expt'
#     args = parser.parse_args(argv[2:])
#
#     proj = make_local_project()
#     expt_list = proj.get_all_experiments()
#     expts = {e.name: e for e in expt_list}
#     expt_ids = {e.id: e for e in expt_list}
#
#     if args.create:
#         if len(args.expts) != 1:
#             print('create one experiment at a time')
#             print('example: mc expt -c ExptName --desc "short description"')
#             parser.print_help()
#             exit(1)
#         for name in args.expts:
#             if name not in expts:
#                 expt = proj.create_experiment(name, args.desc)
#                 print('Created experiment:', expt.name)
#                 set_current_experiment(proj, expt)
#                 print("Set current experiment: '" + expt.name + "'")
#             else:
#                 print('experiment: \'' + name + '\' already exists')
#
#     elif args.delete:
#         for name in args.expts:
#             if args.id:
#                 _expts = expt_ids
#             else:
#                 _expts = expts
#             _expts[name].delete()
#             # Note Delete tally depreciated
#             # print('Deleted experiment:', name)
#             # for key, val in _expts[name].delete_tally.__dict__.items():
#             #    print(key, val)
#             # print("")
#
#     elif args.set:
#         if len(args.expts) != 1:
#             print('set one current experiment at a time')
#             print('example: mc expt -s ExptName')
#             parser.print_help()
#             exit(1)
#
#         if args.id:
#             set_current_experiment(proj, expt_ids[args.expts[0]])
#             print("Set current experiment: '" + expt_ids[args.expts[0]].name + "'")
#         else:
#             set_current_experiment(proj, expts[args.expts[0]])
#             print("Set current experiment: '" + expts[args.expts[0]].name + "'")
#
#     elif args.list:
#
#         _print_experiments(proj.get_all_experiments(), make_local_expt(proj))
#
#     return

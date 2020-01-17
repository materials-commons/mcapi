import json
import sys

from materials_commons.cli.list_objects import ListObjects
import materials_commons.cli.functions as clifuncs

def set_current_experiment(proj, expt=None):
    pconfig = clifuncs.read_project_config(proj.local_path)
    if expt is None:
        pconfig.experiment_id = None
    else:
        pconfig.experiment_id = expt.id
    pconfig.save()

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
            headers=['', 'name', 'description', 'owner', 'id', 'mtime'],
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
        pconfig = clifuncs.read_project_config()
        if pconfig and obj.id == pconfig.experiment_id:
            _is_current = '*'

        return {
            'current': _is_current,
            'name': clifuncs.trunc(obj.name, 40),
            'description': clifuncs.trunc(obj.description, 100),
            'owner': obj.owner,
            'id': obj.id,
            'mtime': clifuncs.format_time(obj.mtime)
        }

    def print_details(self, obj, out=sys.stdout):
        obj.pretty_print(shift=0, indent=2, out=out)

    def create(self, args, out=sys.stdout):
        proj = clifuncs.make_local_project()
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

    def delete(self, objects, args, dry_run, out=sys.stdout):
        if dry_run:
            out.write('Dry-run is not yet possible when deleting experiments.\n')
            out.write('Aborting\n')
            return

        proj = clifuncs.make_local_project()
        current_id = clifuncs.current_experiment_id(proj)

        for obj in objects:
            if obj.id == current_id:
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

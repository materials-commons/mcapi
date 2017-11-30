import os
import copy
import json
from ..api import _Remote as Remote, _make_object, get_project_by_id
# TODO: we should not be using the RAW api interface!
from ..api import __api as mc_raw_api
import pandas
import string
import time
import datetime
from tabulate import tabulate
import requests
import hashlib


def _trunc_name(obj, size=40):
    _name = obj.name
    if len(_name) > size:
        _name = _name[:size-3] + '...'
    return _name


def _trunc_desc(obj, size=100):
    _desc = obj.description
    if len(_desc) > size:
        _desc = _desc[:size-3] + '...'
    return _desc


def _experiments(project_id, remote=Remote()):
    """
    get experiments data for specified project

    Returns
    ----------
      results: List[dict()]

    """
    # TODO: needs to be refactored - there is a method in the Project that gets all the experiments
    return mc_raw_api.get(remote.make_url_v2('projects/' + project_id + '/experiments'), remote=remote)


# mc.py - project object
def _get_experiments(proj):
    """
    get List[materials_commons_api.Experiment] for project
    NOTE: this is not the way to do this - there is a method in the project that gets all the experiments.
    """
    # TODO: needs to be refactored - there is a method in the Project that gets all the experiments
    results = _experiments(proj.id, proj.remote)
    ret = []
    for data in results:
        expt = _make_object(data)
        expt.project = proj
        ret.append(expt)
    return ret


# maybe another file for CLI support
# mc_cli.py/mc.py - additional objects...
def _mc_remotes(path=None):
    """
    Dict of {origin: materialscommons.api.Remote}
    """
    return {'origin': Remote()}


def _format_mtime(mtime):
    if isinstance(mtime, (float, int)):
        return time.strftime("%b %Y %d %H:%M:%S", time.gmtime(mtime))
    elif isinstance(mtime, datetime.datetime):
        return mtime.strftime("%b %Y %d %H:%M:%S")
    else:
        return str(type(mtime))


def _print_projects(projects, current=None):
    """
    Print() list of projects, include '*' for current project

    Arguments:
        projects: List[materials_commons.api.Project]
        current: materials_commons.api.Project containing os.getcwd()
    """
    data = []
    for p in projects:
        _is_current = ' '
        if current is not None and p.id == current.id:
            _is_current = '*'

        if isinstance(p.mtime, (float, int)):
            _mtime = time.strftime("%b %Y %d %H:%M:%S", time.gmtime(p.mtime))
        elif isinstance(p.mtime, datetime.datetime):
            _mtime = p.mtime.strftime("%b %Y %d %H:%M:%S")
        else:
            _mtime = str(type(p.mtime))

        data.append({
            'current': _is_current,
            'name': _trunc_name(p),
            'owner': p.owner,
            'id': p.id,
            'mtime': _mtime
        })

    df = pandas.DataFrame.from_records(
        data,
        columns=['current', 'name', 'owner', 'id', 'mtime']
    )

    # print(df.to_string())
    print(tabulate(df, showindex=False, headers=['', 'name', 'owner', 'id', 'mtime']))


def _print_experiments(experiments, current=None):
    """
    Print() list of experiments, include '*' for current experiment

    Arguments:
        experiments: List[materials_commons.api.Experiment]
        current: current working materials_commons.api.Experiment
    """
    data = []
    for e in experiments:

        _is_current = ' '
        if current is not None and e.id == current.id:
            _is_current = '*'

        data.append({
            'current': _is_current,
            'name': _trunc_name(e),
            'description': _trunc_desc(e),
            'owner': e.owner,
            'id': e.id,
            'mtime': e.mtime.strftime("%b %Y %d %H:%M:%S")
        })

    df = pandas.DataFrame.from_records(
        data,
        columns=['current', 'name', 'description', 'owner', 'id', 'mtime']
    )

    # print(df.to_string())
    print(tabulate(df, showindex=False, headers=['', 'name', 'description', 'owner', 'id', 'mtime']))


def _print_processes(processes, details=False, json=False):
    if not len(processes):
        print("No processes")
        return
    if details:
        _print_processes_details(processes)
    elif json:
        _print_processes_json(processes)
    else:
        _print_processes_list(processes)


def _print_processes_details(processes):
    for p in processes:
        p.pretty_print(shift=0, indent=2)
        print("")


def _print_processes_json(processes):
    for p in processes:
        print(json.dumps(p.input_data, indent=2))


def _print_processes_list(processes):
    data = []
    columns = ['name', 'template_name', 'id', 'mtime']
    for p in processes:
        data.append({
            'name': _trunc_name(p),
            'template_name': p.template_name,
            'id': p.id,
            'mtime': p.mtime.strftime("%b %Y %d %H:%M:%S")
        })

        df = pandas.DataFrame.from_records(data, columns=columns)

    print(tabulate(df, showindex=False, headers=columns))


def _proj_path(path=None):
    if path is None:
        path = os.getcwd()
    # if not os.path.isdir(path):
    #   raise Exception("Error, no directory named: " + path)
    curr = path
    cont = True
    while cont is True:
        test_path = os.path.join(curr, '.mc')
        if os.path.isdir(test_path):
            return curr
        elif curr == os.path.dirname(curr):
            return None
        else:
            curr = os.path.dirname(curr)
    return None


def _proj_config(path=None):
    dirpath = _proj_path(path)
    if dirpath is None:
        return None
    return os.path.join(dirpath, '.mc', 'config.json')


def make_local_project(path=None):
    # get config
    with open(_proj_config(path)) as f:
        j = json.load(f)

    # get remote
    remotes = _mc_remotes()
    remote = None
    for key, val in remotes.items():
        if val.config.mcurl == j['remote_url']:
            remote = val
            break
    if remote is None:
        print("could not find remote:", j['remote_url'])

    # get materials_commons.api.Project by id
    proj = get_project_by_id(j['project_id'])

    proj.local_path = _proj_path(path)
    proj.remote = remote
    return proj


def make_local_expt(proj):
    with open(_proj_config(proj.local_path)) as f:
        j = json.load(f)

    for expt in _get_experiments(proj):
        if expt.id == j['experiment_id']:
            return expt

    return None


def set_current_experiment(proj, expt):
    config_path = _proj_config(proj.local_path)
    with open(config_path, 'r') as f:
        data = json.load(f)
    data['experiment_id'] = expt.id
    with open(config_path, 'w') as f:
        json.dump(data, f)

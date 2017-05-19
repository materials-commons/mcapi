import os
import copy
import json
import mcapi
import pandas
import string
import time
from tabulate import tabulate
import requests
import hashlib


# mc.py - project object - with approperate mapping to api.py
def _experiments(project_id, remote=mcapi.Remote()):
    """
    get experiments data for specified project

    Returns
    ----------
      results: List[dict()]

    """
    return mcapi.api.get(remote.make_url_v2('projects/' + project_id + '/experiments'), remote=remote)


# mc.py - project object
def _get_experiments(proj):
    """
    get List[mcapi.Experiment] for project
    """
    results = _experiments(proj.id, proj.remote)
    ret = []
    for data in results:
        expt = mcapi.mc.make_object(data)
        expt.project = proj
        ret.append(expt)
    return ret

# maybe another file for CLI support
# mcli.py/mc.py - additional objects...
def _mc_remotes(path=None):
    """
    Dict of {name: mcapi.Remote}
    """
    # just 'origin' for now
    return {'origin':mcapi.Remote()}

def _print_projects(projects, current=None):
    """
    Print list of projects, include '*' for current project
    
    Arguments:
        projects: List[mcapi.Project]
        current: mcapi.Project containing os.getcwd()
    """
    data = []
    for p in projects:
        _is_current = ' '
        if current is not None and p.id == current.id:
          _is_current = '*' 
        
        _name = p.name
        if len(_name) > 40:
            _name = _name[:37] + '...'
        
        data.append({
            'current':_is_current,
            'name': _name,
            'owner':p.owner,
            'id':p.id
        })
    
    df = pandas.DataFrame.from_records(data, 
        columns=['current', 'name', 'owner', 'id'])
    
    #print df.to_string()
    print(tabulate(df, showindex=False, headers=['', 'name', 'owner', 'id']))

def _print_experiments(experiments, current=None):
    """
    Print list of experiments, include '*' for current experiment
    
    Arguments:
        experiments: List[mcapi.Experiment]
        current: current working mcapi.Experiment
    """
    data = []
    for e in experiments:
        
        _is_current = ' '
        if current is not None and e.id == current.id:
          _is_current = '*' 
        
        _name = e.name
        if len(_name) > 40:
            _name = _name[:37] + '...'
        
        _description = e.description
        if len(_description) > 100:
            _description = _description[:97] + '...'
        
        data.append({
            'current':_is_current,
            'name': _name,
            'description':_description,
            'owner':e.owner,
            'id':e.id
        })
    
    df = pandas.DataFrame.from_records(data, 
        columns=['current', 'name', 'description', 'owner', 'id'])
    
    #print df.to_string()
    print(tabulate(df, showindex=False, headers=['', 'name', 'description', 'owner', 'id']))

def _proj_path(path=None):
    if path is None:
        path = os.getcwd()
    #if not os.path.isdir(path):
    #  raise Exception("Error, no directory named: " + path)
    curr = path
    cont = True
    while cont == True:
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
    for key, val in remotes.iteritems():
        if val.config.mcurl == j['remote_url']:
            remote = val
            break
    if remote is None:
        print "could not find remote:", j['remote_url']
    
    # get mcapi.Project
    proj =  mcapi.get_project_by_id(j['project_id'])
    
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
    print "set current experiment: '" + expt.name + "'"


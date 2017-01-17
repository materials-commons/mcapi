# temporary home before integrating else where
import os
import sys
import copy
import json
import argparse
import mcapi
import pandas
import string
import time
from tabulate import tabulate
import requests
import StringIO
import imp


def _delete(restpath, remote=mcapi.Remote()):
    r = requests.delete(restpath, params=remote.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()

def _experiments(project_id, remote=mcapi.Remote()):
    """
    get experiments data for specified project

    Returns
    ----------
      results: List[dict()]

    """
    return mcapi.api.get(remote.make_url_v2('projects/' + project_id + '/experiments'), remote=remote)

def _delete_experiment(project_id, experiment_id, remote=mcapi.Remote()):
    """
    delete experiment for specified project

    Returns
    ----------
      results: result

    """
    return _delete(remote.make_url_v2('projects/' + project_id + '/experiments'), remote=remote)

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

def _fetch_project_by_id(id, remote=None):
    if remote is None:
        remote = mcapi.Remote()
    results = mcapi.api.fetch_project(id, remote)
    return mcapi.Project(data=results)

def _local_to_remote_relpath(proj, local_path):
    """
    Arguments:
        proj: mcapi.Project, with proj.path indicating local project location
        local_path: path to file or directory in local tree
    
    Returns:
        remote_path: relative path from the 'top' directory
    """
    return os.path.relpath(local_path, proj.path)

def _obj_path_to_local_path(proj, obj_path):
    """
    Arguments:
        proj: mcapi.Project, with proj.path indicating local project location
        obj_path: Directory.path or File.path
            currently this begins with 'top', instead of being relative to 'top'
    
    Returns:
        local_path: absolute path to file or directory locally
    """
    return os.path.join(os.path.dirname(proj.path), obj_path)

def _get_file_or_directory(proj, local_path):
    """
    Arguments:
        proj: mcapi.Project
        local_path: file or directory local path equivalant
    
    Returns:
        obj: mcapi.File, mcapi.Directory, or None
    """
    if os.path.abspath(local_path) == proj.path:
        return proj.get_top_directory()
    names = string.split(os.path.relpath(local_path, proj.path), '/')
    curr = proj.get_top_directory()
    for n in names:
        nextchild = filter(lambda x: x.name == n, curr.get_children())
        if len(nextchild) == 0:
            return None
        curr = nextchild[0]
    return curr
    

def make_local_project(path=None):
    # get config
    with open(_proj_config(path)) as f:
        j = json.load(f)
    
    # get remote
    remotes = _mc_remotes()
    remote = None
    for key, val in remotes.iteritems():
        if val.mcurl == j['remote_url']:
            remote = val
            break
    if remote is None:
        print "could not find remote:", j['remote_url']
    
    # get mcapi.Project
    proj =  _fetch_project_by_id(j['project_id'], remote)
    
    proj.path = _proj_path(path)
    proj.remote = remote
    return proj


def make_local_expt(proj):
    with open(_proj_config(proj.path)) as f:
        j = json.load(f)
    
    for expt in _get_experiments(proj):
        if expt.id == j['experiment_id']:
            return expt
    
    return None

def set_current_experiment(proj, expt):
    config_path = _proj_config(proj.path)
    with open(config_path, 'r') as f:
        data = json.load(f)
    data['experiment_id'] = expt.id
    with open(config_path, 'w') as f:
        json.dump(data, f)
    print "set current experiment: '" + expt.name + "'"

#  Want to print something like: 
#
#  warning! file0 is a local file and remote dir!
#  warning! file1 is a local direcotry and remote file!
#
#  remote_owner local_mtime local_size remote_mtime remote_size file0 
#             - local_mtime local_size            -           - file1                       
#  remote_owner           -          - remote_mtime remote_size file2                        
#
#  dir1:
#  remote_owner local_mtime local_size remote_mtime remote_size file0 
#             - local_mtime local_size            -           - file1                       
#  remote_owner           -          - remote_mtime remote_size file2                        
#
#  dir2:
#  remote_owner local_mtime local_size remote_mtime remote_size file0 
#             - local_mtime local_size            -           - file1                       
#  remote_owner           -          - remote_mtime remote_size file2
#

def _ls_group(proj, paths, files_only=True):
    """
    Construct DataFrame with 'mc ls' results for paths. Also outputs
    the sets of paths that are files or directories (either local or remote).
    """
    path_data = []
    columns = [
        'owner',
        'l_mtime', 'l_size', 'l_checksum', 'l_type',
        'r_mtime', 'r_size', 'r_checksum', 'r_type',
        'name']
    data_init = {k:'-' for k in columns}
    files = set()
    dirs = set()
    
    for path in paths:
        
        data = copy.deepcopy(data_init)
        data['name'] = os.path.basename(path)
        
        # locals
        if os.path.exists(path):
            data['l_mtime'] = time.strftime("%b %Y %H:%M:%S", time.localtime(os.path.getmtime(path)))
            data['l_size'] = os.path.getsize(path)
            if os.path.isfile(path):
                data['l_type'] = 'file'
                data['l_checksum'] = 'checksum'
                files.add(path)
            elif os.path.isdir(path):
                data['l_type'] = 'dir'
                dirs.add(path)
        
        # remotes
        obj = _get_file_or_directory(proj, path)
        if obj is not None:
            data['owner'] = obj.owner
            if obj.mtime:
                data['r_mtime'] = time.strftime("%b %Y %H:%M:%S", time.localtime(obj.mtime))
            data['r_size'] = obj.size
            if isinstance(obj, mcapi.File):
                data['r_type'] = 'file'
                data['r_checksum'] = obj.checksum
                files.add(path)
            elif isinstance(obj, mcapi.Directory):
                data['r_type'] = 'dir'
                dirs.add(path)
        
        if not files_only or ('file' in [data['l_type'], data['r_type']]):
            path_data.append(data)
    
    return (pandas.DataFrame.from_records(path_data, columns=columns), files, dirs)

class CommonsCLIParser(object):

    standard_usage = [
        {'name':'remote', 'desc': 'List servers'},
        {'name':'proj', 'desc': 'List projects'},
        {'name':'expt', 'desc': 'List, create, delete, and modify experiments'},
        {'name':'init', 'desc': 'Initialize a new project'},
        {'name':'clone', 'desc': 'Clone an existing project'},
        {'name':'ls', 'desc': 'List local and remote directory contents'},
        {'name':'up', 'desc': 'Upload files'},
        {'name':'down', 'desc': 'Download files'}
    ]
    
    def __init__(self):
        pass
    
    def parse_input(self):
        
        usage_help = StringIO.StringIO()
        usage_help.write("mc <command> [<args>]\n\n")
        usage_help.write("The standard mc commands are:\n")
        
        for interface in CommonsCLIParser.standard_usage:
            usage_help.write("  {:10} {:40}\n".format(interface['name'], interface['desc']))
        
        
        # read custom interfaces from config file
        config = mcapi.Config()
        custom_interfaces = {d['name']: d for d in config.interfaces}
        if len(config.interfaces):
            usage_help.write("\nSpecialized commands are:\n")
        for interface in config.interfaces:
            usage_help.write("  {:10} {:40}\n".format(interface['name'], interface['desc']))
       
        parser = argparse.ArgumentParser(
            description='Materials Commons command line interface',
            usage=usage_help.getvalue())
        parser.add_argument('command', help='Subcommand to run')
        
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        
        if hasattr(self, args.command):
            getattr(self, args.command)()
        elif args.command in custom_interfaces:
            # load module and run command
            modulename = custom_interfaces[args.command]['module']
            subcommandname = custom_interfaces[args.command]['subcommand']
            f, filename, description = imp.find_module(modulename)
            try:
                module = imp.load_module(modulename, f, filename, description)
                getattr(module, subcommandname)()
            finally:
                if f:
                    f.close()
            
        else:
            print 'Unrecognized command'
            parser.print_help()
            exit(1)

    def remote(self):
        """
        Show / modify list of known Materials Commons servers.
        
        Goal:
            mc remote [-v]
            mc remote add 
            mc remote remove
        
        Current:
            mc remote
        
        """
        parser = argparse.ArgumentParser(
            description='Server settings')
        
        # ignore 'mc remote'
        args = parser.parse_args(sys.argv[2:])
        
        remotes = _mc_remotes()
        data = [{'name': key, 'url': remotes[key].mcurl} for key in remotes]
        df = pandas.DataFrame.from_records(data, columns=['name', 'url'])
        print df.to_string(index=False)
        

    def proj(self):
        """
        Show list of projects
        
        Goal: 
            mc proj [--details] [--remote <remotename> ...] [<projname> ...]
        
        Current: 
            mc proj
        """
        parser = argparse.ArgumentParser(
            description='Projects')
        
        # ignore 'mc proj'
        args = parser.parse_args(sys.argv[2:])
        
        projects = mcapi.list_projects()
        
        current = None
        if _proj_path() is not None:
            current = make_local_project()
        
        _print_projects(projects, current)
    
    
    def expt(self):
        """
        List, create, delete, and modify experiments
        
        mc expt
        mc expt [-c] <exptname>
        
        """
        parser = argparse.ArgumentParser(
            description='List, create, delete, and modify experiments')
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
    
    def init(self):
        """
        Initialize a new project
        
        mc init <name> <remote> [--desc <description>]
        
        """
        parser = argparse.ArgumentParser(
            description='Initialize a new project')
        parser.add_argument('name', help='Project name')
        parser.add_argument('--remote', type=str, default='origin', help='Remote name')
        parser.add_argument('--desc', type=str, default='', help='Project description')
        
        # ignore 'mc init'
        args = parser.parse_args(sys.argv[2:])
        
        remotes = _mc_remotes()
        if not args.remote in remotes:
            print "unrecognized remote:", args.remote
            parser.print_help()
            exit(1)
        remote=remotes[args.remote]
        
        project = mcapi.create_project(args.name, args.desc)
        #project = mcapi.create_project(args.name, args.desc, remote=remote)
        
        print "Created new project at:", remote.mcurl
        _print_projects([project], project)
    
    def clone(self):
        """
        'Clone' a project, i.e. set the local directory tree where files should
        be uploaded/downloaded. Creates a '.mc/config.json'.
        
        mc clone <projid> [--remote <remotename>]
        
        """
        parser = argparse.ArgumentParser(
            description='Clone an existing project')
        parser.add_argument('id', help='Project id')
        parser.add_argument('--remote', type=str, default='origin', help='Remote name')
        
        # ignore 'mc clone'
        args = parser.parse_args(sys.argv[2:])
        
        remotes = _mc_remotes()
        if not args.remote in remotes:
            print "unrecognized remote:", args.remote
            exit(1)
        remote=remotes[args.remote]
        
        project = _fetch_project_by_id(args.id, remote)
        
        dest = os.path.join(os.getcwd(), project.name)
        
        if _proj_path(dest) is not None:
            print "mc project already exists at", _proj_path(dest)
            exit(1)
        
        if not os.path.exists(dest):
            os.mkdir(dest)
        os.mkdir(os.path.join(dest,'.mc'))
        with open(_proj_config(dest), 'w') as f:
            # set a default current experiment? 
            data = {'remote_url':remote.mcurl, 'project_id': args.id, 'experiment_id': None}
            json.dump(data, f)
        
        print "Cloned project from", remote.mcurl, "to", dest
        _print_projects([project])
    
    def ls(self):
        """
        'ls' a project directory to see local and remote files and directories.
        
        mc ls [<pathspec> ...]
        
        """
        parser = argparse.ArgumentParser(
            description='List local & remote directory contents')
        parser.add_argument('paths', nargs='*', default=[os.getcwd()], help='Files or directories')
        
        # ignore 'mc ls'
        args = parser.parse_args(sys.argv[2:])
        
        local_abspaths = [os.path.abspath(p) for p in args.paths]
        
        proj = make_local_project()
        
        # act on local paths
        (df, files, dirs) = _ls_group(proj, local_abspaths, files_only=True)
        
        # print warnings for type mismatches
        for file in files:
            if file in dirs and os.path.isfile(file):
                print "warning!", file, "is a local file and remote directory!"
            if file in dirs and os.path.isdir(file):
                print "warning!", file, "is a local directory and remote file!"
        
        if df.shape[0]:
            print df.to_string(index=False)
            print ""
        
        for d in dirs:
            
            _locals = []
            if os.path.exists(d):
                _locals = [os.path.join(d, f) for f in os.listdir(d)]
            
            if os.path.abspath(d) == proj.path:
                remote_dir = proj.get_top_directory()
            else:
                remote_dir = _get_file_or_directory(proj, d)
            _remotes = [os.path.join(d, child.name) for child in remote_dir.get_children()]
            
            _local_abspaths = set(_locals + _remotes)
                
            (df, files, dirs) = _ls_group(proj, _local_abspaths, files_only=False)
            
            if df.shape[0]:
                print os.path.relpath(d, os.getcwd()) + ":"
                print df.to_string(index=False)
                print ""
        
        return

    def up(self):
        """
        upload files to Materials Commons
        
        mc up [-r] [<pathspec> ...]
        
        """
        parser = argparse.ArgumentParser(
            description='upload files')
        parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
        parser.add_argument('-r', '--recursive', action="store_true", default=False, help='Upload directory contents recursively')
        
        # ignore 'mc up'
        args = parser.parse_args(sys.argv[2:])
        
        local_abspaths = [os.path.abspath(p) for p in args.paths]
        
        proj = make_local_project()
        
        for p in local_abspaths:
            if os.path.isfile(p):
                #print "uploading:", p
                dir = _get_file_or_directory(proj, os.path.dirname(p))
                result = dir.add_file(os.path.basename(p), p, verbose=True)
                # This should indicate if file already existed on Materials Commons
                #print result.path + ":", result
            elif os.path.isdir(p) and args.recursive:
                #print "uploading:", p
                dir = _get_file_or_directory(proj, os.path.dirname(p))
                result = dir.add_directory_tree(os.path.basename(p), os.path.dirname(p), verbose=True)
                #for f in result:
                #    # This should indicate if file already existed on Materials Commons
                #    print f.path + ":", f
            else:
                print "error uploading:", os.path.relpath(p, os.getcwd())
                print "use -r option to upload directory contents, recursively"
        return
    
    def down(self):
        """
        download files from Materials Commons
        
        mc down [-r] [<pathspec> ...]
        
        """
        parser = argparse.ArgumentParser(
            description='download files')
        parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
        parser.add_argument('-r', '--recursive', action="store_true", default=False, help='Download directory contents recursively')
        parser.add_argument('-f', '--force', action="store_true", default=False, help='Force overwrite of existing files')
        
        # ignore 'mc down'
        args = parser.parse_args(sys.argv[2:])
        
        local_abspaths = [os.path.abspath(p) for p in args.paths]
        
        proj = make_local_project()
        
        def _check_download(proj_id, file_id, local_path, remote):
            if not os.path.exists(local_path) or args.force:
                return mcapi.api.file_download(proj_id, file_id, local_path, remote)
            else:
                print "Overwrite '" + os.path.relpath(local_path, os.getcwd()) + "'?"
                while True:
                    ans = raw_input('y/n: ')
                    if ans == 'y':
                        return mcapi.api.file_download(proj_id, file_id, local_path, remote)
                    elif ans == 'n':
                        break
            return None
        
        def _download(proj, dir, recursive=False):
            results = []
            children = dir.get_children()
            for child in children:
                
                if isinstance(child, mcapi.File):
                    p = _obj_path_to_local_path(proj, os.path.join(child._parent.path, child.name))
                    if not os.path.exists(os.path.dirname(p)):
                        os.makedirs(os.path.dirname(p))
                    result_path = _check_download(proj.id, child.id, p, proj.remote)
                    if result_path is not None:
                        print "downloaded:", os.path.relpath(result_path, os.getcwd())
                    results.append(result_path)
                
                elif isinstance(child, mcapi.Directory) and recursive:
                    _download(proj, child, recursive=recursive)
            
            return results
        
        for p in local_abspaths:
            
            if os.path.abspath(p) == proj.path:
                obj = proj.get_top_directory()
            else:
                obj = _get_file_or_directory(proj, p)
            
            if isinstance(obj, mcapi.File):
                #(project_id, file_id, output_file_path, remote=use_remote())
                result_path = _check_download(proj.id, obj.id, p, proj.remote) 
                if result_path is not None:
                    print "downloaded:", os.path.relpath(result_path, os.getcwd())
            
            elif isinstance(obj, mcapi.Directory):
                _download(proj, obj, recursive=args.recursive)
                
        return
    


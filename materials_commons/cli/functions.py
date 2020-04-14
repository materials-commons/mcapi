import copy
import datetime
import dateutil.parser
import getpass
import json
import hashlib
import io
import os
import re
import string
import sys
import time

import requests

import materials_commons.api as mcapi
from .print_formatter import PrintFormatter, trunc
from .sqltable import SqlTable
from .exceptions import MCCLIException
# TODO: we should not be using the RAW api interface!
from ..api import __api as mc_raw_api

_log = False

def turn_REST_logging_on():
    global _log
    mcapi.__api._log = True
    _log = True

def turn_REST_logging_off():
    global _log
    mcapi.__api._log = False
    _log = False

def post_v3(name, params={}, remote=None):
    """Inserts apikey if not present in params"""
    # remote = mc_raw_api.configure_remote(remote, None)
    # if 'apikey' not in params and remote.config.mcapikey:
    #     params['apikey'] = remote.config.mcapikey
    # try:
    #     if _log:
    #         _params = copy.deepcopy(params)
    #         if 'apikey' in _params:
    #             del _params['apikey']
    #         print("POST:", remote.make_url_v3(name), _params)
    #     r = requests.post(remote.make_url_v3(name), json=params, verify=False)
    #     r.raise_for_status()
    #     return r.json()
    # except requests.exceptions.ConnectionError as e:
    #     print("Could not connect to " + remote.config.mcurl)
    #     exit(1)

    try:
        return mc_raw_api.post_v3(name, params=params, remote=remote)
    except requests.exceptions.ConnectionError as e:
        print("Could not connect to " + remote.config.mcurl)
        exit(1)

def post_v4(name, params={}, remote=None):
    """Inserts apikey if not present in params"""
    # remote = mc_raw_api.configure_remote(remote, None)
    # if 'apikey' not in params and remote.config.mcapikey:
    #     params['apikey'] = remote.config.mcapikey
    # try:
    #     if _log:
    #         _params = copy.deepcopy(params)
    #         if 'apikey' in _params:
    #             del _params['apikey']
    #         print("POSTv4:", remote.make_url_v4(name), _params)
    #     r = requests.post(remote.make_url_v4(name), json=params, verify=False)
    #     r.raise_for_status()
    #     return r.json()
    # except requests.exceptions.ConnectionError as e:
    #     print("Could not connect to " + remote.config.mcurl)
    #     exit(1)

    try:
        return mc_raw_api.post_v4(name, params=params, remote=remote)
    except requests.exceptions.ConnectionError as e:
        print("Could not connect to " + remote.config.mcurl)
        exit(1)

def get_project_by_id_v3(project_id, remote=None):
    data = post_v3("getProject", {"project_id": project_id}, remote=remote)['data']
    return mcapi.Project(data=data, remote=remote)

def get_project_by_id_or_exit(project_id, remote=None):
    try:
        return get_project_by_id_v3(project_id, remote=remote)
    except requests.exceptions.ConnectionError as e:
        print("Could not connect to " + remote.config.mcurl)
        exit(1)

def get_all_templates_or_exit(remote=None):
    try:
        return mcapi.get_all_templates(remote=remote)
    except requests.exceptions.ConnectionError as e:
        print("Could not connect to " + remote.config.mcurl)
        exit(1)

def v2_get_all_projects_or_exit(remote=None):
    try:
        return mcapi.get_all_projects(remote=remote)
    except requests.exceptions.ConnectionError as e:
        print("Could not connect to " + remote.config.mcurl)
        exit(1)

def create_project_or_exit(name, desc, remote=None):
    try:
        return mcapi.create_project(name, desc, remote=remote)
    except requests.exceptions.ConnectionError as e:
        print("Could not connect to " + remote.config.mcurl)
        exit(1)

def get_dataset(project_id, dataset_id, remote=None):
    try:
        result = post_v3(
            "getDataset",
            {"project_id": project_id, "dataset_id": dataset_id},
            remote=remote)
    except requests.exceptions.HTTPError as e:
        result = e.response.json()
        print(result["error"])
        if "error" in result and re.match("Unable retrieve dataset", result["error"]):
            return None
        else:
            raise e
    return mcapi.Dataset(data=result['data'])

def get_published_dataset(dataset_id, remote=None):
    try:
        result = post_v3(
            "getPublishedDataset",
            {"dataset_id": dataset_id},
            remote=remote)
    except requests.exceptions.HTTPError as e:
        result = e.response.json()
        print(result["error"])
        if "error" in result and re.match("Unable retrieve dataset", result["error"]):
            return None
        else:
            raise e
    return mcapi.Dataset(data=result['data'])

def get_directory_by_path(proj, directory_path):
    """Return mcapi.Directory or None"""
    from materials_commons.api.mc_object_utility import make_object

    try:
        result = post_v3(
            "getDirectoryByPathForProject",
            {"project_id": proj.id, "directory_path": directory_path},
            remote=proj.remote)
    except requests.exceptions.HTTPError as e:
        result = e.response.json()
        if "error" in result and re.match("Unable retrieve directory", result["error"]):
            return None
        else:
            raise e

    dir = make_object(result["data"])
    dir._project = proj
    dir.shallow = False
    return dir

def get_directory_by_id(proj, directory_id):
    from materials_commons.api.mc_object_utility import make_object
    data = post_v3(
        "getDirectoryForProject",
        {"project_id": proj.id, "directory_id": directory_id},
        remote=proj.remote)['data']
    dir = make_object(data)
    dir._project = proj
    dir.shallow = False
    return dir

def get_top_directory(proj):
    return get_directory_by_path(proj, proj.name)

def get_file_by_path(proj, path):
    data = post_v3(
        "getFileByPathInProject",
        {"project_id": proj.id, "path": path},
        remote=proj.remote)['data']
    file = mcapi.File(data=data)
    return file

def get_file_by_id(proj, file_id):
    data = post_v3(
        "getFileInProject",
        {"project_id": proj.id, "file_id": file_id},
        remote=proj.remote)['data']
    file = mcapi.File(data=data)
    return file

def get_by_path(proj, path):
    """Get File or Directory by path, or return None"""
    if path == proj.name:
        return get_top_directory(proj)

    parent_path = os.path.dirname(path)
    basename = os.path.basename(path)

    parent_dir = get_directory_by_path(proj, parent_path)

    if not parent_dir:
        return None

    for child in parent_dir.get_children():
        if child.name == basename:
            return child

    return None

def get_by_local_path(proj, local_path):
    """Get File or Directory by path"""
    refpath = os.path.dirname(proj.local_path)
    path = os.path.relpath(local_path, refpath)
    return get_by_path(proj, path)

def get_directory_id_by_path(project_id, directory_path, remote=None):
    return post_v3(
        "getDirectoryByPathForProject",
        {"project_id": project_id, "directory_path": directory_path},
        remote=remote)['data']['id']

def get_children(dir):
    self = dir
    if hasattr(self, 'input_data') and 'children' in self.input_data:
        results = self.input_data
    else:
        results = post_v3(
            "getDirectoryForProject",
            {"project_id": self._project.id, "directory_id": self.id},
            remote=self._project.remote)['data']
    ret = []
    for dir_or_file in results['children']:
        its_type = dir_or_file['otype']
        if its_type == 'file':
            obj = mcapi.File(data=dir_or_file)
            obj._directory_id = self.id
        if its_type == 'directory':
            obj = mcapi.Directory(data=dir_or_file)
            obj._parent_id = self.id
        obj._project = self._project
        ret.append(obj)
    return ret

def get_parent_id(file_or_dir):
    """Get _parent_id, else _directory_id, else raise"""
    if hasattr(file_or_dir, '_parent_id'):
        if file_or_dir._parent_id == file_or_dir.id:
            raise MCCLIException("_parent_id == id")
        return file_or_dir._parent_id
    elif hasattr(file_or_dir, '_directory_id'):
        if file_or_dir._directory_id == file_or_dir.id:
            raise MCCLIException("_directory_id == id")
        return file_or_dir._directory_id
    else:
        raise MCCLIException("file_or_dir is missing _parent_id or _directory_id")

def delete_files_and_directories(proj, parent_id, files_and_dirs=[]):
    """
    Arguments
    ---------
    proj: mcapi.Project
    parent_id: str, ID of Parent directory of the files and directories to be deleted
    files_and_dirs: List of dict,
        Elements describe a file or directory inside the parent directory using the format:
            {"id":<file_or_dir_id>, "otype": <'file' or 'directory'>}
    """
    # params = {"project_id": proj.id, "directory_id": parent_id, "files": files_and_dirs}
    # result = post_v3(
    #     "deleteFilesFromDirectoryInProject",
    #     params=params,
    #     remote=proj.remote)

    for file_or_dir in files_and_dirs:
        if file_or_dir['otype'] == 'file':
            mc_raw_api.file_delete(proj.id, file_or_dir['id'], remote=proj.remote)
        elif file_or_dir['otype'] == 'directory':
            mc_raw_api.directory_delete(proj.id, file_or_dir['id'], remote=proj.remote)
        else:
            raise MCCLIException("Error in delete_files_and_directories: " + str(file_or_dir))

def download_file_as_string(project_id, file_id, remote=None, apikey=None):
    remote = mc_raw_api.configure_remote(remote, apikey)
    f = io.BytesIO()
    api_url = "projects/" + project_id + "/files/" + file_id + "/download"
    restpath = remote.make_url_v2(api_url)
    r = requests.get(restpath, params=remote.config.get_params(), stream=True, verify=False)

    if not r.ok:
        r.raise_for_status()

    for block in r.iter_content(1024):
        f.write(block)

    return f.getvalue().decode('utf-8')

def getit(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    else:
        return getattr(obj, name, default)

def as_is(value):
    return value

def epoch_time(mtime):
    if isinstance(mtime, str): # expect ISO 8601 str
        return time.mktime(dateutil.parser.parse(mtime).timetuple())
    elif isinstance(mtime, (float, int)):
        return mtime
    elif isinstance(mtime, datetime.datetime):
        return time.mktime(mtime.timetuple())
    elif isinstance(mtime, dict) and ('epoch_time' in mtime):
        return mtime['epoch_time']
    elif mtime is None:
        return None
    else:
        return str(type(mtime))

def format_time(mtime, fmt="%b %Y %d %H:%M:%S"):
    if isinstance(mtime, str): # expect ISO 8601 str
        return dateutil.parser.parse(mtime).strftime(fmt)
    elif isinstance(mtime, (float, int)):
        return time.strftime(fmt, time.localtime(mtime))
    elif isinstance(mtime, datetime.datetime):
        return mtime.strftime(fmt)
    elif isinstance(mtime, dict) and ('epoch_time' in mtime):
        return format_time(mtime['epoch_time'])
    elif mtime is None:
        return '-'
    else:
        return str(type(mtime))

def checksum(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def print_projects(projects, current=None):
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

        data.append({
            'current': _is_current,
            'name': trunc(p.name, 40),
            'owner': p.owner,
            'id': p.id,
            'mtime': format_time(p.mtime)
        })

    columns=['current', 'name', 'owner', 'id', 'mtime']
    headers=['', 'name', 'owner', 'id', 'mtime']
    mcapi.print_table(data, columns=columns, headers=headers)

def print_experiments(experiments, current=None):
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
            'name': trunc(e, 40),
            'description': trunc(e, 100),
            'owner': e.owner,
            'id': e.id,
            'mtime': e.mtime.strftime("%b %Y %d %H:%M:%S")
        })

    columns = ['current', 'name', 'description', 'owner', 'id', 'mtime']
    headers = ['', 'name', 'description', 'owner', 'id', 'mtime']
    mcapi.print_table(data, columns=columns, headers=headers)

def _proj_path(path=None):
    """Find project path if .mc directory already exists, else return None"""
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

def project_path(path=None):
    """Return path to local project, else None"""
    return _proj_path(path)

def project_exists(path=None):
    if _proj_path(path):
        return True
    return False

def _mcdir(path=None):
    """Find project .mc directory path if it already exists, else return None"""
    dirpath = _proj_path(path)
    if dirpath is None:
        return None
    return os.path.join(dirpath, '.mc')


def _proj_config(path=None):
    """Find project config path if .mc directory already exists, else return None"""
    dirpath = _proj_path(path)
    if dirpath is None:
        return None
    return os.path.join(dirpath, '.mc', 'config.json')

class ProjectConfig(object):
    """
    Format:
        {
            "remote": {
                "mcurl": <url>,
                "email": <email>
            },
            "project_id": <id>,
            "experiment_id": <id>,
            "remote_updatetime": <number>
        }

    Attributes
    ----------
        project_id: str or None
        experiment_id: str or None
        remote: mcapi.RemoteConfig
        remote_updatetime: number or None

    """
    def __init__(self, project_path):
        self.project_path = project_path
        self.config_dir = os.path.join(self.project_path, ".mc")
        self.config_path = os.path.join(self.config_dir, "config.json")

        data = {}
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                data = json.load(f)

        # handle deprecated 'remote_url'
        if 'remote_url' in data and 'remote' not in data:
            config = mcapi.Config()
            matching = [rconfig for rconfig in config.remotes if rconfig.mcurl == data['remote_url']]
            if len(matching) == 0:
                print("Could not make local project, failed to find remote with url: {0}".format(data['remote_url']))
                print_remote_help()
                exit(1)
            elif len(matching) > 1:
                print("Could not make local project, found multiple remote accounts for url: {0}".format(data['remote_url']))
                print('** Please edit .mc/config.json to include `"remote":{"mcurl": "' + data['remote_url'] + '", "email": "YOUR_EMAIL_HERE"}` **')
                exit(1)
            else:
                data['remote'] = dict()
                data['remote']['mcurl'] = matching[0].mcurl
                data['remote']['email'] = matching[0].email

        self.remote = mcapi.RemoteConfig(**data.get('remote', {}))
        self.project_id = data.get('project_id', None)
        self.experiment_id = data.get('experiment_id', None)
        self.remote_updatetime = data.get('remote_updatetime', None)

    def to_dict(self):
        return {
            'remote': {
                'mcurl': self.remote.mcurl,
                'email': self.remote.email
            },
            'project_id': self.project_id,
            'experiment_id': self.experiment_id,
            'remote_updatetime': self.remote_updatetime
        }

    def save(self):
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        with open(self.config_path, 'w') as f:
            json.dump(self.to_dict(), f)
        return

def read_project_config(path=None):
    """Read <project>/.mc/config.json file, or return None"""
    # get config
    proj_config_path = _proj_config(path)
    if proj_config_path:
        return ProjectConfig(project_path(path))
    else:
        return None

VIEW_OTYPE = {
  "process": "proc",
  "sample": "samp",
  "dataset": "dset",
  "project": "proj",
  "attribute": "attr",
  "measurement": "val",
  "attribute_set": "aset",
  "file": "file",
  "directory": "dir",
  "experiment": "expt",
  "action": "act"
}

def view_otype(otype):
    return VIEW_OTYPE[otype]

def read_view_state(path=None):
    mcdirpath = _mcdir(path)
    if not mcdirpath:
        print("No .mc directory. Exiting...")
        exit(1)
    viewstatepath = os.path.join(mcdirpath, 'view_state.json')
    if not os.path.exists(viewstatepath):
        return None
    with open(viewstatepath, 'w') as f:
        data = json.load(f)
    return data

def write_view_state(data, path=None):
    mcdirpath = _mcdir(path)
    if not mcdirpath:
        print("No .mc directory. Exiting...")
        exit(1)
    viewstatepath = os.path.join(mcdirpath, 'view_state.json')
    with open(viewstatepath, 'w') as f:
        json.dump(data, f)
    return

# def write_project_config(proj, experiment_id=None):
#     """Write <project>/.mc/config.json file
#
#     Format:
#         {
#             "remote": {
#                 "mcurl": <url>,
#                 "email": <email>
#             },
#             "project_id": <id>,
#             "experiment_id": <id>,
#             "remote_updatetime": <number>
#         }
#     """
#     proj_config_dir = os.path.join(proj.local_path, ".mc")
#     proj_config_path = os.path.join(proj_config_dir, "config.json")
#     if not os.path.exists(proj_config_dir):
#         os.mkdir(proj_config_dir)
#
#     config = {
#         'remote': {
#             'mcurl': proj.remote.config.mcurl,
#             'email': proj.remote.config.email
#         },
#         'project_id': proj.id,
#         'experiment_id': experiment_id
#     }
#
#     with open(proj_config_path, 'w') as f:
#         json.dump(config, f)
#     return

def print_remote_help():
    print("Add a remote with:")
    print("    mc remote --add EMAIL URL")
    print("List current remotes with:")
    print("    mc remote")
    print("List other known remote urls with:")
    print("    mc remote -l")

def make_local_project_remote(path=None):
    pconfig = read_project_config(path)
    if not pconfig:
        return None

    config = mcapi.Config()
    rconfig = pconfig.remote
    if rconfig not in config.remotes:
        print("Could not make project Remote, failed to find remote config: {0} {1}".format(rconfig.email, rconfig.mcurl))
        print_remote_help()
        exit(1)
    rconfig_with_apikey = config.remotes[config.remotes.index(rconfig)]
    return mcapi.Remote(rconfig_with_apikey)

class ProjectTable(SqlTable):

    @staticmethod
    def default_print_fmt():
        """list of tuple, see an example"""
        return [
            ("name", "name", "<", 24, as_is),
            ("id", "id", "<", 36, as_is),
            ("checktime", "checktime", "<", 24, format_time)
        ]

    @staticmethod
    def tablecolumns():
        """dict, column name as key, list of table creation args for value. Requires unique 'id'."""
        return {
            "id": ["text", "UNIQUE"],
            "name": ["text"],
            "data": ["text"],
            "checktime": ["real"]     # last time the remote data was queried (s since epoch)
        }

    @staticmethod
    def tablename():
        return "project"

    def __init__(self, proj_local_path):
        """

        Arguments:
            proj_local_path: str, Path to project, locally.
        """
        super(ProjectTable, self).__init__(proj_local_path)

    def select_all(self):
        """Select record by id

        Returns:
             sqlite3.Row or None
        """
        self.curs.execute("SELECT * FROM " + self.tablename())
        return self.curs.fetchall()

def make_local_project(path=None):

    proj_path = project_path(path)
    if not proj_path:
        print("Not a Materials Commons project (or any of the parent directories)")
        exit(1)

    pconfig = read_project_config(path)

    ptable = ProjectTable(proj_path)
    ptable.connect()
    results = ptable.select_all()
    ptable.close()

    if len(results) > 1:
        raise MCCLIException("project db error: Found >1 project")

    remote = make_local_project_remote(path)
    if not results or not pconfig.remote_updatetime or results[0]['checktime'] < pconfig.remote_updatetime:
        checktime = time.time()
        try:
            data = post_v3("getProject", {"project_id": pconfig.project_id}, remote=remote)['data']
        except requests.exceptions.ConnectionError as e:
            print("Could not connect to " + remote.config.mcurl)
            exit(1)
        except requests.exceptions.HTTPError as e:
            # raise mcapi.MCNotFoundException(e.response.json()['error'])
            print(e.response.json()['error'])
            exit(1)

        record = {
            'id': pconfig.project_id,
            'name': data['name'],
            'data': json.dumps(data),
            'checktime': checktime
        }
        ptable.connect()
        ptable.insert_or_replace(record)
        ptable.close()
    else:
        record = results[0]

    proj = mcapi.Project(data=json.loads(record['data']), remote=remote)
    proj.local_path = proj_path
    return proj

def make_local_expt(proj):
    pconfig = read_project_config(proj.local_path)

    if pconfig:
        for expt in proj.get_all_experiments():
            if expt.id == pconfig.experiment_id:
                return expt

    return None

def current_experiment_id(proj):
    """Return current experiment id, else None"""
    pconfig = read_project_config(proj.local_path)
    if pconfig:
        return pconfig.experiment_id
    else:
        return None

def humanize(file_size_bytes):
    abbrev = [("B", 0), ("K", 10), ("M", 20), ("G", 30), ("T", 40)]
    for key, val in abbrev:
        _size = (file_size_bytes >> val)
        if _size < 1000 or key == "T":
            return str(_size) + key

def request_confirmation(msg, force=False):
    """Request user confirmation

    Arguments
    ---------
    msg: str
        Ex: "Are you sure you want to permanently delete these?", will prompt user with:

            "Are you sure you want to permanently delete these? ('Yes'/'No'): "

    force: bool
        Proceed without user confirmation

    Returns
    -------
    confirmation: bool
        True if confirmed or forced, False if not confirmed.
    """
    if not force:
        msg = msg + " ('Yes'/'No'): "
        while True:
            input_str = input(msg)
            if input_str == 'No':
                return False
            elif input_str == 'Yes':
                return True
            print("Invalid input")
    else:
        return True

def add_remote_option(parser, help):
    """Add --remote cli option"""
    parser.add_argument('--remote', nargs=2, metavar=('EMAIL', 'URL'), help=help)

def optional_remote(args, default_remote=None):
    """Return remote specified by cli option --remote, or default remote

    Arguments:
        args: argparse args, with attribute `remote`
        override_default: Remote, the default remote to use. If None, uses
            mcapi.Remote(mcapi.Config().default_remote)

    Returns:
        remote: mcapi.Remote
    """
    config = mcapi.Config()
    if args.remote:
        email = args.remote[0]
        url = args.remote[1]

        rconfig = mcapi.RemoteConfig(mcurl=url, email=email)
        if rconfig not in config.remotes:
            print("Could not find remote: {0} {1}".format(rconfig.email, rconfig.mcurl))
            print_remote_help()
            exit(1)

        return mcapi.Remote(config.remotes[config.remotes.index(rconfig)])
    else:

        if default_remote is None:
            if not config.default_remote.mcurl or not config.default_remote.mcapikey:
                print("Default remote not set")
                print("Set the default remote with:")
                print("    mc remote --set-default EMAIL URL")
                print_remote_help()
                exit(1)

            return mcapi.Remote(config.default_remote)
        else:
            return default_remote


def print_remotes(config_remotes, show_apikey=False):
    """Print list of remotes

    Arguments:
        remote_configs: RemoteConfigs, grouped like: {<url>: {<email>: RemoteConfig, ...}, ...}
    """
    if not len(config_remotes):
        print("No remotes")
        return

    from operator import itemgetter
    data = sorted([vars(rconfig) for rconfig in config_remotes], key=itemgetter('mcurl', 'email'))

    columns = ['url', 'email']
    if show_apikey:
        columns.append('apikey')

    def width(col):
        return max([len(str(record[col])) for record in data])

    fmt = [
        ('email', 'email', '<', width('email'), as_is),
        ('mcurl', 'url', '<', width('mcurl'), as_is)
    ]
    if show_apikey:
        fmt.append(('mcapikey', 'apikey', '<', width('mcapikey'), as_is))

    pformatter = PrintFormatter(fmt)

    pformatter.print_header()
    for record in data:
        pformatter.print(record)

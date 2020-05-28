import datetime
import dateutil
import json
import os
import sys
import time

from tabulate import tabulate

from .print_formatter import PrintFormatter, trunc
from .sqltable import SqlTable
from .user_config import Config, RemoteConfig
import materials_commons2.models as models

# TODO: mcapi.Config, mcapi.Remote, mcapi.RemoteConfig

def getit(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    else:
        return getattr(obj, name, default)

def as_is(value):
    return value

def format_time(mtime, fmt="%Y %b %d %H:%M:%S"):
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

def print_table(data, columns=[], headers=[], out=None):
    """Print table from list of dict

    Arguments
    ---------
    data: list of dict, Data to print
    columns: list of str, Keys of data to print, in order
    headers: list of str, Header strings
    out: stream, Output stream
    """
    tabulate_in = []
    if out is None:
        out = sys.stdout
    for record in data:
        tabulate_in.append([record[col] for col in columns])
    out.write(tabulate(tabulate_in, headers=headers))
    out.write('\n')

def print_projects(projects, current=None):
    """
    Print list of projects, include '*' for current project

    Arguments:
        projects: List[materials_commons2.model.Project]
        current: materials_commons2.model.Project containing os.getcwd()
    """
    data = []
    for p in projects:
        _is_current = ' '
        if current is not None and p.uuid == current.uuid:
            _is_current = '*'

        data.append({
            'current': _is_current,
            'name': trunc(p.name, 40),
            'owner': p.owner_id,    # TODO: owner email
            'id': p.id,
            'uuid': p.uuid,
            'mtime': format_time(p.updated_at)
        })

    columns=['current', 'name', 'owner', 'id', 'uuid', 'mtime']
    headers=['', 'name', 'owner', 'id', 'uuid', 'mtime']
    print_table(data, columns=columns, headers=headers)

def print_remote_help():
    print("Add a remote with:")
    print("    mc remote --add EMAIL URL")
    print("List current remotes with:")
    print("    mc remote")
    print("List other known remote urls with:")
    print("    mc remote -l")


def add_remote_option(parser, help):
    """Add --remote cli option"""
    parser.add_argument('--remote', nargs=2, metavar=('EMAIL', 'URL'), help=help)

def optional_remote_config(args):
    """Return RemoteConfig specified by cli option --remote, or default remote

    Arguments:
        args: argparse args, with attribute `remote`

    Returns:
        remote: RemoteConfig
    """
    config = Config()
    if args.remote:
        email = args.remote[0]
        url = args.remote[1]

        remote_config = RemoteConfig(mcurl=url, email=email)
        if remote_config not in config.remotes:
            print("Could not find remote: {0} {1}".format(remote_config.email, remote_config.mcurl))
            print_remote_help()
            exit(1)

        return remote_config
    else:
        if not config.default_remote.mcurl or not config.default_remote.mcapikey:
            print("Default remote not set")
            print("Set the default remote with:")
            print("    mc remote --set-default EMAIL URL")
            print_remote_help()
            exit(1)
        return config.default_remote

def optional_remote(args, default_client=None):
    """Return remote specified by cli option --remote, or default remote

    Arguments:
        args: argparse args, with attribute `remote`
        default_client: mcapi.Client, the default client to use. If None, uses
            `Config().default_remote.make_client()`.

    Returns:
        remote: mcapi.Client
    """
    config = Config()
    if args.remote:
        email = args.remote[0]
        url = args.remote[1]

        remote_config = RemoteConfig(mcurl=url, email=email)
        if remote_config not in config.remotes:
            print("Could not find remote: {0} {1}".format(remote_config.email, remote_config.mcurl))
            print_remote_help()
            exit(1)

        return config.remotes[config.remotes.index(remote_config)].make_client()
    else:

        if default_client is None:
            if not config.default_remote.mcurl or not config.default_remote.mcapikey:
                print("Default remote not set")
                print("Set the default remote with:")
                print("    mc remote --set-default EMAIL URL")
                print_remote_help()
                exit(1)

            return config.default_remote.make_client()
        else:
            return default_client

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

def make_local_project_client(path=None):
    project_config = read_project_config(path)
    if not project_config:
        return None

    config = Config()
    remote_config = project_config.remote
    if remote_config not in config.remotes:
        print("Could not make project Client, failed to find remote config: {0} {1}".format(remote_config.email, remote_config.mcurl))
        print_remote_help()
        exit(1)
    remote_config_with_apikey = config.remotes[config.remotes.index(remote_config)]
    return remote_config_with_apikey.make_client()

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

    project_config = read_project_config(path)

    project_table = ProjectTable(proj_path)
    project_table.connect()
    results = project_table.select_all()
    project_table.close()

    if len(results) > 1:
        raise MCCLIException("project db error: Found >1 project")

    remote = make_local_project_remote(path)
    if not results or not project_config.remote_updatetime or results[0]['checktime'] < project_config.remote_updatetime:
        checktime = time.time()
        try:
            data = post_v3("getProject", {"project_id": project_config.project_id}, remote=remote)['data']
        except requests.exceptions.ConnectionError as e:
            print("Could not connect to " + remote.config.mcurl)
            exit(1)
        except requests.exceptions.HTTPError as e:
            print(e.response.json()['error'])
            exit(1)

        record = {
            'id': project_config.project_id,
            'name': data['name'],
            'data': json.dumps(data),
            'checktime': checktime
        }
        project_table.connect()
        project_table.insert_or_replace(record)
        project_table.close()
    else:
        record = results[0]

    proj = models.Project(data=json.loads(record['data']), remote=remote)
    proj.local_path = proj_path
    return proj

def make_local_expt(proj):
    project_config = read_project_config(proj.local_path)

    if project_config:
        for expt in proj.get_all_experiments():
            if expt.id == project_config.experiment_id:
                return expt

    return None

def current_experiment_id(proj):
    """Return current experiment id, else None"""
    project_config = read_project_config(proj.local_path)
    if project_config:
        return project_config.experiment_id
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
            "project_uuid": <uuid>,
            "experiment_id": <id>,
            "experiment_uuid": <uuid>,
            "remote_updatetime": <number>
        }

    Attributes
    ----------
        project_id: int or None
        project_uuid: str or None
        experiment_id: int or None
        experiment_uuid: str or None
        remote: RemoteConfig
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
            config = Config()
            matching = [remote_config for remote_config in config.remotes if remote_config.mcurl == data['remote_url']]
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

        self.remote = RemoteConfig(**data.get('remote', {}))
        self.project_id = data.get('project_id', None)
        self.project_uuid = data.get('project_uuid', None)
        self.experiment_id = data.get('experiment_id', None)
        self.experiment_uuid = data.get('experiment_uuid', None)
        self.remote_updatetime = data.get('remote_updatetime', None)

    def to_dict(self):
        return {
            'remote': {
                'mcurl': self.remote.mcurl,
                'email': self.remote.email
            },
            'project_id': self.project_id,
            'project_uuid': self.project_uuid,
            'experiment_id': self.experiment_id,
            'experiment_uuid': self.experiment_uuid,
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

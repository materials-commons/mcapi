import requests
import getpass
import os
from os.path import join
import json, subprocess


class NoAPIKey(Exception):
    pass


def mcdatapath():
    user = getpass.getuser()
    return join(os.path.expanduser('~' + user), '.materialscommons')

class Remote(object):
    """
    Attributes:
    -----------
      params: dict
        Holds 'apikey': (string) the user API key value for REST calls
      
      mcurl: str
        Holds base url for Materials Commons instance
      
      config: dict
        All configuration variables, as from environ or '~/.materialscommons/config.json'
        Expected values are:
          'apikey'
          'mcurl'
      
    """
    def __init__(self, config=None):
        """
        Arguments
        -----------
          config: dict, optional 
            Defaults read from environment or '~/.materialscommons/config.json'.
            Possible values are:
              'apikey'
              'mcurl'
            
        """
        
        # get configuration values from 'config.json' or environment variables
        configfile = join(mcdatapath(), 'config.json')
        
        if os.path.exists(configfile):
            with open(configfile, 'r') as f:
                config = json.load(f)
        else:
            raise Exception('No ~/.materialscommons/config.json file found: Run \'mc setup c\'')
        
        self.config = config
        for key in config:
            self.config[key] = os.getenv(key, config[key])
        
        self.mcurl = config['mcurl']
        self.params = {'apikey' : config['apikey']}
    
    def make_url(self, restpath):
        p = self.mcurl + '/' + restpath
        return p
    
    def make_url_v2(self, restpath):
        p = self.mcurl + '/v2/' + restpath
        return p

def disable_warnings():
  """Temporary fix to disable requests' InsecureRequestWarning"""
  from requests.packages.urllib3.exceptions import InsecureRequestWarning
  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Defaults
disable_warnings()
_mcorg = Remote()

def mcorg():
    """
    Default mcapi.Remote().
    
    Returns
    ---------
      mcorg: mcapi.Remote
        Default Materials Commons at 'https://materialscommons.org/api'
    """
    return _mcorg


def mccli():
    """
    Default 'mc' cli application
    
    Returns
    ---------
      mc: str
        The program name "mc"
    """
    return "mc"


def set_cli_remote(remote):
    """
    Set the Remote instance the cli executable is communicating with
    
    Arguments
    -----------
      mc: str
        The cli executable
      
      remote: mcapi.Remote instance
        The Materials Commons instance to use
    
    Returns
    -----------
      For now, just raise an Exception if there is a mismatch.
    """
    #if True: return
    
    child = subprocess.Popen((mccli() + " show config").split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = child.communicate()
    
    if child.returncode:
        raise Exception("Error checking cli remote")
    
    cli_url = out.splitlines()[1].split()[1]
    
    if cli_url != remote.mcurl:
        print "cli:", mc
        print "cli url:", cli_url
        print "remote url:", remote.mcurl
        raise Exception("Error checking cli remote: url mismatch")
    
    

class MCObject(object):
    """
    Base class for Materials Commons objects.
    
    Attributes
    ----------
      id: str
        ID of the object
        
      name: str      
        Name of the object
      
      description: str
        Description of the object
      
      birthtime: int
        Creation time of the object
        
      mtime: int
        Last modification time
        
    """
    def __init__(self, data=dict()):
        attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        for a in attr:
          setattr(self, a, data.get(a,None))    


class CLIResult(object):
    """
    Attributes:
    -----------
      out: str
        stdout from Materials Commons CLI program, mc
      
      out: str
        stdout from Materials Commons CLI program, mc
      
      returncode: int
        return code from calling Materials Commons CLI program, mc
      
    """
    def __init__(self, out, err, returncode):
        self.out = out
        self.err = err
        self.returncode = returncode
    
    def __bool__(self):
        return not self.returncode
    
    __nonzero__ = __bool__
               

def get(restpath, remote=mcorg()):
    r = requests.get(restpath, params=remote.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def post(restpath, data, remote=mcorg()):
    r = requests.post(restpath, params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data, remote=mcorg()):
    r = requests.put(restpath, params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


# Project

def projects(remote=mcorg()):
    """
    Return GET '/projects' data from API
    
    Arguments
    ----------
    remote: mcapi.Remote, optional, default=mcapi.mcorg()
        where to search for Projects. Use 'remote=mcapi.remote' for the 
        projects stored on materialscommons.org.
    
    Returns
    ----------
      results: List[dict()]
        Data from: GET '/projects'
    
    """
    return get(remote.make_url_v2('projects'), remote=remote)


# Datadir

def top(projectid, remote=mcorg()):
    return get(remote.make_url_v2('projects/' + projectid + '/directories'), remote=remote)

def datadir(projectid, datadirid, remote=mcorg()):
    return get(remote.make_url_v2('projects/' + projectid + '/directories/' + datadirid), remote=remote)

def create_datadir(projectid, path, remote=mcorg()):
    data = {'path':path}
    return post(remote.make_url_v2('projects/' + projectid + '/directories'), data, remote=remote)

# Datafile

def datafiles_by_id(projectid, ids, remote=mcorg()):
    basepath = remote.make_url_v2('projects/' + projectid + '/files')
    data = {'file_ids': ids}
    return post(basepath, data, remote=remote)
            
            




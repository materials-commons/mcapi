import requests
import getpass
import os
import json


class NoAPIKey(Exception):
    pass


def mcdatapath():
    user = getpass.getuser()
    return os.path.join(os.path.expanduser('~' + user), '.materialscommons')

class Remote(object):
    """
    Attributes:
    -----------
      params: dict
        Holds 'apikey' value.
      
      baseurl: str
        Holds base url for Materials Commons.
    """
    def __init__(self, baseurl=None, params=None):
        """
        Arguments
        -----------
          params: dict, optional, default read from '~/.mcapikey'
            the 'apikey' value.
          
          baseurl: str, optional, default 'https://materialscommons.org/api/v2'
            the base url for Materials Commons.
        """
        if baseurl is None:
            #baseurl = os.getenv('MCURL', 'https://materialscommons.org/api/v2')
            baseurl = os.getenv('MCURL', 'https://materialscommons.org/api/v2')
        self.baseurl = baseurl
        
        if params is None:
            params = {'apikey': ''}
            user = getpass.getuser()
            mcapi_key_path = os.path.join(os.path.expanduser('~' + user), '.mcapikey')
            if os.path.exists(mcapi_key_path):
                with open(mcapi_key_path, 'r') as fd:
                    userapikey = fd.read()
                    params['apikey'] = userapikey.strip()
        self.params = params
    
    def make_url(self, restpath):
        p = self.baseurl + '/' + restpath
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
        Default Materials Commons at 'https://materialscommons.org/api/v2'
    """
    return _mcorg


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
           

def get(restpath, remote=mcorg()):
    r = requests.get(remote.make_url(restpath), params=remote.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def post(restpath, data, remote=mcorg()):
    r = requests.post(remote.make_url(restpath), params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data, remote=mcorg()):
    r = requests.put(remote.make_url(restpath), params=remote.params, verify=False, json=data)
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
    return get('projects', remote=remote)


# Datadir

def top(projectid, remote=mcorg()):
    return get('projects/' + projectid + '/directories', remote=remote)

def datadir(projectid, datadirid, remote=mcorg()):
    return get('projects/' + projectid + '/directories/' + datadirid, remote=remote)

def create_datadir(projectid, path, remote=mcorg()):
    data = {'path':path}
    return post('projects/' + projectid + '/directories', data, remote=remote)

# Datafile

def datafiles_by_id(projectid, ids, remote=mcorg()):
    basepath = 'projects/' + projectid + '/files'
    data = {'file_ids': ids}
    return post(basepath, data, remote=remote)
            
            




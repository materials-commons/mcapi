import requests
import getpass
import os
import json


class NoAPIKey(Exception):
    pass

params = {'apikey': ''}
baseurl = os.getenv('MCURL', 'https://materialscommons.org/api/v2')

def disable_warnings():
  """Temporary fix to disable requests' InsecureRequestWarning"""
  from requests.packages.urllib3.exceptions import InsecureRequestWarning
  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
        attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type']
        for a in attr:
          setattr(self, a, data.get(a,None))    
           

def init():
    """
    Reads $HOME/.mcapikey
    """
    disable_warnings()
    global params
    user = getpass.getuser()
    mcapi_key_path = os.path.join(os.path.expanduser('~' + user), '.mcapikey')
    if not os.path.exists(mcapi_key_path):
        raise NoAPIKey()
    with open(mcapi_key_path, 'r') as fd:
        userapikey = fd.read()
        params['apikey'] = userapikey.strip()


def get(restpath):
    r = requests.get(make_url(restpath), params=params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def post(restpath, data):
    r = requests.post(make_url(restpath), params=params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data):
    r = requests.put(make_url(restpath), params=params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def make_url(restpath):
    p = baseurl + '/' + restpath
    return p

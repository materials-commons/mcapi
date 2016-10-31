from remote import Remote
import requests

def disable_warnings():
  """Temporary fix to disable requests' InsecureRequestWarning"""
  from requests.packages.urllib3.exceptions import InsecureRequestWarning
  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Defaults
disable_warnings()
_mcorg = Remote()

def mcorg():
    """
    Returns
    ---------
      Default Remote: Materials Commons at 'https://materialscommons.org/api'
    """
    return _mcorg

def get(self, restpath, remote=mcorg()):
    r = requests.get(restpath, params=remote.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()

def post(self, restpath, data, remote=mcorg()):
    r = requests.post(restpath, params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()

def put(self, restpath, data, remote=mcorg()):
    r = requests.put(restpath, params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()





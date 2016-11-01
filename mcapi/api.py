from remote import Remote
import requests

# Defaults
_mcorg = Remote()
_remote = None


def use_remote():
    if (_remote): return _remote
    return mcorg()


def set_remote(remote):
    _remote = remote


def unset_remote():
    _remote = None


def mcorg():
    """
    Returns
    ---------
      Default Remote: Materials Commons at 'https://materialscommons.org/api'
    """
    return _mcorg


def get(restpath, remote=use_remote()):
    r = requests.get(restpath, params=remote.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def post(restpath, data, remote=use_remote()):
    r = requests.post(restpath, params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data, remote=use_remote()):
    r = requests.put(restpath, params=remote.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def disable_warnings():
    """Temporary fix to disable requests' InsecureRequestWarning"""
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


disable_warnings()


# Project

def projects(remote=use_remote()):
    """
    get data for all projects

    Returns
    ----------
      results: List[dict()]

    """
    return get(remote.make_url_v2('projects'), remote=remote)


def create_project(name, description, remote=use_remote()):
    """
    create a project

    Returns
    ----------
      results: dict of 'project_id' and 'datadir_id'

    """
    data = {
        "name": name,
        "description": description
    }
    return post(remote.make_url("/projects"), data)


def cerate_experiment(project_id, name, description, remote=use_remote()):
    """
        create a project

        Returns
        ----------
          results: id of new experiment

        """
    data = {
        "project_id": project_id,
        "name": name,
        "description": description
    }
    return post(remote.make_url("/projects/" + project_id + "/experiments"), data)

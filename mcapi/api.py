from remote import Remote
from config import Config
import requests
import magic

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
    return post(remote.make_url("projects"), data)

def fetch_project(id, remote=use_remote()):
    api_url = "projects/" + id
    return get(remote.make_url_v2(api_url), remote=remote)

# Experiment

def create_experiment(project_id, name, description, remote=use_remote()):
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
    return post(remote.make_url_v2("projects/" + project_id + "/experiments"), data)

# Process

def create_process_from_template(project_id, experiment_id, template_id, remote=use_remote()):
    data = {
        "id" : template_id
    }
    api_url = "projects/" + project_id + \
        "/experiments/" + experiment_id + \
        "/processes/templates/" + template_id
    return post(remote.make_url_v2(api_url), data)

# Sample

def create_samples(project_id, process_id, sample_names, remote=use_remote()):
    sample_names_data = [{"name":name} for name in sample_names]
    data = {
        "process_id" : process_id,
        "samples" : sample_names_data
    }
    api_url = "projects/" + project_id + "/samples"
    return post(remote.make_url_v2(api_url), data)

# Create sample process

def add_samples_to_process(project_id, experiment_id, process, samples, remote=use_remote()):
    samples_data = map((lambda s: {'command': 'add', 'id':s.id, 'property_set_id': s.property_set_id}),samples)
    data = {
        "template_id": process.template_id,
        "process_id": process.id,
        "samples": samples_data
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process.id
    return put(remote.make_url_v2(api_url), data)

# directory

def directory_by_id(project_id, directory_id, remote=use_remote()):
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return get(remote.make_url_v2(api_url))

# file

def file_upload(project_id, directory_id, file_name, input_path, remote=use_remote()):
    with open(input_path, 'rb') as f:
        api_url = "projects/" + project_id + "/directories/" + directory_id +"/fileupload"
        mime_type = magic.Magic(mime=True).from_file(input_path)
        files = {'file': (file_name,f,mime_type)}
        restpath = remote.make_url_v2(api_url)
        r = requests.post(restpath, params=remote.params, files=files)
        if r.status_code == requests.codes.ok:
            return r.json()
        r.raise_for_status()

def file_download(project_id, file_id, output_file_path, remote=use_remote()):

    print("file_download:")
    print("  project_id = " + project_id)
    print("  file_id = " + file_id)
    print("  output_file_path = " + output_file_path)

    with open(output_file_path, 'wb') as f:
        api_url = "projects/" + project_id + "/files/" + file_id + "/download"
        restpath = remote.make_url_v2(api_url)
        print ("  " + restpath)
        r = requests.get(restpath, params=remote.params, stream=True)

        if not r.ok:
            r.raise_for_status()

        for block in r.iter_content(1024):
            f.write(block)

    return output_file_path

def set_remote_config_url(url):
    set_remote(Remote(config=Config(config={'mcurl': url})))

def get_remote_config_url():
    return use_remote().mcurl
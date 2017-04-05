from remote import Remote
from config import Config
import requests
import magic

# Defaults
_mcorg = Remote()
_current_remote = None


def use_remote():
    global _current_remote
    if _current_remote:
        return _current_remote
    return mcorg()


def set_remote(remote):
    global _current_remote
    _current_remote = remote


def unset_remote():
    global _current_remote
    _current_remote = None


def mcorg():
    return _mcorg


def get(restpath, remote=None):
    if not remote:
        remote = use_remote()
    r = requests.get(restpath, params=remote.config.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def post(restpath, data, remote=None):
    if not remote:
        remote = use_remote()
    r = requests.post(restpath, params=remote.config.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data, remote=None):
    if not remote:
        remote = use_remote()
    r = requests.put(restpath, params=remote.config.params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def disable_warnings():
    """Temporary fix to disable requests' InsecureRequestWarning"""
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


disable_warnings()


# Set Config url

def set_remote_config_url(url):
    set_remote(Remote(config=Config(override_config={'mcurl': url})))


def get_remote_config_url():
    return use_remote().config.mcurl


# Project

def projects(remote=None):
    if not remote:
        remote = use_remote()
    """
    get data for all projects

    Returns
    ----------
      results: List[dict()]

    """
    return get(remote.make_url_v2('projects'), remote=remote)


def create_project(name, description, remote=None):
    if not remote:
        remote = use_remote()
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
    return post(remote.make_url_v2("projects"), data)


def fetch_project(project_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id
    return get(remote.make_url_v2(api_url), remote=remote)


def update_project(project_id, name, description, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "name": name,
        "description": description
    }
    return put(remote.make_url_v2("projects/" + project_id), data)


def fetch_project_sample_by_id(project_id, sample_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url), remote=remote)


# Experiment

def create_experiment(project_id, name, description, remote=None):
    if not remote:
        remote = use_remote()
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


def fetch_experiments(project_id, remote=None):
    if not remote:
        remote = use_remote()
    return get(remote.make_url_v2("projects/" + project_id + "/experiments"))


def fetch_experiment_samples(project_id, experiment_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/experiments/" + experiment_id + "/samples"
    return get(remote.make_url_v2(api_url))


def fetch_experiment_processes(project_id, experiment_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id + "/processes"
    return get(remote.make_url_v2(api_url))


# Process

def create_process_from_template(project_id, experiment_id, template_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "id": template_id
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/templates/" + template_id
    return post(remote.make_url_v2(api_url), data)


def push_name_for_process(project_id, process_id, name, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "name": name
    }
    api_url = "projects/" + project_id + "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data)


def fetch_process_by_id(project_id, experiment_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id \
              + "/experiments/" + experiment_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url))


# Sample

def create_samples_in_project(project_id, process_id, sample_names, remote=None):
    if not remote:
        remote = use_remote()
    sample_names_data = [{"name": name} for name in sample_names]
    data = {
        "process_id": process_id,
        "samples": sample_names_data
    }
    api_url = "projects/" + project_id + "/samples"
    return post(remote.make_url_v2(api_url), data)


def add_samples_to_experiment(project_id, experiment_id, sample_id_list, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "samples": sample_id_list
    }
    api_url = "projects/" + project_id + "/experiments/" + experiment_id + "/samples"
    return post(remote.make_url_v2(api_url), data)


def fetch_sample_details(project_id, sample_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url))


# Create sample process

def get_process_from_id(project_id, experiment_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process_id
    return get(remote.make_url_v2(api_url))


def add_samples_to_process(project_id, experiment_id, process, samples, remote=None):
    if not remote:
        remote = use_remote()
    samples_data = map(
        (lambda s: {'command': 'add', 'id': s.id, 'property_set_id': s.property_set_id}),
        samples)
    data = {
        "template_id": process.template_id,
        "process_id": process.id,
        "samples": samples_data
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process.id
    return put(remote.make_url_v2(api_url), data)


# add/update measurements on process samples

def set_measurement_for_process_samples(project_id, experiment_id, process_id,
                                        samples, measurement_property, measurements, remote=None):
    if not remote:
        remote = use_remote()
    request_properties = {
        'property': measurement_property,
        'add_as': 'separate',
        'samples': samples,
        'measurements': measurements,
    }
    data = {
        'process_id': process_id,
        'properties': [request_properties]
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/samples/measurements"
    return post(remote.make_url_v2(api_url), data)


# update process setup values

def update_process_setup_properties(project_id, experiment_id, process, properties, remote=None):
    if not remote:
        remote = use_remote()
    # properties_data = map(
    #    (lambda p: p.__dict__),
    #    properties)
    properties_data = []
    for prop in properties:
        properties_data.append(update_process_setup_properties_make_data(prop))
    data = {
        "template_id": process.template_id,
        "properties": properties_data
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process.id
    index = 0
    while index < len(data["properties"]):
        if not data["properties"][index]["required"]:
            data["properties"][index]["required"] = False
        index += 1
    return put(remote.make_url_v2(api_url), data)


def update_process_setup_properties_make_data(setup_property):
    data = {}
    if not setup_property.required:
        setup_property.required = False
    slot_list = ["attribute", "choices", "description", "name", "required", "unit", "units",
                 "value", "id", "setup_id", "setup_attribute", "otype"]
    for slot in slot_list:
        data[slot] = getattr(setup_property, slot)
    return data


# templates

def get_all_templates(remote=None):
    if not remote:
        remote = use_remote()
    api_url = "templates"
    return get(remote.make_url_v2(api_url))


# directory

def directory_by_id(project_id, directory_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return get(remote.make_url_v2(api_url))


def create_fetch_all_directories_on_path(project_id, directory_id, path, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "from_dir": directory_id,
        "path": path
    }
    api_url = "projects/" + project_id + \
              "/directories/"
    return post(remote.make_url_v2(api_url), data)


def directory_rename(project_id, directory_id, new_name, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'rename': {
            'new_name': new_name
        }
    }
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return put(remote.make_url_v2(api_url), data)


# file

def file_upload(project_id, directory_id, file_name, input_path, remote=None):
    if not remote:
        remote = use_remote()
    with open(input_path, 'rb') as f:
        api_url = "projects/" + project_id + "/directories/" + directory_id + "/fileupload"
        mime_type = magic.Magic(mime=True).from_file(input_path)
        files = {'file': (file_name, f, mime_type)}
        restpath = remote.make_url_v2(api_url)
        r = requests.post(restpath, params=remote.config.params, files=files, verify=False)
        if r.status_code == requests.codes.ok:
            return r.json()
        r.raise_for_status()


def file_download(project_id, file_id, output_file_path, remote=None):
    if not remote:
        remote = use_remote()
    with open(output_file_path, 'wb') as f:
        api_url = "projects/" + project_id + "/files/" + file_id + "/download"
        restpath = remote.make_url_v2(api_url)
        r = requests.get(restpath, params=remote.config.params, stream=True, verify=False)

        if not r.ok:
            r.raise_for_status()

        for block in r.iter_content(1024):
            f.write(block)

    return output_file_path


def add_files_to_process(project_id, experiment_id, process, files, remote=None):
    if not remote:
        remote = use_remote()
    file_id_list = map(
        (lambda f: {'command': 'add', 'id': f.id}),
        files)
    data = {
        "template_id": process.template_id,
        "process_id": process.id,
        "files": file_id_list
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process.id
    return put(remote.make_url_v2(api_url), data)


def file_rename(project_id, file_id, new_file_name, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "name": new_file_name
    }
    api_url = "projects/" + project_id + \
              "/files/" + file_id
    return put(remote.make_url_v2(api_url), data)

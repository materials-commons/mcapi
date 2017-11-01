from collections import OrderedDict
from .remote import Remote
from .config import Config
import requests
import magic
import json

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
    data = OrderedDict(data)
    r = requests.post(
        restpath, params=remote.config.params, verify=False, json=data
    )
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data, remote=None):
    if not remote:
        remote = use_remote()
    r = requests.put(
        restpath, params=remote.config.params, verify=False, json=data
    )
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def delete(restpath, remote=None):
    if not remote:
        remote = use_remote()
    r = requests.delete(restpath, params=remote.config.params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def disable_warnings():
    """Temporary fix to disable requests' InsecureRequestWarning"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


disable_warnings()


# Set Config url

def set_remote_config_url(url):
    """
    Set the base url for the REST query layer, normally taken from
    the user configuration file at ~/.materialscommons/config.json

    :param url: the URL as a string
    :return: None

    >>> mcapi.set_remote_config_url("http://mcdev.localhost/api")

    """
    set_remote(Remote(config=Config(override_config={'mcurl': url})))


def get_remote_config_url():
    """
    The current setting of the url for the REST query layer.

    :return: the URL as a string

    >>> url = mcapi.get_remote_config_url()
    >>> print(url)

    """
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


def get_project_by_id(project_id, remote=None):
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


def get_project_sample_by_id(project_id, sample_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url), remote=remote)


def delete_project(project_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id
    return delete(remote.make_url_v2(api_url))


def get_project_processes(project_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id + "/processes"
    return get(remote.make_url_v2(api_url))


def get_project_samples(project_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id + "/samples"
    return get(remote.make_url_v2(api_url))


def users_with_access_to_project(project_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/access"
    return get(remote.make_url_v2(api_url))


def add_user_access_to_project(project_id, user_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "action": "add",
        "user_id": user_id
    }
    api_url = "projects/" + project_id + "/access"
    return put(remote.make_url_v2(api_url), data)


def remove_user_access_to_project(project_id, user_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "action": "delete",
        "user_id": user_id
    }
    api_url = "projects/" + project_id + "/access"
    return put(remote.make_url_v2(api_url), data)


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


def delete_experiment(project_id, experiment_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id
    return delete(remote.make_url_v2(api_url))


def delete_experiment_fully(project_id, experiment_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id + "/delete/fully"
    return delete(remote.make_url_v2(api_url))


def delete_experiment_dry_run(project_id, experiment_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id + "/delete/dryrun"
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


def delete_process(project_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/processes/" + process_id
    return delete(remote.make_url_v2(api_url))


def set_notes_for_process(project_id, process_id, value, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        "description": value
    }
    api_url = "projects/" + project_id + "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data)


def get_process_by_id(project_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url))


def get_experiment_process_by_id(project_id, experiment_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id \
              + "/experiments/" + experiment_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url))


def delete_sample_created_by_process(project_id, process_id, sample_id, property_set_id, remote=None):
    if not remote:
        remote = use_remote()
    command_list = [{
        "command": "delete",
        "id": sample_id,
        "property_set_id": property_set_id
    }]
    data = {
        "samples": command_list
    }
    api_url = "projects/" + project_id + "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data)


def get_all_files_for_process(project_id, experiment_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id \
              + "/experiments/" + experiment_id \
              + "/processes/" + process_id \
              + "/files"
    return get(remote.make_url_v2(api_url))


# Sample

def get_sample_by_id(project_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url))


def get_experiment_sample_by_id(project_id, experiment_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id \
              + "/experiments/" + experiment_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url))


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


def link_files_to_sample(project_id, sample_id, file_id_list, remote=None):
    if not remote:
        remote = use_remote()
    command_list = []
    for id in file_id_list:
        command_list.append({
            "command": "add",
            "id": id
        })
    data = {
        "files": command_list
    }
    api_url = "projects/" + project_id + "/samples/" + sample_id + "/files"
    return put(remote.make_url_v2(api_url), data)


def fetch_sample_details(project_id, sample_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url))


# Create sample process

def add_samples_to_process(project_id, experiment_id, process, samples, remote=None):
    if not remote:
        remote = use_remote()
    samples_data = [
        {'command': 'add', 'id': s.id, 'property_set_id': s.property_set_id}
        for s in samples]
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


# users
def get_all_users(remote=None):
    if not remote:
        remote = use_remote()
    api_url = "users"
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


def directory_move(project_id, directory_id, new_directory_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'move': {
            'new_directory_id': new_directory_id
        }
    }
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return put(remote.make_url_v2(api_url), data)


def directory_create_subdirectories_from_path_list(project_id, directory_id, path_list, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'paths': path_list
    }
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return post(remote.make_url_v2(api_url), data)


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
    file_id_list = [{'command': 'add', 'id': f.id} for f in files]
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


def file_move(project_id, old_directory_id, new_directory_id, file_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'move': {
            'old_directory_id': old_directory_id,
            'new_directory_id': new_directory_id
        }
    }
    api_url = "projects/" + project_id + \
              "/files/" + file_id
    return put(remote.make_url_v2(api_url), data)


# for testing only - datasets
def create_dataset(project_id, experiment_id, title, description, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'title': title,
        'description': description
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets"
    return post(remote.make_url_v2(api_url), data)


def publish_dataset(project_id, experiment_id, dataset_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {}
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/publish"
    return put(remote.make_url_v2(api_url), data)


def add_process_to_dataset(project_id,
                           experiment_id, dataset_id, process_id, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'processes': [{
            'command': 'add',
            'id': process_id
        }]
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/processes"
    return put(remote.make_url_v2(api_url), data)


# for testing only - comments
def add_comment(item_type, item_id, text, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'item_type': item_type,
        'item_id': item_id,
        'text': text
    }
    api_url = "comments"
    print(remote.make_url_v2(api_url))
    return post(remote.make_url_v2(api_url), data)


def update_comment(comment_id, updated_text, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'text': updated_text
    }
    api_url = "comments/" + comment_id
    return put(remote.make_url_v2(api_url), data)

def delete_comment(comment_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "comments/" + comment_id
    return delete(remote.make_url_v2(api_url))

# for testing only - doi
def check_statue_of_doi_server(project_id,
                               experiment_id, dataset_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doiserverstatus"
    return get(remote.make_url_v2(api_url))


def create_doi(project_id, experiment_id, dataset_id, title,
               description, author, year, remote=None):
    if not remote:
        remote = use_remote()
    data = {
        'title': title,
        'description': description,
        'author': author,
        'publication_year': year
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doi"
    return post(remote.make_url_v2(api_url), data)


def get_doi_metadata(project_id, experiment_id, dataset_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doi"
    return get(remote.make_url_v2(api_url))


def get_doi_link(project_id, experiment_id, dataset_id, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doi/link"
    return get(remote.make_url_v2(api_url))


def _create_new_template(template_data, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "templates/"
    data = template_data
    return post(remote.make_url_v2(api_url), data)


def _update_template(template_id, template_data, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "templates/" + template_id
    data = template_data
    return put(remote.make_url_v2(api_url), data)


#
# ---
#   testing user profile backend
# ---
def _store_in_user_profile(user_id, name, value, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "users/" + user_id + "/profiles/" + name
    data = {
        'value': value
    }
    return put(remote.make_url_v2(api_url), data)


def _get_from_user_profile(user_id, name, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "users/" + user_id + "/profiles/" + name
    return get(remote.make_url_v2(api_url))


def _clear_from_user_profile(user_id, name, remote=None):
    if not remote:
        remote = use_remote()
    api_url = "users/" + user_id + "/profiles/" + name
    return delete(remote.make_url_v2(api_url))

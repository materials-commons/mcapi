from collections import OrderedDict
from .remote import Remote, RemoteWithApikey
from .config import Config
import requests
import magic

# import json

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


def get(restpath, remote):
    r = requests.get(restpath, params=remote.config.get_params(), verify=False)
    r.raise_for_status()
    return r.json()


def post(restpath, data, remote):
    data = OrderedDict(data)
    r = requests.post(
        restpath, params=remote.config.get_params(), verify=False, json=data
    )
    r.raise_for_status()
    return r.json()


def put(restpath, data, remote):
    r = requests.put(
        restpath, params=remote.config.get_params(), verify=False, json=data
    )
    r.raise_for_status()
    return r.json()


def delete(restpath, remote):
    r = requests.delete(restpath, params=remote.config.get_params(), verify=False)
    r.raise_for_status()
    return r.json()


def delete_expect_empty(restpath, remote):
    r = requests.delete(restpath, params=remote.config.get_params(), verify=False)
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

    >>> import materials_commons
    >>> materials_commons.api.set_remote_config_url("http://mcdev.localhost/api")

    """
    set_remote(Remote(config=Config(override_config={'mcurl': url})))


def get_remote_config_url():
    """
    The current setting of the url for the REST query layer.

    :return: the URL as a string

    >>> import materials_commons
    >>> url = materials_commons.api.get_remote_config_url()
    >>> print(url)

    """
    return use_remote().config.mcurl


def configure_remote(remote, apikey):
    if apikey and remote:
        remote = RemoteWithApikey(apikey, config=remote.config)
    elif apikey:
        remote = RemoteWithApikey(apikey)

    if not remote:
        remote = use_remote()

    return remote


# Project

def projects(remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    return get(remote.make_url_v2('projects'), remote)


def create_project(name, description, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "name": name,
        "description": description
    }
    return post(remote.make_url_v2("projects"), data, remote)


def get_project_by_id(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id
    return get(remote.make_url_v2(api_url), remote)


def update_project(project_id, name, description, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "name": name,
        "description": description
    }
    return put(remote.make_url_v2("projects/" + project_id), data, remote)


def get_project_sample_by_id(project_id, sample_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url), remote)


def delete_project(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id
    return delete(remote.make_url_v2(api_url), remote)


def get_project_processes(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id + "/processes"
    return get(remote.make_url_v2(api_url), remote)


def get_project_samples(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id + "/samples"
    return get(remote.make_url_v2(api_url), remote)


def users_with_access_to_project(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + "/access"
    return get(remote.make_url_v2(api_url), remote)


def add_user_access_to_project(project_id, user_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "action": "add",
        "user_id": user_id
    }
    api_url = "projects/" + project_id + "/access"
    return put(remote.make_url_v2(api_url), data, remote)


def remove_user_access_to_project(project_id, user_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "action": "delete",
        "user_id": user_id
    }
    api_url = "projects/" + project_id + "/access"
    return put(remote.make_url_v2(api_url), data, remote)


def create_globus_upload_request(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "project_id": project_id
    }
    api_url = "createGlobusUploadRequest"
    return post(remote.make_url_v4(api_url), data, remote)


def get_globus_upload_status_list(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "project_id": project_id,
    }
    api_url = "etl/globus/upload/status"
    return post(remote.make_url(api_url), data, remote)


def create_globus_download_request(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "project_id": project_id,
    }
    api_url = "etl/globus/transfer/download"
    return post(remote.make_url(api_url), data, remote)


# Experiment
def create_experiment(project_id, name, description, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "project_id": project_id,
        "name": name,
        "description": description
    }
    return post(remote.make_url_v2("projects/" + project_id + "/experiments"), data, remote)


def rename_experiment(project_id, experiment_id, name, description, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "name": name,
        "description": description
    }
    api_url = remote.make_url_v2("projects/" + project_id + "/experiments/" + experiment_id)
    return put(api_url, data, remote)


def fetch_experiments(project_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    return get(remote.make_url_v2("projects/" + project_id + "/experiments"), remote)


def fetch_experiment_samples(project_id, experiment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + "/experiments/" + experiment_id + "/samples"
    return get(remote.make_url_v2(api_url), remote)


def fetch_experiment_processes(project_id, experiment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id + "/processes"
    return get(remote.make_url_v2(api_url), remote)


def delete_experiment(project_id, experiment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id
    return delete(remote.make_url_v2(api_url), remote)


def delete_experiment_fully(project_id, experiment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id + "/delete/fully"
    return delete(remote.make_url_v2(api_url), remote)


def delete_experiment_dry_run(project_id, experiment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "/projects/" + project_id + "/experiments/" + experiment_id + "/delete/dryrun"
    return get(remote.make_url_v2(api_url), remote)


# Process

def create_process_from_template(project_id, experiment_id, template_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "id": template_id
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/templates/" + template_id
    return post(remote.make_url_v2(api_url), data, remote)


def push_name_for_process(project_id, process_id, name, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "name": name
    }
    api_url = "projects/" + project_id + "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data, remote)


def delete_process(project_id, process_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + "/processes/" + process_id
    return delete(remote.make_url_v2(api_url), remote)


def set_notes_for_process(project_id, process_id, value, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "description": value
    }
    api_url = "projects/" + project_id + "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data, remote)


def get_process_by_id(project_id, process_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url), remote)


def get_experiment_process_by_id(project_id, experiment_id, process_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id \
              + "/experiments/" + experiment_id \
              + "/processes/" + process_id
    return get(remote.make_url_v2(api_url), remote)


def delete_sample_created_by_process(project_id, process_id, sample_id, property_set_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    command_list = [{
        "command": "delete",
        "id": sample_id,
        "property_set_id": property_set_id
    }]
    data = {
        "samples": command_list
    }
    api_url = "projects/" + project_id + "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data, remote)


def get_all_files_for_process(project_id, experiment_id, process_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id \
              + "/experiments/" + experiment_id \
              + "/processes/" + process_id \
              + "/files"
    return get(remote.make_url_v2(api_url), remote)


# Sample

def get_sample_by_id(project_id, sample_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id \
              + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url), remote)


def create_samples_in_project(project_id, process_id, sample_names, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    sample_names_data = [{"name": name} for name in sample_names]
    data = {
        "process_id": process_id,
        "samples": sample_names_data
    }
    api_url = "projects/" + project_id + "/samples"
    return post(remote.make_url_v2(api_url), data, remote)


def add_samples_to_experiment(project_id, experiment_id, sample_id_list, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "samples": sample_id_list
    }
    api_url = "projects/" + project_id + "/experiments/" + experiment_id + "/samples"
    return post(remote.make_url_v2(api_url), data, remote)


def link_files_to_sample(project_id, sample_id, file_id_list, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    command_list = []
    for file_id in file_id_list:
        command_list.append({
            "command": "add",
            "id": file_id
        })
    data = {
        "files": command_list
    }
    api_url = "projects/" + project_id + "/samples/" + sample_id + "/files"
    return put(remote.make_url_v2(api_url), data, remote)


def fetch_sample_details(project_id, sample_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + "/samples/" + sample_id
    return get(remote.make_url_v2(api_url), remote)


# Create sample process

def add_samples_to_process(
        project_id, experiment_id, process_id, template_id, sample_id_prop_id_list, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)

    samples_data = []
    for s in sample_id_prop_id_list:
        data_item = {'command': 'add', 'id': s['sample_id'], 'property_set_id': s['property_set_id']}
        if 'transform' in s:
            data_item['transform'] = s['transform']
        samples_data.append(data_item)
    data = {
        "template_id": template_id,
        "process_id": process_id,
        "samples": samples_data
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data, remote)


# add/update measurements on process samples

def set_measurement_for_process_samples(
        project_id, experiment_id, process_id,
        samples, measurement_property, measurements, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
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
    return post(remote.make_url_v2(api_url), data, remote)


# update process setup values

def update_process_setup_properties(project_id, experiment_id, process, properties, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
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
    return put(remote.make_url_v2(api_url), data, remote)


def update_process_setup_properties_make_data(setup_property):
    data = {}
    if not setup_property.required:
        setup_property.required = False
    slot_list = ["attribute", "choices", "description", "name", "required", "unit", "units",
                 "value", "id", "setup_id", "setup_attribute", "otype"]
    for slot in slot_list:
        data[slot] = getattr(setup_property, slot)
    return data


def update_additional_properties_in_process(
        project_id, experiment_id, process_id, properties, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'properties': properties
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process_id + \
              "/addparameters"
    return post(remote.make_url_v2(api_url), data, remote)


# experiment etl metadata

def create_experiment_metadata(experiment_id, json, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'json': json
    }
    api_url = "etl/create/" + experiment_id
    return put(remote.make_url_v2(api_url), data, remote)


def get_experiment_metadata(metadata_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "etl/metadata/" + metadata_id
    return get(remote.make_url_v2(api_url), remote)


def get_experiment_metadata_by_experiment_id(experiment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "etl/experiment/" + experiment_id + \
              "/metadata"
    return get(remote.make_url_v2(api_url), remote)


def update_experiment_metadata(metadata_id, json, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'json': json
    }
    api_url = "etl/metadata/" + metadata_id
    return post(remote.make_url_v2(api_url), data, remote)


def delete_experiment_metadata(metadata_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "etl/metadata/" + metadata_id
    # throws on error
    delete_expect_empty(remote.make_url_v2(api_url), remote)
    return True


# templates

def get_all_templates(remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "templates"
    return get(remote.make_url_v2(api_url), remote)


# users
def get_all_users(remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "users"
    return get(remote.make_url_v2(api_url), remote)


# directory
def directory_by_id(project_id, directory_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return get(remote.make_url_v2(api_url), remote)


def create_fetch_all_directories_on_path(project_id, directory_id, path, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "from_dir": directory_id,
        "path": path
    }
    api_url = "projects/" + project_id + \
              "/directories/"
    return post(remote.make_url_v2(api_url), data, remote)


def directory_rename(project_id, directory_id, new_name, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'rename': {
            'new_name': new_name
        }
    }
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return put(remote.make_url_v2(api_url), data, remote)


def directory_move(project_id, directory_id, new_directory_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'move': {
            'new_directory_id': new_directory_id
        }
    }
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return put(remote.make_url_v2(api_url), data, remote)


def directory_create_subdirectories_from_path_list(project_id, directory_id, path_list, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'paths': path_list
    }
    api_url = "projects/" + project_id + \
              "/directories/" + directory_id
    return post(remote.make_url_v2(api_url), data, remote)


# file

def file_upload(project_id, directory_id, file_name, input_path, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    with open(input_path, 'rb') as f:
        api_url = "projects/" + project_id + "/directories/" + directory_id + "/fileupload"
        mime_type = magic.Magic(mime=True).from_file(input_path)
        files = {'file': (file_name, f, mime_type)}
        restpath = remote.make_url_v2(api_url)
        r = requests.post(restpath, params=remote.config.get_params(), files=files, verify=False)
        if r.status_code == requests.codes.ok:
            return r.json()
        r.raise_for_status()


def file_download(project_id, file_id, output_file_path, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    with open(output_file_path, 'wb') as f:
        api_url = "projects/" + project_id + "/files/" + file_id + "/download"
        restpath = remote.make_url_v2(api_url)
        r = requests.get(restpath, params=remote.config.get_params(), stream=True, verify=False)

        if not r.ok:
            r.raise_for_status()

        for block in r.iter_content(1024):
            f.write(block)

    return output_file_path


def add_files_to_process(
        project_id, experiment_id, process_id, template_id, file_ids,
        direction, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    if not direction:
        direction = ''
    file_id_list = [{'command': 'add', 'id': file_id, 'direction': direction} for file_id in file_ids]
    data = {
        "template_id": template_id,
        "process_id": process_id,
        "files": file_id_list
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/processes/" + process_id
    return put(remote.make_url_v2(api_url), data, remote)


def file_rename(project_id, file_id, new_file_name, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        "name": new_file_name
    }
    api_url = "projects/" + project_id + \
              "/files/" + file_id
    return put(remote.make_url_v2(api_url), data, remote)


def file_move(project_id, old_directory_id, new_directory_id, file_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'move': {
            'old_directory_id': old_directory_id,
            'new_directory_id': new_directory_id
        }
    }
    api_url = "projects/" + project_id + \
              "/files/" + file_id
    return put(remote.make_url_v2(api_url), data, remote)


# for testing only - datasets
def create_dataset(project_id, experiment_id, title, description, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'title': title,
        'description': description
    }
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets"
    return post(remote.make_url_v2(api_url), data, remote)


def publish_dataset(project_id, experiment_id, dataset_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {}
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/publish"
    return put(remote.make_url_v2(api_url), data, remote)


def add_process_to_dataset(
        project_id, experiment_id, dataset_id, process_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
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
    return put(remote.make_url_v2(api_url), data, remote)


# for testing only - comments
def add_comment(item_type, item_id, text, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'item_type': item_type,
        'item_id': item_id,
        'text': text
    }
    api_url = "comments"
    return post(remote.make_url_v2(api_url), data, remote)


def update_comment(comment_id, updated_text, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    data = {
        'text': updated_text
    }
    api_url = "comments/" + comment_id
    return put(remote.make_url_v2(api_url), data, remote)


def delete_comment(comment_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "comments/" + comment_id
    return delete(remote.make_url_v2(api_url), remote)


# for testing only - doi
def check_statue_of_doi_server(project_id,
                               experiment_id, dataset_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doiserverstatus"
    return get(remote.make_url_v2(api_url), remote)


def create_doi(project_id, experiment_id, dataset_id, title,
               description, author, year, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
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
    return post(remote.make_url_v2(api_url), data, remote)


def get_doi_metadata(project_id, experiment_id, dataset_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doi"
    return get(remote.make_url_v2(api_url), remote)


def get_doi_link(project_id, experiment_id, dataset_id, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "projects/" + project_id + \
              "/experiments/" + experiment_id + \
              "/datasets/" + dataset_id + \
              "/doi/link"
    return get(remote.make_url_v2(api_url), remote)


def get_apikey(email, password):
    remote = mcorg()
    api_url = "user/"+email+"/apikey"
    data = {
        "password": password
    }
    u = put(remote.make_url(api_url), data, remote)
    return u["apikey"]


def _create_new_template(template_data, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "templates/"
    data = template_data
    return post(remote.make_url_v2(api_url), data, remote)


def _update_template(template_id, template_data, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "templates/" + template_id
    data = template_data
    return put(remote.make_url_v2(api_url), data, remote)


#
# ---
#   testing user profile backend
# ---
def _store_in_user_profile(user_id, name, value, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "users/" + user_id + "/profiles/" + name
    data = {
        'value': value
    }
    return put(remote.make_url_v2(api_url), data, remote)


def _get_from_user_profile(user_id, name, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "users/" + user_id + "/profiles/" + name
    return get(remote.make_url_v2(api_url), remote)


def _clear_from_user_profile(user_id, name, remote=None, apikey=None):
    remote = configure_remote(remote, apikey)
    api_url = "users/" + user_id + "/profiles/" + name
    return delete(remote.make_url_v2(api_url), remote)

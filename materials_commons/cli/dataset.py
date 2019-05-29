import json
import requests
import sys
from ..api import __api as mc_raw_api
from .list_objects import ListObjects
from .ls import _humanize
from .functions import _trunc, _proj_path, _format_mtime, _proj_config

class Dataset(object):
    def __init__(self):
        pass

def get_all_datasets_from_experiment(expt, remote=None, apikey=None):
    remote = mc_raw_api.configure_remote(remote, apikey)
    api_url = "projects/" + expt.project_id + "/experiments/" + expt.id + "/datasets"
    return mc_raw_api.get(remote.make_url_v2(api_url), remote)

def get_all_datasets_from_project(proj, remote=None, apikey=None):
    remote = mc_raw_api.configure_remote(remote, apikey)
    api_url = remote.make_url_v3("listDatasets")
    params = {'apikey':remote.config.mcapikey, 'project_id':proj.id}
    r = requests.get(api_url, params=params, verify=False)
    r.raise_for_status()
    return r.json()

def get_all_datasets(remote=None, apikey=None):
    remote = mc_raw_api.configure_remote(remote, apikey)
    api_url = "getTopViewedPublishedDatasets"
    return mc_raw_api.get(remote.make_url_v3(api_url), remote)

def download_dataset_zipfile(dataset_id, output_file_path, remote=None, apikey=None):
    remote = mc_raw_api.configure_remote(remote, apikey)
    api_url = remote.make_url_v3("downloadDatasetZipfile")
    params = {'apikey':remote.config.mcapikey, 'dataset_id':dataset_id}

    with open(output_file_path, 'wb') as f:
        r = requests.get(api_url, params=params, verify=False, stream=True)

        if not r.ok:
            r.raise_for_status()

        for block in r.iter_content(8192):
            if block:
                f.write(block)

    return output_file_path


class DatasetSubcommand(ListObjects):
    def __init__(self):
        super(DatasetSubcommand, self).__init__(
            ["dataset"], "Dataset", "Datasets",
            requires_project=False, non_proj_member=True, proj_member=True, expt_member=True,
            list_columns=['name', 'owner', 'id', 'mtime', 'size', 'published'],
            deletable=False,
            custom_selection_actions=['down']
        )

    def get_all_from_experiment(self, expt):
        return get_all_datasets_from_experiment(expt)

    def get_all_from_project(self, proj):
        return get_all_datasets_from_project(proj)['data']

    def get_all(self):
        return get_all_datasets()['data']

    def list_data(self, obj):

        mtime = '-'
        if 'mtime' in obj:
            if 'epoch_time' in obj['mtime']:
                mtime = _format_mtime(obj['mtime']['epoch_time'])

        size = '-'
        if 'zip' in obj:
            if 'size' in obj['zip']:
                size = _humanize(obj['zip']['size'])

        return {
            'name': _trunc(obj.get('title', '-'), 40),
            'owner': _trunc(obj.get('owner', '-'), 40),
            'id': _trunc(obj.get('id', '-'), 40),
            'mtime': mtime,
            'size': size,
            'published': obj.get('published', '-')
        }

    def add_custom_options(self, parser):

        # for --create, add experiment description
        parser.add_argument('--down', action="store_true", default=False, help='Download dataset zipfile')

    def down(self, objects, args, out=sys.stdout):
        for obj in objects:
            out.write("Title: " + obj['title'] + "\n")
            out.write("ID: " + obj['id'] + "\n")
            out.write("Downloading...\n")
            download_dataset_zipfile(obj['id'], obj['id']+".zip")
            out.write("DONE\n\n")
        return

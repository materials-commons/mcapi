import json
import requests
import sys

import materials_commons.api as mcapi
from ..api import __api as mc_raw_api
from materials_commons.cli.list_objects import ListObjects
import materials_commons.cli.functions as clifuncs

def get_all_datasets_from_experiment(project_id, experiment_id, remote=None):
    remote = mc_raw_api.configure_remote(remote, None)
    api_url = "projects/" + project_id + "/experiments/" + experiment_id + "/datasets"
    result = mc_raw_api.get(remote.make_url_v2(api_url), remote)
    for r in result:
        r['name'] = r['title']
    # return result
    return [mcapi.Dataset(d) for d in result]

def get_all_datasets_from_project(project_id, remote=None):
    result = clifuncs.post_v3("listDatasets", {'project_id':project_id}, remote=remote)['data']
    # print(json.dumps(result, indent=2))
    for r in result:
        r['name'] = r['title']
    # return result
    return [mcapi.Dataset(d) for d in result]

def get_all_datasets_from_remote(remote=None):
    result = clifuncs.post_v3("getTopViewedPublishedDatasets", remote=remote)['data']
    for r in result:
        r['name'] = r['title']
    # return result
    return [mcapi.Dataset(d) for d in result]

def download_dataset_zipfile(dataset_id, output_file_path, remote=None):
    remote = mc_raw_api.configure_remote(remote, None)
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

    desc = """List, create, publish, and download datasets. By default lists all public datasets at remote. With `--proj` lists private and public datasets for the current project."""

    def __init__(self):
        super(DatasetSubcommand, self).__init__(
            ["dataset"], "Dataset", "Datasets", desc=self.desc,
            requires_project=False, non_proj_member=True, proj_member=True, expt_member=False,
            remote_help='Remote to get datasets from',
            list_columns=['name', 'owner', 'id', 'mtime', 'zip_size', 'published'],
            deletable=False,
            custom_selection_actions=['down']
        )

    def get_all_from_experiment(self, expt):
        return get_all_datasets_from_experiment(expt.project.id, expt.id, expt.project.remote)

    def get_all_from_project(self, proj):
        return get_all_datasets_from_project(proj.id, proj.remote)

    def get_all_from_remote(self, remote):
        return get_all_datasets_from_remote(remote)

    def list_data(self, obj):

        zip_size = '-'
        if isinstance(obj, dict):
            if 'zip' in obj and 'size' in obj['zip']:
                zip_size = clifuncs.humanize(obj['zip']['size'])
        else:
            if obj.zip_size:
                zip_size = clifuncs.humanize(obj.zip_size)

        published = "no"
        if isinstance(obj, dict):
            if 'published' in obj and obj['published']:
                published = "public"
            if 'is_published_private' in obj and obj['is_published_private']:
                published = "private"
        else:
            if 'published' in obj.input_data and obj.input_data['published']:
                published = "public"
            if 'is_published_private' in obj.input_data and obj.input_data['is_published_private']:
                published = "private"

        return {
            'name': clifuncs.trunc(clifuncs.getit(obj, 'title', '-'), 40),
            'owner': clifuncs.trunc(clifuncs.getit(obj, 'owner', '-'), 40),
            'id': clifuncs.trunc(clifuncs.getit(obj, 'id', '-'), 40),
            'mtime': clifuncs.format_time(clifuncs.getit(obj, 'mtime', '-')),
            'zip_size': zip_size,
            'published': published
        }

    def print_details(self, obj, out=sys.stdout):
        if hasattr(obj, 'pretty_print'):
            obj.pretty_print(shift=0, indent=2, out=out)
        else:
            out.write(json.dumps(obj, indent=2))

    def add_custom_options(self, parser):

        # for --create, add experiment description
        parser.add_argument('--down', action="store_true", default=False, help='Download dataset zipfile')
        # parser.add_argument('--publish-public', action="store_true", default=False, help='Publish public dataset. Makes it available for public download.')
        # parser.add_argument('--publish-private', action="store_true", default=False, help='Publish private dataset. Makes it available for globus download.')
        # parser.add_argument('--unpublish', action="store_true", default=False, help='Download dataset zipfile')

    def down(self, objects, args, out=sys.stdout):
        """Download dataset zipfile, --down

        .. note:: The downloaded dataset is named <dataset_id>.zip
        """
        for obj in objects:
            out.write("Title: " + obj['title'] + "\n")
            out.write("ID: " + obj['id'] + "\n")
            out.write("Downloading...\n")
            download_dataset_zipfile(obj['id'], obj['id']+".zip")
            out.write("DONE\n\n")
        return

    # def publish_public(self, objects, args, out=sys.stdout):
    #     """Public publish dataset
    #
    #     .. note:: The downloaded dataset is named <dataset_id>.zip
    #     """
    #     for obj in objects:
    #         out.write("Title: " + obj['title'] + "\n")
    #         out.write("ID: " + obj['id'] + "\n")
    #         out.write("Publishing for public...\n")
    #         download_dataset_zipfile(obj['id'], obj['id']+".zip")
    #         out.write("DONE\n\n")
    #     return

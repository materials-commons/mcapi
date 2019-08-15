import os
import sys

from . import api
from materials_commons.api.base import MCObject, PrettyPrint, humanize, MCGenericException
from materials_commons.api.Author import Author, print_authors
from materials_commons.api.mc_object_utility import make_object

def input_or_None(prompt):
    value = input(prompt)
    if not value:
        return None
    return value

def _dictget(data, key_list, default_value):
    if len(key_list) == 1:
        return data.get(key_list[0], default_value)
    else:
        if key_list[0] in data:
            return _dictget(data, key_list[1:], default_value)
        else:
            return default_value

class DatasetLicense(object):
    """A Dataset's metadata contains a list of related papers. All attributes are strings."""
    def __init__(self, name=None, link=None):
        self.name = name
        self.link = link

    def __bool__(self):
        return bool(self.name) or bool(self.link)

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if singleline:
            pp.write('{0}. link: {1}'.format(
                pp.str_else(self.name, '<name>'),
                pp.str_else(self.link, '<link>')))
        else:
            pp.write('name: ' + pp.str_or_None(self.name))
            pp.write('link: ' + pp.str_or_None(self.link))

    def to_dict(self):
        return {
            'name': self.name,
            'link': self.link
        }

    def cli_input(self):
        """Prompt for and accept CLI input to set attributes"""

        print('License choices: ')
        print('1: Public Domain Dedication and License (PDDL)')
        print('   Summary: Free to share, create, adapt, without restriction.')
        print('   Link: https://opendatacommons.org/licenses/pddl/summary/')
        print('2: Attribution License (ODC-By)')
        print('   Summary: Free to share, create, adapt, as long as attribution is given.')
        print('   Link: https://opendatacommons.org/licenses/by/summary/')
        print('3: Open Database License (ODC-ODbL)')
        print('   Summary: Free to share, create, adapt, as long as attribution is given, ')
        print('            and if adapted, an open version with the ODC-ODbl license must ')
        print('            be redistributed.')
        print('   Link: https://opendatacommons.org/licenses/odbl/summary/')

        while True:
            choice = int(input('Select a license: '))
            if choice in [1, 2, 3]:
                break
            else:
                print('Invalid selection: ', choice)

        if choice == 1:
            self.name = 'Public Domain Dedication and License (PDDL)'
            self.link = 'https://opendatacommons.org/licenses/pddl/summary/'
        elif choice == 2:
            self.name = 'Attribution License (ODC-By)'
            self.link = 'https://opendatacommons.org/licenses/by/summary/'
        elif choice == 3:
            self.name = 'Open Database License (ODC-ODbL)'
            self.link = 'https://opendatacommons.org/licenses/odbl/summary/'
        else:
            raise MCGenericException('Invalid license choice.')

def print_license(license, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):

    if pp is None:
        pp = PrettyPrint(shift=shift, indent=indent, out=out)

    if not license:
        pp.write("license: None")
        return

    if singleline:
        pp.write("license: ", end='')
        license.pretty_print(shift=shift, indent=indent, out=out, pp=pp, singleline=singleline)
    else:
        pp.write("license: ")
        pp.n_indent += 1
        license.pretty_print(shift=shift, indent=indent, out=out, pp=pp, singleline=singleline)
        pp.n_indent -= 1

class DatasetPaper(object):
    """A Dataset's metadata contains a list of related papers. All attributes are strings."""
    def __init__(self, title=None, authors=None, doi=None, link=None, abstract=None):
        self.title = title
        self.authors = authors
        self.doi = doi
        self.link = link
        self.abstract = abstract

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if singleline:
            pp.write('{0}, {1}. doi: {2} link: {3}'.format(
                pp.str_else(self.authors, '<authors>'),
                pp.str_else(self.title, '<title>'),
                pp.str_else(self.doi, '<doi>'),
                pp.str_else(self.link, '<link>')))
        else:
            pp.write('title: ' + pp.str_or_None(self.title))
            pp.write('authors: ' + pp.str_or_None(self.authors))
            pp.write('doi: ' + pp.str_or_None(self.doi))
            pp.write('link: ' + pp.str_or_None(self.link))
            pp.write('abstract: ' + pp.str_or_None(self.abstract))

    def to_dict(self):
        return {
            'title': self.title,
            'authors': self.authors,
            'doi': self.doi,
            'link': self.link,
            'abstract': self.abstract
        }

    def cli_input(self):
        """Prompt for and accept CLI input to set attributes"""

        self.title = input_or_None('Input paper title: ')
        self.authors = input_or_None('Input paper authors (as single string): ')
        self.doi = input_or_None('Input paper doi: ')
        self.link = input_or_None('Input paper link: ')
        self.abstract = input_or_None('Input paper abstract: ')

def print_papers(papers, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):

    if pp is None:
        pp = PrettyPrint(shift=shift, indent=indent, out=out)

    if not papers:
        pp.write("papers: None")
        return

    pp.write("papers:")
    pp.n_indent += 1
    for index, paper in enumerate(papers):
        if not singleline and index != 0:
            pp.write('')
        paper.pretty_print(shift=shift, indent=indent, out=out, pp=pp, singleline=singleline)
    pp.n_indent -= 1

class DatasetStatus(object):
    """Dataset status

    Arguments
    ---------
    files_count: (int)
    samples_count: (int)
    processes_count: (int)
    can_be_published: (bool)
    """
    def __init__(self, files_count=None, samples_count=None, processes_count=None, can_be_published=None):
        self.files_count = files_count
        self.samples_count = samples_count
        self.processes_count = processes_count
        self.can_be_published = can_be_published

    def __bool__(self):
        return bool(self.files_count) or bool(self.samples_count) or bool(self.processes_count) or bool(self.can_be_published)

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if not bool(self):
            pp.write('status: None')
            return

        pp.write('status:')
        pp.n_indent += 1
        pp.write('files_count: ' + pp.str_else(self.files_count, '?'))
        pp.write('samples_count: ' + pp.str_else(self.samples_count, '?'))
        pp.write('processes_count: ' + pp.str_else(self.processes_count, '?'))
        pp.write('can_be_published: ' + pp.str_else(self.can_be_published, '?'))
        pp.n_indent -= 1

class DatasetZipStatus(object):
    """Dataset zip status

    Arguments
    ---------
    size: (int)
    filename: (str)
    """
    def __init__(self, filename=None, size=None):
        self.filename = filename
        self.size = size


    def __bool__(self):
        return bool(self.size) or bool(self.filename)

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if not bool(self):
            pp.write('zip status: None')
            return

        pp.write('zip status:')
        pp.n_indent += 1
        pp.write('filename: ' + pp.str_else(self.filename, 'None'))
        pp.write('size: ' + pp.str_else(humanize(self.size), 'None'))
        pp.n_indent -= 1

class DatasetStats(object):
    """Dataset stats

    Arguments
    ---------
    unique_view_count: (int)
    comment_count: (int)
    interested_users: (list of str)
    """
    def __init__(self, unique_view_count=None, comment_count=None, interested_users=None):
        if isinstance(unique_view_count, dict):
            if 'total' in unique_view_count:
                unique_view_count = unique_view_count['total']
        self.unique_view_count = unique_view_count
        self.comment_count = comment_count
        if isinstance(interested_users, list):
            interested_users = len(interested_users)
        self.interested_users = interested_users

    def __bool__(self):
        return bool(self.unique_view_count) or bool(self.comment_count) or bool(self.interested_users)

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if not bool(self):
            pp.write('stats: None')
            return

        pp.write('stats:')
        pp.n_indent += 1
        pp.write('unique_view_count: ' + pp.str_else(self.unique_view_count, 'None'))
        pp.write('comment_count: ' + pp.str_else(self.comment_count, 'None'))
        pp.write('interested_users: ' + pp.str_else(self.interested_users, 'None'))
        pp.n_indent -= 1


class Dataset(MCObject):
    """Dataset metadata

    Note
    ----
    Does not contain Dataset "contents": file selection, samples, processes
    """
    def __init__(self, data={}):

        data['name'] = data.get('title', None)

        # list all attributes w/defaults:

        # ** base components **
        #   ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Dataset, self).__init__(data)

        # ** attributes users may change: metadata **

        # str attributes
        self.title = data.get('title', None)
        self.name = self.title
        self.description = data.get('description', None)
        self.funding = data.get('funding', None)
        self.institution = data.get('institution', None)

        # license - object
        self.license = DatasetLicense(**data.get('license', {}))

        # authors
        self.authors = [Author(**d) for d in data.get('authors', [])]

        # papers
        self.papers = [DatasetPaper(**d) for d in data.get('papers', [])]

        # keywords - list of str
        self.keywords = data.get('keywords', [])

        # ** attributes users may change: contents **

        # these can be large, so it might be best if there are separate calls
        # to get/update file selection, samples, and processes

        # self.include_dirs = None
        # self.exclude_dirs = None
        # self.include_files = None
        # self.exclude_files = None
        #
        # self.samples = []
        # self.processes = []

        # ** attributes that cannot be updated by the user **

        self.status = DatasetStatus(**data.get('status', {}))
        self.zip_status = DatasetZipStatus(**data.get('zip', {}))
        self.stats = DatasetStats(**data.get('stats', {}))

        # time attributes
        self.embargo_date = data.get('embargo_date', None)
        self.published_date = data.get('published_date', None)

        # boolean attributes
        self.published = data.get('published', None)
        self.is_published_private = data.get('is_published_private', None)
        self.published_to_globus = data.get('published_to_globus', None)

        # str attributes
        self.doi = data.get('doi', None)
        self.globus_url = data.get('globus_url', None)


    def get_all_samples(self):
        return self.samples

    def get_all_samples(self):
        return self.processes

    def _contains_dir(self, path):
        if path in self.include_dirs:
            return True
        elif path in self.exclude_dirs:
            return False
        else:
            parent = os.path.dirname(path)
            if parent:
                return self._contains_dir(parent)
            else:
                return False

    def contains(self, path):
        if path in self.include_files:
            return True
        elif path in self.excludes_files:
            return False
        else:
            return self._contains_dir(path)

    def pretty_print_metadata(self, shift=0, indent=2, out=sys.stdout, pp=None):

        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        # standard attr
        pp.write("name: " + pp.str_or_None(self.name))
        pp.write("id: " + pp.str(self.id))
        pp.write("doi: " + pp.str_or_None(self.doi))
        pp.write("owner: " + pp.str_or_None(self.owner))
        print_authors(self.authors, pp=pp, singleline=True)
        pp.write("institution: " + pp.str_or_None(self.institution))
        pp.write("funding: " + pp.str_or_None(self.funding))
        print_license(self.license, pp=pp, singleline=True)
        print_papers(self.papers, pp=pp, singleline=True)
        self.status.pretty_print(pp=pp)
        self.zip_status.pretty_print(pp=pp)
        self.stats.pretty_print(pp=pp)

    def pretty_print_description(self, shift=0, indent=2, out=sys.stdout, pp=None):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("description: " + pp.str_or_None(self.description))

    # def pretty_print_file_selection(self, shift=0, indent=2, out=sys.stdout, pp=None):
    #
    #     if pp is None:
    #         pp = PrettyPrint(shift=shift, indent=indent, out=out)
    #
    #     if not self.include_files:
    #         pp.write("include_files: None")
    #     else:
    #         pp.write("include_files:")
    #         pp.n_indent += 1
    #         for file in self.include_files:
    #             pp.write(file)
    #         pp.n_indent -= 1
    #
    #     if not self.exclude_files:
    #         pp.write("exclude_files: None")
    #     else:
    #         pp.write("exclude_files:")
    #         pp.n_indent += 1
    #         for file in self.exclude_files:
    #             pp.write(file)
    #         pp.n_indent -= 1
    #
    #     if not self.include_dirs:
    #         pp.write("include_dirs: None")
    #     else:
    #         pp.write("include_dirs:")
    #         pp.n_indent += 1
    #         for dir in self.include_dirs:
    #             pp.write(dir)
    #         pp.n_indent -= 1
    #
    #     if not self.exclude_dirs:
    #         pp.write("exclude_dir: None")
    #     else:
    #         pp.write("exclude_dirs:")
    #         pp.n_indent += 1
    #         for dir in self.exclude_dirs:
    #             pp.write(dir)
    #         pp.n_indent -= 1
    #
    # def pretty_print_samples(self, shift=0, indent=2, out=sys.stdout, pp=None):
    #
    #     if pp is None:
    #         pp = PrettyPrint(shift=shift, indent=indent, out=out)
    #
    #     pp.write("samples:")
    #     pp.n_indent += 1
    #     for samp in self.samples:
    #         pp.write(samp.name + ', ' + samp.id)
    #     pp.n_indent -= 1
    #
    # def pretty_print_processes(self, shift=0, indent=2, out=sys.stdout, pp=None):
    #
    #     if pp is None:
    #         pp = PrettyPrint(shift=shift, indent=indent, out=out)
    #
    #     pp.write("processes:")
    #     pp.n_indent += 1
    #     for proc in self.processes:
    #         pp.write(proc.name + ', ' + proc.id)
    #     pp.n_indent -= 1

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None):
        """
        Prints a nice layout of the object and all of it's values.

        :param shift: the offset from the start of the line, in increments of indent
        :param indent: the indent used for layout, in characters
        :param out: the stream to which the object in printed
        :param pp: PrettyPrint object to use. If None, constructed from other arguments.
        :return: None
        """
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)
        self.pretty_print_metadata(pp=pp)
        self.pretty_print_description(pp=pp)


def get_all_datasets_from_experiment(project_id, experiment_id, remote=None):
    remote = api.configure_remote(remote, None)
    api_url = "projects/" + project_id + "/experiments/" + experiment_id + "/datasets"
    result = mc_raw_api.get(remote.make_url_v2(api_url), remote)
    for r in result:
        r['name'] = r['title']
    # return result
    return [Dataset(d) for d in result]

def get_all_datasets_from_project(project_id, remote=None):
    result = api.post_v3("listDatasets", {'project_id':project_id}, remote=remote)['data']
    # print(json.dumps(result, indent=2))
    for r in result:
        r['name'] = r['title']
    # return result
    return [Dataset(d) for d in result]

def get_all_datasets_from_remote(remote=None):
    result = api.post_v3("getTopViewedPublishedDatasets", remote=remote)['data']
    for r in result:
        r['name'] = r['title']
    # return result
    return [Dataset(d) for d in result]

def download_dataset_zipfile(dataset_id, output_file_path, remote=None):
    remote = api.configure_remote(remote, None)
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

def get_dataset(project_id, dataset_id, remote=None):
    result = api.post_v3(
        "getDataset",
        {
            'project_id': project_id,
            'dataset_id': dataset_id
        },
        remote=remote)['data']
    return Dataset(result)

def create_dataset(project_id, title, description="", sample_ids=[], file_selection=None, remote=None):
    if file_selection is None:
        file_selection = {
            'include_dirs': [],
            'exclude_dirs': [],
            'include_files': [],
            'exclude_files': []
        }
    result = api.post_v3(
        "createDataset",
        {
            'project_id': project_id,
            'title': title,
            'description': description,
            'samples': sample_ids
        },
        remote=remote)['data']
    return Dataset(result)

def _check_file_selection_dirs(path, file_selection, orig_path=None):
    if path == orig_path:
        selected_by = "(self)"
    else:
        selected_by = path
    if path in file_selection['include_dirs']:
        return (True, selected_by)
    elif path in file_selection['exclude_dirs']:
        return (False, selected_by)
    else:
        parent = os.path.dirname(path)
        if parent:
            return _check_file_selection_dirs(parent, file_selection, orig_path=orig_path)
        else:
            return (False, None)

def check_file_selection(path, file_selection):
    """Check if a file or directory is included/excluded/neither in a file_selection, and why

    :returns: (selected, selected_by)
        selected: True if included, False otherwise
        selected_by: One of "(self)" if included/excluded explicitly, <path> if included/explicitly by a higher level directory, None if selected==None
    """
    if path in file_selection['include_files']:
        return (True, "(self)")
    elif path in file_selection['exclude_files']:
        return (False, "(self)")
    else:
        return _check_file_selection_dirs(path, file_selection, orig_path=path)


def update_dataset_file_selection(project_id, dataset_id, file_selection, remote=None):
    """
    :param project_id: str, Project ID
    :param dataset_id: str, Dataset ID
    :param file_selection: dict,
        Format:
            file_selection = {
                'include_dirs': [<list of included dirs>],
                'exclude_dirs': [<list of excluded dirs>],
                'include_files': [<list of included files>],
                'exclude_files': [<list of excluded files>]
            }
    """
    result = api.post_v3(
        "updateDatasetFileSelection",
        {
            'project_id': project_id,
            'dataset_id': dataset_id,
            'file_selection': file_selection
        },
        remote=remote)['data']
    return Dataset(result)

def add_samples_to_dataset(project_id, dataset_id, sample_ids, remote=None):
    result = api.post_v3(
        "addDatasetSamples",
        {
            'project_id': project_id,
            'dataset_id': dataset_id,
            'samples': sample_ids
        },
        remote=remote)['data']
    return Dataset(result)

def remove_samples_from_dataset(project_id, dataset_id, sample_ids, remote=None):
    result = api.post_v3(
        "deleteDatasetSamples",
        {
            'project_id': project_id,
            'dataset_id': dataset_id,
            'samples': sample_ids
        },
        remote=remote)['data']
    return Dataset(result)

def remove_processes_from_dataset(project_id, dataset_id, process_ids, remote=None):
    import json, requests
    result = api.post_v3(
        "deleteProcessesFromDatasetSample",
        {
            'project_id': project_id,
            'dataset_id': dataset_id,
            'processes': process_ids
        },
        remote=remote)['data']
    return Dataset(result)


def delete_dataset(project_id, dataset_id, remote=None):
    result = api.post_v3(
        "deleteDataset",
        {
            'project_id': project_id,
            'dataset_id': dataset_id
        },
        remote=remote)['data']
    return result['success']

def unpublish_dataset(project_id, dataset_id, remote=None):
    """Unpublish a dataset

    Returns
    -------
    dataset: mcapi.Dataset
    """
    result = api.post_v3(
        "unpublishDataset",
        {
            'project_id': project_id,
            'dataset_id': dataset_id
        },
        remote=remote)
    if 'data' in result:
        # unpublish a private dataset
        return Dataset(result['data'])
    else:
        # unpublish a public dataset
        return

def publish_dataset(project_id, dataset_id, remote=None):
    """Publish a dataset

    Returns
    -------
    dataset: mcapi.Dataset
    """
    result = api.post_v3(
        "publishDataset",
        {
            'project_id': project_id,
            'dataset_id': dataset_id
        },
        remote=remote)
    return Dataset(result['data'])

def publish_private_dataset(project_id, dataset_id, remote=None):
    result = api.post_v3(
        "publishPrivateDataset",
        {
            'project_id': project_id,
            'dataset_id': dataset_id
        },
        remote=remote)
    return Dataset(result['data'])

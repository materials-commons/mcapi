from materials_commons.api import mc_object_utility
from datetime import datetime


class Dataset:

    def __init__(self, data=None):
        if not data:
            data = {}

        self.raw_data = data

        # ignore keywords, tags, papers - empty in example but most likely strings
        # ignore other datasets - self-included and not useful at this point
        attr = ['authors', 'birthtime', 'description', 'doi', 'embargo_date', 'files',
                'funding', 'id', 'institution', 'license', 'mtime',
                'owner', 'papers', 'processes', 'published', 'published_date', 'publisher',
                'samples', 'title', 'zip'
                # , 'papers', 'tags', 'keywords', 'other_datasets'
                ]
        for a in attr:
            setattr(self, a, data.get(a, None))

        # Convert "objects"
        self.authors = [DatasetAuthor(data=data) for data in self.authors]
        self.files = [convert_file(file) for file in self.files]
        self.processes = [convert_process(process) for process in self.processes]
        self.samples = [convert_sample(sample) for sample in self.samples]
        self.zip = DatasetZip(self.zip)
        self.license = DatasetLicense(self.license)
        if self.embargo_date:
            self.embargo_date = convert_string_date_time(self.embargo_date)
        self.birthtime = convert_string_date_time(self.birthtime)
        self.mtime = convert_string_date_time(self.mtime)
        self.published_date = convert_string_date_time(self.published_date)


class DatasetAuthor:

    def __init__(self, data):
        self.firstname = data['firstname']
        self.lastname = data['lastname']
        self.affiliation = data['affiliation']

    def __str__(self):
        return self.lastname + ', ' + self.firstname + "(" + self.affiliation + ")"


class DatasetZip:
    def __init__(self, data):
        self.filename = data['filename']
        self.size = data['size']


class DatasetLicense:
    def __init__(self, data):
        self.link = data['link']
        self.name = data['name']


def convert_file(file):
    # in example, found file without either '_type' or 'otype'!!
    file['otype'] = 'datafile'
    return mc_object_utility.make_mc_file(file)


def convert_process(process):
    return mc_object_utility.make_mc_process(process)


def convert_sample(sample):
    return mc_object_utility.make_mc_sample(sample)


def convert_string_date_time(dt):
    # '2016-07-30T02:32:20.140Z'
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')

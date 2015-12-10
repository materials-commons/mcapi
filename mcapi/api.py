import requests
import getpass
import os
import json


class NoAPIKey(Exception):
    pass


params = {'apikey': ''}
baseurl = os.getenv('MCURL', 'https://materialscommons.org/api/v2')


class Sample(object):
    def __init__(self, project_id, name, manufacturer):
        self.project_id = project_id
        self.name = name
        self.description = ''
        self.manufacturer = manufacturer


class Process(object):
    def __init__(self, project_id, process_type, process_name, name):
        self.project_id = project_id
        self._type = process_type
        self.process_name = process_name
        self.name = name
        self.description = ''
        self.does_transform = False
        self.input_files = []
        self.output_files = []
        self.input_samples = []
        self.output_samples = []
        self.owner = ''
        self.setup = {
            'files': [],
            'settings': []
        }
        self.transformed_samples = []
        self.what = ''
        self.why = ''


def init():
    global params
    user = getpass.getuser()
    mcapi_key_path = os.path.join(os.path.expanduser('~' + user), '.mcapikey')
    if not os.path.exists(mcapi_key_path):
        raise NoAPIKey()
    with open(mcapi_key_path, 'r') as fd:
        userapikey = fd.read()
        params['apikey'] = userapikey.strip()


def get_projects():
    return api_get('projects')


def create_sample(sample):
    p = Process(sample.project_id, 'as_received', 'As Received', 'As Received')
    p.output_samples.append({'name': sample.name})
    if sample.manufacturer != '':
        p.setup['settings'].append({
            'attribute': 'instrument',
            'name': 'Instrument',
            'properties': [
                {
                    'property': {
                        '_type': 'string',
                        'attribute': 'manufacturer',
                        'name': 'Manufacturer',
                        'description': '',
                        'unit': '',
                        'value': sample.manufacturer
                    }
                }
            ]
        })
    return api_post('projects/' + sample.project_id + '/processes', p.__dict__)


def api_get(restpath):
    r = requests.get(make_api_url(restpath), params=params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def api_post(restpath, data):
    r = requests.post(make_api_url(restpath), params=params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def make_api_url(restpath):
    p = baseurl + '/' + restpath
    return p

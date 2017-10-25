import requests
from .dataset import Dataset


class Public:

    default_base_url = "https://materialscommons.org/"
    path_for_dataset_id = 'api/pub/datasets/'

    def __init__(self, base_url=None):
        if not base_url:
            base_url = Public.default_base_url
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    def make_url(self, rest):
        return self.base_url + rest

    def get_dataset(self, id):
        r = requests.get(self.make_url(Public.path_for_dataset_id + id), verify=False)
        if r.status_code == requests.codes.ok:
            return Dataset(data=r.json())
        r.raise_for_status()


def disable_warnings():
    """Temporary fix to disable requests' InsecureRequestWarning"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#    from requests.packages.urllib3.exceptions import InsecureRequestWarning
#    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


disable_warnings()

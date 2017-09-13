import requests

class Public():

    default_base_url = "https://materialscommons.org/"
    path_for_dateaset_id = 'api/pub/datasets/'

    def __init__(self, base_url=None):
        if not base_url:
            base_url = Public.default_base_url
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    def make_url(self,rest):
        return self.base_url + rest

    def get_dataset(self, id):
        return requests.get(self.make_url(Public.path_for_dateaset_id + id), verify=False)

def disable_warnings():
    """Temporary fix to disable requests' InsecureRequestWarning"""
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


disable_warnings()

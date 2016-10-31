import requests
from mcapi.config import Config

class Remote(object):
    """
    Attributes:
    -----------
      params: dict
        Holds 'apikey': (string) the user API key value for REST calls

      mcurl: str
        Holds base url for Materials Commons instance

      config: dict
        All configuration variables, as from environ or '~/.materialscommons/config.json'
        Expected values are:
          'apikey'
          'mcurl'

    """

    def __init__(self, config=Config()):
        """
        Arguments
        -----------
          config: dict, optional
            Defaults read from environment or '~/.materialscommons/config.json'.
            Possible values are:
              'apikey'
              'mcurl'

        """

        if ((not config.mcurl) or (not config.mcapikey)):
            raise Exception("Remote not properly configured: mcapikey and mculr are reguired")

        self.config = config
        self.mcurl = config.mcurl

    def make_url(self, restpath):
        p = self.mcurl + '/' + restpath
        return p

    def make_url_v2(self, restpath):
        p = self.mcurl + '/v2/' + restpath
        return p

    def get(self,restpath, remote=mcorg()):
        r = requests.get(restpath, params=remote.params, verify=False)
        if r.status_code == requests.codes.ok:
            return r.json()
        r.raise_for_status()


    def post(self,restpath, data, remote=mcorg()):
        r = requests.post(restpath, params=remote.params, verify=False, json=data)
        if r.status_code == requests.codes.ok:
            return r.json()
        r.raise_for_status()


    def put(self,restpath, data, remote=mcorg()):
        r = requests.put(restpath, params=remote.params, verify=False, json=data)
        if r.status_code == requests.codes.ok:
            return r.json()
        r.raise_for_status()

# Defaults
_mcorg = Remote()

def mcorg(self):
    """
    Default mcapi.Remote().

    Returns
    ---------
      mcorg: mcapi.Remote
        Default Materials Commons at 'https://materialscommons.org/api'
    """
    return self._mcorg

def _disable_warnings():
    """Temporary fix to disable requests' InsecureRequestWarning"""
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

_disable_warnings()

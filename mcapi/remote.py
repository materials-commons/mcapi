import requests
from config import Config

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

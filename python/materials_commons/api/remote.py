from .config import Config
from .base import MCConfigurationException


class Remote(object):
    def __init__(self, config=Config()):
        if not config.mcurl:
            raise MCConfigurationException(
                "Remote not properly configured: mcurl is required")

        self.config = config

    def make_url_v2(self, restpath):
        p = self.config.mcurl + '/v2/' + restpath
        return p

    def make_url_v4(self, restpath):
        p = self.config.mcurl + '/v4/' + restpath
        return p

    def make_url(self, restpath):
        p = self.config.mcurl + "/" + restpath
        return p


class RemoteWithApikey(Remote):
    def __init__(self, apikey, config=Config()):
        if not config.mcurl:
            raise Exception("Remote not properly configured: mcurl is required")

        config.mcapikey = apikey
        self.config = config

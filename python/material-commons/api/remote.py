from .config import Config


class Remote(object):
    def __init__(self, config=Config()):
        if (not config.mcurl) or (not config.mcapikey):
            raise Exception("Remote not properly configured: mcapikey and mcurl are required")

        self.config = config
        # self.mcurl = config.mcurl
        # self.params = config.params

    def make_url_v2(self, restpath):
        p = self.config.mcurl + '/v2/' + restpath
        return p

    def make_url(self, restpath):
        p = self.config.mcurl + "/" + restpath
        return p

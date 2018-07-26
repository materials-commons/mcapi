import getpass
import os
import warnings
from os.path import join
import json
from .base import MCConfigurationException


class Config(object):

    def __init__(self, config_file_path=None, config_file_name="config.json", override_config=None):
        if not override_config:
            override_config = {}
        if not config_file_path:
            user = getpass.getuser()
            config_file_path = join(os.path.expanduser('~' + user), '.materialscommons')
        config_file = join(config_file_path, config_file_name)

        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {
                'apikey': None,
                'mcurl': None
            }

        env_apikey = os.environ.get("MC_API_KEY")
        env_mcurl = os.environ.get("MC_API_URL")

        if env_apikey:
            config['apikey'] = env_apikey
        if env_mcurl:
            config['mcurl'] = env_mcurl

        self.config = config
        for key in config:
            self.config[key] = os.getenv(key, config[key])

        for key in override_config:
            self.config[key] = override_config[key]

        self.mcapikey = self.config['apikey']
        self.mcurl = self.config['mcurl']

        message = None
        if not self.mcurl:
            message = "Python API, Configuration Exception, env variables: " \
                      + "You must set MC_API_URL"
            raise MCConfigurationException(message)

        if not self.mcapikey:
            message = "Python API, Configuration Warning, env variables: " \
                      + "The apikey in MC_API_KEY is not set; assuming it is set in all calls"
            warnings.warn(message, UserWarning)

        # 'interfaces': [
        #   { 'name': 'casm',
        #     'desc':'Create CASM samples, processes, measurements, etc.',
        #     'subcommand':'casm_subcommand',
        #     'module':'casm_mcapi'
        #   },
        #   {
        #     'name': 'other':...
        #   }
        # }
        self.interfaces = config.get('interfaces', dict())

    def get_params(self):
        return {'apikey': self.mcapikey}

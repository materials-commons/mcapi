import getpass
import os
from os.path import join
import json

class Config(object):

    def __init__(self,config_file_path=None, config_file_name="config.json", config={}):
        if (not config_file_path):
            user = getpass.getuser()
            config_file_path = join(os.path.expanduser('~' + user), '.materialscommons')
        path = join(config_file_path,config_file_name)
        config_file = join(config_file_path, 'config.json')

        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            raise Exception('No config file found, " + config_file + ": Run \'mc setup c\'')

        self.config = config
        for key in config:
            self.config[key] = os.getenv(key, config[key])

        self.mcurl = config['mcurl']
        self.params = {'apikey': config['apikey']}

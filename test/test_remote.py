import unittest
from os.path import exists
from mcapi import Config
from mcapi import Remote

class TestRemote(unittest.TestCase):

    def setup(self):
        test_data_dir = "test/test_config_data/"
        if (not exists(test_data_dir)):
            Exception("No test data for TestRemote. Can not find directory: " + test_data_dir);

    def test_default_remote(self):
        remote = Remote()
        config = remote.config
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)
        self.assertEqual(remote.mcurl,config.mcurl);

    def test_with_config_settings(self):
        config = Config(config_file_path="test/test_config_data/", config_file_name="config.json")
        remote = Remote(config=config)


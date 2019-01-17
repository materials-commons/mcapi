import unittest
from os.path import exists
from os import environ, path
from materials_commons.api import _Config as Config
from materials_commons.api import _Remote as Remote


class TestRemote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_data_dir = "test/test_config_data/"
        if not exists(test_data_dir):
            Exception("No test data for TestRemote. Can not find directory: " + test_data_dir)

    def test_default_remote(self):
        remote = Remote()
        config = remote.config
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)
        self.assertEqual(remote.config.mcurl, config.mcurl)

    def test_with_config_settings(self):
        test_path = "test/path/for/config"
        config = Config(config_file_path=self.make_test_dir_path(), config_file_name="config.json")
        remote = Remote(config=config)
        self.assertIsNotNone(remote.make_url_v2(test_path))
        self.assertTrue(config.mcurl in remote.make_url_v2(test_path))
        self.assertTrue(test_path in remote.make_url_v2(test_path))

    def make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_dir = path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_dir)
        self.assertTrue(path.isdir(test_dir))
        test_dir = path.join(test_dir, 'test_config_data')
        self.assertTrue(path.isdir(test_dir))
        return test_dir

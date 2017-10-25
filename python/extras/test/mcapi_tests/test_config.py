import unittest
from os import environ, path
from materials_commons.api import _Config as Config


class TestConfig(unittest.TestCase):

    def test_default_config(self):
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)

    def test_path_settings(self):
        config = Config(config_file_path=self.make_test_dir_path(), config_file_name="config.json")
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)
        self.assertEqual(config.params['apikey'], "12345678901234567890123456789012")
        self.assertEqual(config.mcurl, "http://not.mcdev.localhost/api")

    def make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_dir = path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_dir)
        self.assertTrue(path.isdir(test_dir))
        test_dir = path.join(test_dir, 'test_config_data')
        self.assertTrue(path.isdir(test_dir))
        return test_dir

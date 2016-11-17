import unittest
from os import environ, path
from mcapi import Config


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
        self.assertEqual(config.mcurl, "http://mctest.localhost/api")

    def make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(path.abspath(environ['TEST_DATA_DIR']))
        self.assertTrue(path.isdir(path.abspath(environ['TEST_DATA_DIR'])))
        test_dir = path.abspath(environ['TEST_DATA_DIR'])
        test_dir = path.join(test_dir,'test_config_data')
        self.assertTrue(path.isdir(test_dir))
        return test_dir
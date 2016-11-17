import unittest
from os import environ
from mcapi import Config


class TestConfig(unittest.TestCase):

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)

    def test_default_config(self):
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)

    def test_path_settings(self):
        test_dir = environ['TEST_DATA_DIR']
        if not test_dir.endswith('/'):
            test_dir += '/'
        config = Config(config_file_path=test_dir + "test_config_data/", config_file_name="config.json")
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)
        self.assertEqual(config.params['apikey'], "12345678901234567890123456789012")
        self.assertEqual(config.mcurl, "http://mctest.localhost/api")


import unittest
from mcapi import Config


class TestConfig(unittest.TestCase):

    def test_default_config(self):
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)

    def test_path_settings(self):
        config = Config(config_file_path="test/test_config_data/", config_file_name="config.json")
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.params)
        self.assertIsNotNone(config.params['apikey'])
        self.assertIsNotNone(config.mcurl)
        self.assertEqual(config.params['apikey'], "12345678901234567890123456789012")
        self.assertEqual(config.mcurl, "http://mctest.localhost/api")

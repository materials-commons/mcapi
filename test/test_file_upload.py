import unittest
from random import randint
from pathlib import Path
from mcapi import set_remote_config_url, get_remote_config_url #, ping

url = 'http://mctest.localhost/api'

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestProject(unittest.TestCase):
    def setup(self):
        set_remote_config_url(url)
        self.filepath = 'test/test_config_data/fractal.jpg'

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url,url)
        self.assertTrue(Path(self.filepath).is_file())

#    def test_apikey_and_site(self):
#        self.assertTrue(ping())


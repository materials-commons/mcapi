import unittest
from random import randint
from mcapi import set_remote_config_url, get_remote_config_url

url = 'http://mctest.localhost/api'

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestDirectory(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        set_remote_config_url(url)

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url(), url)



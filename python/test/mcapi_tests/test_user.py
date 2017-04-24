import unittest
import pytest
from random import randint
from mcapi import set_remote_config_url, get_remote_config_url, get_all_templates

url = 'http://mctest.localhost/api'

class TestTemplateAccess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)



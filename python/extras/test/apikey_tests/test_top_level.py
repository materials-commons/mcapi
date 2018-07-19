import unittest
from random import randint
# from unittest import mock


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestTopLevel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"

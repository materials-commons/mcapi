import unittest
from random import randint
from mcapi import set_remote_config_url, get_remote_config_url
from mcapi import _storeInUserProfile as storeInUserProfile
from mcapi import _getFromUserProfile as getFromUserProfile
from mcapi import _clearFromUserProfile as clearFromUserProfile


url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


user_id = "test@test.mc"


class TestUserProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url(), url)

    def test_can_store_value(self):
        name = fake_name("test value - ")
        value = name
        probe = storeInUserProfile(user_id,name, value)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = storeInUserProfile(user_id, name, value)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = getFromUserProfile(user_id,name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = clearFromUserProfile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = clearFromUserProfile(user_id, name)
        self.assertIsNone(probe)
        probe = getFromUserProfile(user_id, name)
        self.assertIsNone(probe)

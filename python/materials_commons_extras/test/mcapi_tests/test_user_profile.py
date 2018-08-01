import unittest
import pytest
from random import randint
from materials_commons.api import set_remote_config_url, get_remote_config_url
from materials_commons.api import _store_in_user_profile
from materials_commons.api import _get_from_user_profile
from materials_commons.api import _clear_from_user_profile


url = 'http://mcdev.localhost/api'


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
        probe = _store_in_user_profile(user_id, name, value)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _store_in_user_profile(user_id, name, value)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _get_from_user_profile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _clear_from_user_profile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _clear_from_user_profile(user_id, name)
        self.assertIsNone(probe)
        probe = _get_from_user_profile(user_id, name)
        self.assertIsNone(probe)

    def test_cannot_access_others_profile(self):
        name = fake_name("test value - ")
        value = name
        probe = _store_in_user_profile(user_id, name, value)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _get_from_user_profile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)

        another_user_id = "another@test.mc"
        with pytest.raises(Exception):
            _get_from_user_profile(another_user_id, name)

        probe = _clear_from_user_profile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _get_from_user_profile(user_id, name)
        self.assertIsNone(probe)

    def test_cannot_modify_others_profile(self):
        name = fake_name("test value - ")
        value = name
        probe = _store_in_user_profile(user_id, name, value)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _get_from_user_profile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)

        another_user_id = "another@test.mc"
        with pytest.raises(Exception):
            _store_in_user_profile(another_user_id, name, value)

        probe = _clear_from_user_profile(user_id, name)
        self.assertIsNotNone(probe)
        self.assertEqual(probe, name)
        probe = _get_from_user_profile(user_id, name)
        self.assertIsNone(probe)

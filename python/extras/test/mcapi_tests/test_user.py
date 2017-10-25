import unittest
import pytest
from materials_commons.api import get_all_users


class TestUser(unittest.TestCase):

    def test_get_all(self):

        my_id = "test@test.mc"
        me = None
        user_list = get_all_users()

        for user in user_list:
            if user.id == my_id:
                me = user
        self.assertIsNotNone(me)
        self.assertEqual(me.fullname, "Test User One")

        another_id = "another@test.mc"
        another = None
        for user in user_list:
            if user.id == another_id:
                another = user
        self.assertIsNotNone(another)
        self.assertEqual(another.fullname, "Test User Two")

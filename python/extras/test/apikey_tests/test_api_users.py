import unittest
from materials_commons.api import api


class TestUserRaw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"

    def test_get_all_users_raw(self):
        results = api.get_all_users(apikey=self.apikey)
        user_list = results['val']
        found = None
        for user in user_list:
            if user['id'] == self.user:
                found = user
        self.assertIsNotNone(found)

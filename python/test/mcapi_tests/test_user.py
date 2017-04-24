import unittest
from mcapi import set_remote_config_url, get_all_users

url = 'http://mctest.localhost/api'

class TestTemplateAccess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)

    def test_get_all(self):
        my_id = "test@test.mc"
        me = None
        user_list = get_all_users()

        print user_list

        for user in user_list:
            if (user.id == my_id):
                me = user
        self.assertIsNotNome(me)
        self.assertEqual(me.fullname,"Test User1")
        self.assertEqual(me.affiliation,"")

        another_id = "another@test.mc"
        another = None
        for user in user_list:
            if (user.id == another_id):
                another = user
        self.assertIsNotNome(another)
        self.assertEqual(another.fullname,"Test User2")
        self.assertEqual(another.affiliation,"")

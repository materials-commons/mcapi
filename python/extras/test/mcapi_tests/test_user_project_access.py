import unittest
from random import randint
from mcapi import create_project


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestUserProjectAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(" -- ")
        cls.project_name = fake_name("TestProject-")
        print(cls.project_name)
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description)
        cls.project_id = cls.project.id

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.project.name)
        self.assertEqual(self.project_name, self.project.name)
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_id, self.project.id)

    def test_project_owner_has_access_list(self):
        owner = self.project.owner
        access_list = self.project.get_access_list()
        self.assertTrue(owner in access_list)

    def test_add_user_to_access_list(self):
        another_user = "another@test.mc"
        added_user = self.project.add_user_to_access_list(another_user)
        self.assertIsNotNone(added_user)
        self.assertEqual(another_user, added_user)
        all_users = self.project.get_access_list()
        count = 0
        for user_id in all_users:
            if user_id == another_user:
                count += 1
        self.assertEqual(count, 1)

    def test_no_add_of_invalid_user(self):
        invalid_user = "This-is-not-a-User"
        message = self.project.add_user_to_access_list(invalid_user)
        self.assertIsNotNone(message)
        self.assertNotEqual(message, invalid_user)
        self.assertTrue("invalid" in message)

    def test_adding_twice_valid_user_ok(self):
        another_user = "another@test.mc"
        added_user = self.project.add_user_to_access_list(another_user)
        self.assertIsNotNone(added_user)
        self.assertEqual(another_user, added_user)
        another_user = "another@test.mc"
        added_user = self.project.add_user_to_access_list(another_user)
        self.assertIsNotNone(added_user)
        self.assertEqual(another_user, added_user)
        all_users = self.project.get_access_list()
        count = 0
        for user_id in all_users:
            if user_id == another_user:
                count += 1
        self.assertEqual(count, 1)

    def test_remove_user_from_access_list(self):
        another_user = "another@test.mc"
        added_user = self.project.add_user_to_access_list(another_user)
        self.assertIsNotNone(added_user)
        self.assertEqual(another_user, added_user)
        all_users = self.project.get_access_list()
        count = 0
        for user_id in all_users:
            if user_id == another_user:
                count += 1
        self.assertEqual(count, 1)
        removed_user = self.project.remove_user_from_access_list(another_user)
        self.assertEqual(another_user, removed_user)
        all_users = self.project.get_access_list()
        count = 0
        for user_id in all_users:
            if user_id == another_user:
                count += 1
        self.assertEqual(count, 0)

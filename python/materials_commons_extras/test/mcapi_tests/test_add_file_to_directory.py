import unittest
from random import randint
from os import environ
from os import path as os_path
from os.path import getsize
from pathlib import Path
from materials_commons.api import create_project


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestAddFileToDirectory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_name = fake_name("Project - ")
        cls.project_description = "Test project, " + cls.project_name
        cls.testDirPath = "/testDir1/testdir2/testdir3"
        cls.project = create_project(
            name=cls.project_name,
            description=cls.project_description)

        cls.rootDir = cls.project.get_top_directory()
        cls.testDir = cls.project.add_directory(cls.testDirPath)

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_name, self.project.name)
        self.assertEqual(self.project_description, self.project.description)
        path1 = "/" + self.testDir.name.split("/", 1)[1]
        path2 = self.testDirPath
        if path2.endswith("/"):
            path2 = path2[:-1]
        self.assertEqual(path1, path2)

    def test_add_file_to_project_root(self):
        path = Path(self.make_test_dir_path('fractal.jpg'))
        file_name = path.parts[-1]
        input_path = str(path.absolute())
        byte_count = getsize(input_path)

        added_file = self.project.add_file_using_directory(self.rootDir, file_name, input_path)
        self.assertIsNotNone(added_file)
        self.assertEqual(added_file.size, byte_count)
        found = None
        descendants = self.rootDir.get_children()
        for one in descendants:
            if (one.otype == 'file') and (one.name == file_name):
                found = one
        self.assertIsNotNone(found)
        self.assertEqual(found.size, byte_count)
        self.assertEqual(added_file.id, found.id)

        added_file = self.project.add_file_using_directory(self.testDir, file_name, input_path)
        self.assertIsNotNone(added_file)
        self.assertEqual(added_file.size, byte_count)
        found = None
        descendants = self.testDir.get_children()
        for one in descendants:
            if (one.otype == 'file') and (one.name == file_name):
                found = one
        self.assertIsNotNone(found)
        self.assertEqual(found.size, byte_count)
        self.assertEqual(added_file.id, found.id)

    def test_add_file_to_directory(self):
        dir_path = "/add/file/to_directory/test"

        path = Path(self.make_test_dir_path('fractal.jpg'))
        file_name = path.parts[-1]
        input_path = str(path.absolute())
        byte_count = getsize(input_path)

        directory = self.project.add_directory(dir_path)
        added_file = directory.add_file(file_name, input_path)

        self.assertIsNotNone(added_file)
        self.assertEqual(added_file.size, byte_count)

    def make_test_dir_path(self, file_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        self.assertTrue(os_path.isfile(test_file))
        return test_file

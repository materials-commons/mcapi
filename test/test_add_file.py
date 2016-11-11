import unittest
from random import randint
from os.path import getsize
from pathlib import Path
from mcapi import create_project, Template
from mcapi import create_file_with_upload

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestFileInProject(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.project_name = fake_name("Project - ")
        self.project_description = "Test project, " + self.project_name
        self.filepath = 'test/test_upload_data/fractal.jpg'

        self.rootDirPath = "/"
        self.testDirPath = "/testDir"

        self.project = create_project(
            name = self.project_name,
            description = self.project_description)

    @unittest.skip("")
    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_name,self.project.name)
        self.assertEqual(self.project_description,self.project.description)

    @unittest.skip("")
    def test_add_file_to_project_root(self):

        path = Path(self.filepath)
        file_name = path.parts[-1]
        input_path = str(path.absolute())
        byte_count = getsize(input_path)

        file = self.project.add_file(self.rootDirPath, file_name, input_path)

        self.assertIsNotNone(file)
        self.assertEqual(file.size, byte_count)

        # dir = self.project.get_dir(self.rootDirPath)
        # file1 = dir.get_file(file_name)

        # self.assertIsNotNone(file1)
        # self.assertEqual(file1.size, byte_count)
        # self.assertEqual(file1, file)

        # file2 = self.project.get_file(self.rootDirPath, file_name)

        # self.assertIsNotNone(file2)
        # self.assertEqual(file2.size, byte_count)
        # self.assertEqual(file2, file)

        # file3 = self.project.add_file(self.rootDirPath, file_name, input_path)

        # self.assertIsNotNone(file3)
        # self.assertEqual(file3.size, byte_count)
        # self.assertEqual(file3, file)

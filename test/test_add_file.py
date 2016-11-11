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

        self.testDirPath = "/testDir1/testdir2/testdir3"

        self.project = create_project(
            name = self.project_name,
            description = self.project_description)

        self.rootDir = self.project.get_top_directory()
        self.testDir = self.project.add_directory(self.testDirPath)

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_name,self.project.name)
        self.assertEqual(self.project_description,self.project.description)
        path1 = "/" + self.testDir.name.split("/", 1)[1]
        path2 = self.testDirPath
        if path2.endswith("/"): path2 = path2[:-1]
        self.assertEqual(path1, path2);

    def test_add_file_to_project_root(self):
        path = Path(self.filepath)
        file_name = path.parts[-1]
        input_path = str(path.absolute())
        byte_count = getsize(input_path)

        file = self.project.add_file_using_directory(self.rootDir, file_name, input_path)
        self.assertIsNotNone(file)
        self.assertEqual(file.size, byte_count)

        file = self.project.add_file_using_directory(self.testDir, file_name, input_path)
        self.assertIsNotNone(file)
        self.assertEqual(file.size, byte_count)


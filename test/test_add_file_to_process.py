import unittest
from random import randint
from os.path import getsize
from pathlib import Path
from mcapi import create_project, Template


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number


class TestFileInProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_name = fake_name("Project - ")
        cls.project_description = "Test project, " + cls.project_name
        cls.experiment_name = fake_name("Experiment-")
        cls.experiment_description = "a test experiment generated from api"
        cls.filepath = 'test/test_upload_data/fractal.jpg'
        cls.test_dir_path = "/testDir1/testdir2/testdir3"
        cls.filename = "test.jpg"

        cls.project = create_project(
            name = cls.project_name,
            description = cls.project_description)

        experiment = cls.project.create_experiment(
            name = cls.experiment_name,
            description = cls.experiment_description)

        cls.process = experiment.create_process_from_template(Template.create)

        cls.test_dir = cls.project.add_directory(cls.test_dir_path)
        cls.file = cls.project.add_file_using_directory(
            cls.test_dir, cls.filename, cls.filepath)

        path = Path(cls.filepath)
        cls.file_name = path.parts[-1]
        input_path = str(path.absolute())
        cls.byte_count = getsize(input_path)

        cls.file = cls.project.add_file_using_directory(cls.test_dir, cls.file_name, input_path)

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_name, self.project.name)
        self.assertEqual(self.project_description, self.project.description)

        path1 = "/" + self.test_dir.name.split("/", 1)[1]
        path2 = self.test_dir_path
        if path2.endswith("/"):
            path2 = path2[:-1]
        self.assertEqual(path1, path2)

        self.assertIsNotNone(self.process.process_type)
        self.assertEqual(self.process.process_type, 'create')
        self.assertTrue(self.process.does_transform)

        test_file = self.file
        byte_count = self.byte_count
        self.assertIsNotNone(test_file)
        self.assertEqual(test_file.size, byte_count)
        found = None
        decendents = self.test_dir.get_children()
        for one in decendents:
            if (one._type == 'file') and (one.name == self.file_name):
                found = one
        self.assertIsNotNone(found)
        self.assertEqual(found.size, byte_count)
        self.assertEqual(test_file.id, found.id)

    @unittest.skip("not working yet")
    def test_add_file_to_process(self):
        files1 = [self.file]
        self.assertIsNotNone(files1)
        self.assertEqual(len(files1), 1)
        file1 = files1[0]
        self.assertIsNotNone(file1)
        self.assertIsNotNone(file1.id)

        files2 = self.process.add_files(files1)
        self.assertIsNotNone(files2)
        self.assertEqual(len(files2), 1)
        file2 = files2[0]
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file2.id)

        self.assertEqual(file1.id, file2.id)

        files2 = self.process.get_files()
        self.assertIsNotNone(files2)
        self.assertEqual(len(files2), 1)
        file2 = files2[0]
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file2.id)

        self.assertEqual(file1.id, file2.id)

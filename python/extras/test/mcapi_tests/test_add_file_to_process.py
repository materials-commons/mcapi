import unittest
from random import randint
from os import environ
from os import path as os_path
from os.path import getsize
from pathlib import Path as PathClass
from materials_commons.api import create_project, Template


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestAddFileToProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_name = "Test file Project"
        cls.project_description = "A test Project generated from api"
        cls.experiment_name = fake_name("Experiment-")
        cls.experiment_description = "A test Experiment generated from api"
        cls.test_dir_path = "/testDir1/testdir2/testdir3"
        cls.filename = "test.jpg"

        cls.project = create_project(
            name=cls.project_name,
            description=cls.project_description)

        cls.experiment = cls.project.create_experiment(
            name=cls.experiment_name,
            description=cls.experiment_description)

        cls.process = cls.experiment.create_process_from_template(Template.create)

    def test_is_setup_correctly(self):
        self.setup_each_test()
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_name, self.project.name)
        self.assertTrue(self.project_description in self.project.description)

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
        decendants = self.test_dir.get_children()
        for one in decendants:
            if (one.otype == 'file') and (one.name == self.file_name):
                found = one
        self.assertIsNotNone(found)
        self.assertEqual(found.size, byte_count)
        self.assertEqual(test_file.id, found.id)

    def test_add_file_to_process(self):
        self.setup_each_test()
        files1 = [self.file]
        self.assertIsNotNone(files1)
        self.assertEqual(len(files1), 1)
        file1 = files1[0]
        self.assertIsNotNone(file1)
        self.assertIsNotNone(file1.id)

        process = self.process.add_files(files1)
        files = self.process.get_all_files()
        process.files = files
        self.assertIsNotNone(process.files)
        self.assertEqual(len(process.files), 1)
        file2 = process.files[0]
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file2.id)

        self.assertEqual(file1.id, file2.id)

        process = self.experiment.get_process_by_id(self.process.id)
        files = self.process.get_all_files()
        process.files = files
        self.assertIsNotNone(process.files)
        self.assertEqual(len(process.files), 1)
        file2 = process.files[0]
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file2.id)

        self.assertEqual(file1.id, file2.id)

    def make_test_dir_path(self, file_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        self.assertTrue(os_path.isfile(test_file))
        return test_file

    def setup_each_test(self):
        if not hasattr(self, 'filepath'):
            self.filepath = self.make_test_dir_path('fractal.jpg')
            self.test_dir = self.project.add_directory(self.test_dir_path)
            self.file = self.project.add_file_using_directory(
                self.test_dir, self.filename, self.filepath)

            file_path = PathClass(self.filepath)
            self.file_name = file_path.parts[-1]
            input_path = str(file_path.absolute())
            self.byte_count = getsize(input_path)

            self.file = self.project.add_file_using_directory(self.test_dir, self.file_name, input_path)

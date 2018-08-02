import unittest
from os import environ
from os import path as os_path
from os.path import getsize
from pathlib import Path
from materials_commons.api import create_project


class TestFileUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_project_name = "FileUploadTest01"
        description = "Test project generated by automated test"
        project = create_project(cls.base_project_name, description)
        cls.base_project_id = project.id
        cls.base_project = project

    def test_is_setup_correctly(self):
        self.setup_test_file()

        project = self.base_project
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.name)
        self.assertEqual(self.base_project_name, project.name)
        self.assertIsNotNone(project.id)
        self.assertEqual(self.base_project_id, project.id)

        directory = project.get_top_directory()
        self.assertEqual(directory._project, self.base_project)

    def test_upload1(self):
        self.setup_test_file()
        project = self.base_project
        directory = project.get_top_directory()

        path = Path(self.filepath1)
        file_name = path.parts[-1]
        input_path = str(path.absolute())
        byte_count = getsize(input_path)
        test_file = project.add_file_using_directory(directory, file_name, input_path)
        self.assertIsNotNone(test_file)
        self.assertEqual(test_file.size, byte_count)

    def test_upload2(self):
        self.setup_test_file()
        project = self.base_project
        directory = project.get_top_directory()

        path = Path(self.filepath2)
        file_name = path.parts[-1]
        input_path = str(path.absolute())
        byte_count = getsize(input_path)
        file1 = project.add_file_using_directory(directory, file_name, input_path)
        self.assertIsNotNone(file1)
        self.assertEqual(file1.size, byte_count)
        self.assertEqual(file1.name, file_name)

        # redundant calls work - return equivalent descriptor
        file2 = project.add_file_using_directory(directory, file_name, input_path)
        self.assertIsNotNone(file2)
        self.assertEqual(file1.size, file2.size)
        self.assertEqual(file1.name, file2.name)

    def make_test_dir_path(self, file_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        self.assertTrue(os_path.isfile(test_file))
        return test_file

    def setup_test_file(self):
        if not hasattr(self, 'filepath1'):
            self.filepath1 = self.make_test_dir_path('fractal.jpg')
            self.filepath2 = self.make_test_dir_path('sem.tif')
            self.assertTrue(Path(self.filepath1).is_file())
            self.assertTrue(Path(self.filepath2).is_file())
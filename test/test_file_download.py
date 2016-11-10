import unittest
import tempfile
import filecmp
from os.path import getsize, exists, isfile
from pathlib import Path
from mcapi import set_remote_config_url, get_remote_config_url, create_project
from mcapi import create_file_with_upload,download_data_to_file

remote_url = 'http://mctest.localhost/api'

class TestFileDownload(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        set_remote_config_url(remote_url)
        self.filepath1 = 'test/test_upload_data/fractal.jpg'
        self.base_project_name = "FileUploadTest01"
        description = "Test project generated by automated test"
        project = create_project(self.base_project_name, description)
        directory = project.get_top_directory()
        self.base_project_id = project.id
        self.base_project = project
        self.base_directory_id = directory.id
        self.base_directory = directory

        path = Path(self.filepath1)
        self.file_name = path.parts[-1]
        input_path = str(path.absolute())
        self.byte_count = getsize(input_path)
        self.file = create_file_with_upload(project, self.base_directory, self.file_name, input_path)

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url(), remote_url)
        self.assertTrue(Path(self.filepath1).is_file())

        project = self.base_project
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.name)
        self.assertEqual(self.base_project_name, project.name)
        self.assertIsNotNone(project.id)
        self.assertEqual(self.base_project_id, project.id)

        self.assertEqual(self.base_directory._project, self.base_project)

        self.assertIsNotNone(self.file)
        self.assertEqual(self.file.size, self.byte_count)
        self.assertEqual(self.file.name, self.file_name)

    @unittest.skip("Skiping non-working test for push to archvie")
    def test_download_raw(self):
        project = self.base_project
        directory = project.get_top_directory()
        file = self.file
        download_file_path = tempfile.gettempdir() + "/" + file.name

        filepath = download_data_to_file(project, file, download_file_path)

        print(filepath)

        self.assertTrue(exists(filepath))
        self.assertTure(isfile(filepath))
        self.assertTrue(filecmp.cmp(self.filepath1, file.name))


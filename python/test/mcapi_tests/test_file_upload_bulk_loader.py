import unittest
from random import randint
from os import environ
from os import path as os_path
from os import walk

from mcapi import set_remote_config_url, get_remote_config_url
from mcapi import create_project
from mcapi import BulkFileUploader

url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestBulkUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.upload_dir_path = None
        if 'TEST_DATA_DIR' in environ:
            test_dir_path = os_path.abspath(environ['TEST_DATA_DIR'])
            cls.upload_dir_path = os_path.join(test_dir_path, 'test_upload_data')
        cls.upload_dir = 'test_upload_dir'

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.upload_dir_path)
        self.assertTrue(os_path.isdir(self.upload_dir_path))
        self.assertTrue(os_path.isdir(os_path.join(self.upload_dir_path,self.upload_dir)))

        self.assertEqual(get_remote_config_url(), url)

    def test_upload_sequential(self):
        print '--'
        project_name = fake_name("TestRenameProject-")
        print project_name
        description = "Test project generated by automated test"
        project = create_project(project_name, description)

        self.assertIsNotNone(project)
        self.assertIsNotNone(project.id)
        self.assertIsNotNone(project.name)
        self.assertEqual(project_name, project.name)

        project.local_path = self.upload_dir_path
        local_path = os_path.join(project.local_path,self.upload_dir)

        parallel = False
        verbose = False
        limit = 1
        # buik loader with very small limit to test for upload failure and shorten test length
        loader = BulkFileUploader(parallel = parallel, limit = limit, verbose = verbose)
        missed_files = loader.bulk_upload(project,local_path)

        expected_missed_files = self.find_big_files(local_path,limit)
        self.assertEqual(len(missed_files),len(expected_missed_files))

        for i in range(0,len(expected_missed_files)):
            self.assertEqual(expected_missed_files[i],missed_files[i])

    def test_upload_parallel(self):
        print '--'
        project_name = fake_name("TestRenameProject-")
        print project_name
        description = "Test project generated by automated test"
        project = create_project(project_name, description)

        self.assertIsNotNone(project)
        self.assertIsNotNone(project.id)
        self.assertIsNotNone(project.name)
        self.assertEqual(project_name, project.name)

        project.local_path = self.upload_dir_path
        local_path = os_path.join(project.local_path,self.upload_dir)

        parallel = True
        verbose = False
        limit = 1
        # buik loader with very small limit to test for upload failure and shorten test length
        loader = BulkFileUploader(parallel = parallel, limit = limit, verbose = verbose)
        missed_files = loader.bulk_upload(project,local_path)

        expected_missed_files = self.find_big_files(local_path,limit)
        if (len(missed_files) > 2):
            print missed_files
        self.assertEqual(len(missed_files),len(expected_missed_files))

        for i in range(0,len(expected_missed_files)):
            self.assertTrue(expected_missed_files[i] in missed_files)

    def find_big_files(self,local_path,limit):
        collect = []
        for (dirpath, dirnames, filenames) in walk(local_path):
            for name in filenames:
                probe = os_path.join(dirpath, name)
                file_size_MB = os_path.getsize(probe) >> 20
                if file_size_MB > limit:
                    collect.append(probe)
        return collect
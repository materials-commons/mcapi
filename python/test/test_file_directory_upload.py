import unittest
from random import randint
from os import environ
from os import path as os_path
from os import listdir
from os.path import getsize
from pathlib import Path
from mcapi import set_remote_config_url, get_remote_config_url, create_project
from mcapi import _create_file_with_upload

url = 'http://mctest.localhost/api'

def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number

class TestFileDirectoryUpload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.base_project_name = "DirectoryUploadTest01"
        description = "Test project generated by automated test"
        project = create_project(cls.base_project_name, description)
        cls.base_project_id = project.id
        cls.base_project = project
        cls.top_dir = 'TestUploadDir'

    def test_is_setup_correctly(self):
        self.setup_test_directory_table()

        self.assertTrue(hasattr(self, 'testdir_table'))
        self.assertIsNotNone(self.testdir_table)
        relitive_path = list(self.testdir_table.keys())[0]
        self.assertIsNotNone(self.testdir_table[relitive_path])
        file_name = list(self.testdir_table[relitive_path].keys())[0]
        absolute_local_path = self.testdir_table[relitive_path][file_name]
        self.assertTrue(Path(absolute_local_path).is_file())

        self.assertEqual(get_remote_config_url(), url)

        project = self.base_project
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.name)
        self.assertEqual(self.base_project_name, project.name)
        self.assertIsNotNone(project.id)
        self.assertEqual(self.base_project_id, project.id)

        directory = project.get_top_directory()
        self.assertEqual(directory._project, self.base_project)

    def test_upload_one_file_by_dir(self):
        self.setup_test_directory_table()
        self.assertIsNotNone(self.testdir_table)
        relitive_path = list(self.testdir_table.keys())[0]
        self.assertIsNotNone(self.testdir_table[relitive_path])
        file_name = list(self.testdir_table[relitive_path].keys())[0]
        absolute_local_path = self.testdir_table[relitive_path][file_name]
        self.assertTrue(Path(absolute_local_path).is_file())

        directory_name = fake_name("test_dir")

        project = self.base_project
        top_directory = project.get_top_directory()
        self.assertEqual(top_directory._project, project)

        dir_list = top_directory.get_descendant_list_by_path(directory_name)
        base_directory = dir_list[0]
        self.assertEqual(base_directory._project, project)

        dir_list = base_directory.get_descendant_list_by_path(relitive_path)
        directory = dir_list[0]
        self.assertEqual(directory._project, project)

        file = _create_file_with_upload(project, directory, file_name, absolute_local_path)

        byte_count = getsize(absolute_local_path)

        self.assertIsNotNone(file)
        self.assertEqual(file.size, byte_count)
        self.assertEqual(file.name, file_name)

    def test_upload_recursive_dir(self):
        directory_name = fake_name("test_dir")

        project = self.base_project
        top_directory = project.get_top_directory()
        self.assertEqual(top_directory._project, project)

        dir_list = top_directory.get_descendant_list_by_path(directory_name)
        base_directory = dir_list[0]
        self.assertEqual(base_directory._project, project)

        base_directory.upload_all_tree(self.test_data_dir,self.top_dir);

    def setup_test_directory_table(self):
        if not hasattr(self, 'testdir_table'):
            self.testdir_table = self.make_testdir_table(self.top_dir)

    def make_testdir_table(self, dir_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'test_upload_data')
        self.assertTrue(os_path.isdir(test_path))
        return self.make_testdir_table_helper(test_path,dir_name,dir_name,{})

    def make_testdir_table_helper(self,test_path,dir_name,relitive_base,table_so_far):
        top_path = os_path.join(test_path, dir_name)
        self.assertTrue(os_path.isdir(test_path))
        file_dictionary = {}
        for file in listdir(top_path):
            path = os_path.join(top_path, file)
            if (os_path.isfile(path)):
                file_dictionary[file] = path
        if file_dictionary:
            table_so_far[relitive_base] = file_dictionary
        for dir in listdir(top_path):
            path = os_path.join(top_path, dir)
            base = os_path.join(relitive_base,dir)
            if (os_path.isdir(path)):
                table_so_far = self.make_testdir_table_helper(top_path,dir,base,table_so_far)
        return table_so_far


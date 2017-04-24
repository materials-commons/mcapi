import unittest
from random import randint
from os import environ
from os import path as os_path
from os import listdir
from os import makedirs
from os.path import getsize
from mcapi import set_remote_config_url, get_remote_config_url, create_project
from mcapi import make_dir_tree_table

url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestFileDirectoryUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.base_project_name = fake_name("DirectoryUploadTest")
        description = "Test project generated by automated test"
        project = create_project(cls.base_project_name, description)
        cls.base_project_id = project.id
        cls.base_project = project
        cls.single_file_dir_path = "test_upload_dir/sub_directory_a"
        cls.path_of_empty_dir = "test_upload_dir/sub_directory_c/empty_dir"
        cls.full_dir = 'test_upload_dir'

    def test_is_setup_correctly(self):
        path = self.setup_test_directory_path(self.single_file_dir_path)
        self.assertTrue(os_path.isdir(path))

        path = self.setup_test_directory_path(self.full_dir)
        self.assertTrue(os_path.isdir(path))

        self.fix_empty_dir_if_needed()
        path = self.setup_test_directory_path(self.path_of_empty_dir)
        self.assertTrue(os_path.isdir(path))

        self.assertEqual(get_remote_config_url(), url)

        project = self.base_project
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.name)
        self.assertEqual(self.base_project_name, project.name)
        self.assertIsNotNone(project.id)
        self.assertEqual(self.base_project_id, project.id)

        directory = project.get_top_directory()
        self.assertEqual(directory._project, self.base_project)

    def test_upload_one_file_by_path(self):
        directory_name = fake_name("test_one_dir")

        project = self.base_project
        top_directory = project.get_top_directory()
        self.assertEqual(top_directory._project, project)

        dir_list = top_directory.get_descendant_list_by_path(directory_name)
        base_directory = dir_list[0]
        self.assertEqual(base_directory._project, project)

        relative_path = self.single_file_dir_path

        dir_list = base_directory.get_descendant_list_by_path(relative_path)
        directory = dir_list[-1]
        self.assertEqual(directory._project, project)

        local_dir_path = self.setup_test_directory_path(self.single_file_dir_path)

        file_name = listdir(local_dir_path)[0]

        path = os_path.join(local_dir_path, file_name)
        self.assertTrue(os_path.isfile(path))

        test_file = directory.add_file(file_name, path)
        self.assertIsNotNone(test_file)
        self.assertEqual(test_file.name, file_name)
        byte_count = getsize(path)
        self.assertEqual(test_file.size, byte_count)

    def test_upload_files_by_dir(self):
        directory_name = fake_name("test_two_dir")

        project = self.base_project
        top_directory = project.get_top_directory()
        self.assertEqual(top_directory._project, project)

        dir_list = top_directory.get_descendant_list_by_path(directory_name)
        base_directory = dir_list[0]
        self.assertEqual(base_directory._project, project)

        local_dir_path = self.setup_test_directory_path(self.full_dir)
        self.assertTrue(os_path.isdir(local_dir_path))

        relative_path = "test_dir"

        dir_tree_table = make_dir_tree_table(local_dir_path, "sub_directory_b", relative_path, {})
        self.assertEqual(dir_tree_table.keys()[0], relative_path)

        file_dict = dir_tree_table[relative_path]
        self.assertEqual(len(file_dict.keys()), 2)

        dir_list = base_directory.get_descendant_list_by_path(relative_path)
        directory = dir_list[-1]
        self.assertEqual(directory._project, project)

        for key in file_dict.keys():
            file_name = key
            local_path = file_dict[key]
            self.assertTrue(os_path.isfile(local_path))
            test_file = directory.add_file(file_name, local_path)
            self.assertEqual(test_file.name, file_name)
            byte_count = getsize(local_path)
            self.assertEqual(test_file.size, byte_count)

    def test_file_dir_upload_inline(self):
        directory_name = fake_name("test_full_dir")

        project = self.base_project
        top_directory = project.get_top_directory()
        self.assertEqual(top_directory._project, project)

        dir_list = top_directory.create_descendant_list_by_path(directory_name)
        base_directory = dir_list[0]
        self.assertEqual(base_directory._project, project)

        local_base_path = self.get_base_local_test_dir()
        self.assertTrue(os_path.isdir(local_base_path))

        dir_name = self.full_dir

        dir_tree_table = make_dir_tree_table(local_base_path, dir_name, dir_name, {})
        for relative_dir_path in dir_tree_table.keys():
            file_dict = dir_tree_table[relative_dir_path]
            dirs = base_directory.create_descendant_list_by_path(relative_dir_path)
            directory = dirs[-1]
            for file_name in file_dict.keys():
                directory.add_file(file_name, file_dict[file_name])

        children = base_directory.get_children()
        self.assertEqual(len(children), 1)
        directory = children[0]
        self.assertEqual(directory._project, project)
        self.assertEqual(directory.name, dir_name)

        children = directory.get_children()
        self.assertEqual(len(children), 4)
        d = self.make_child_dict(children)
        c1 = d['TopLevel.txt']
        c2 = d['sub_directory_a']
        c3 = d['sub_directory_b']
        c4 = d['sub_directory_c']
        self.assertEqual(c1.otype, 'file')
        self.assertEqual(c2.otype, 'directory')
        self.assertEqual(c3.otype, 'directory')
        self.assertEqual(c4.otype, 'directory')

        children = c2.get_children()
        self.assertEqual(len(children), 1)
        d = self.make_child_dict(children)
        c21 = d['A.txt']
        self.assertEqual(c21.otype, 'file')

        children = c3.get_children()
        self.assertEqual(len(children), 2)
        d = self.make_child_dict(children)
        c31 = d['B1.txt']
        c32 = d['B2.txt']
        self.assertEqual(c31.otype, 'file')
        self.assertEqual(c32.otype, 'file')

        children = c4.get_children()
        self.assertEqual(len(children), 2)
        d = self.make_child_dict(children)
        c41 = d['C.txt']
        c42 = d['empty_dir']
        self.assertEqual(c41.otype, 'file')
        self.assertEqual(c42.otype, 'directory')

    def test_file_dir_upload(self):
        directory_name = fake_name("test_full_dir")

        project = self.base_project
        top_directory = project.get_top_directory()
        self.assertEqual(top_directory._project, project)

        dir_list = top_directory.create_descendant_list_by_path(directory_name)
        base_directory = dir_list[0]
        self.assertEqual(base_directory._project, project)

        local_base_path = self.get_base_local_test_dir()
        self.assertTrue(os_path.isdir(local_base_path))

        dir_name = self.full_dir

        results = base_directory.add_directory_tree(dir_name, local_base_path)

        file_table = self.make_results_file_dictionary(results)

        for file_name in ['TopLevel.txt', 'A.txt', 'B1.txt', 'B2.txt', 'C.txt']:
            self.assertTrue(file_name in file_table)

        base_dir_name = '/' + directory_name + '/'

        name_path_list = [
            ['TopLevel.txt', base_dir_name + 'test_upload_dir'],
            ['A.txt', base_dir_name + 'test_upload_dir/sub_directory_a'],
            ['B1.txt', base_dir_name + 'test_upload_dir/sub_directory_b'],
            ['B2.txt', base_dir_name + 'test_upload_dir/sub_directory_b'],
            ['C.txt', base_dir_name + 'test_upload_dir/sub_directory_c']
        ]

        for name_path in name_path_list:
            file_name = name_path[0]
            path = name_path[1]
            test_file = file_table[file_name]
            directory_list = project.get_directory_list(path)
            directory = directory_list[-1]
            self.assertEqual(test_file._directory_id, directory.id)

        directory = base_directory
        children = directory.get_children()
        self.assertEqual(len(children), 1)
        directory = children[0]
        self.assertEqual(directory._project, project)
        self.assertEqual(directory.name, dir_name)

        children = directory.get_children()
        self.assertEqual(len(children), 4)
        d = self.make_child_dict(children)
        c1 = d['TopLevel.txt']
        c2 = d['sub_directory_a']
        c3 = d['sub_directory_b']
        c4 = d['sub_directory_c']
        self.assertEqual(c1.otype, 'file')
        self.assertEqual(c2.otype, 'directory')
        self.assertEqual(c3.otype, 'directory')
        self.assertEqual(c4.otype, 'directory')

        children = c2.get_children()
        self.assertEqual(len(children), 1)
        d = self.make_child_dict(children)
        c21 = d['A.txt']
        self.assertEqual(c21.otype, 'file')

        children = c3.get_children()
        self.assertEqual(len(children), 2)
        d = self.make_child_dict(children)
        c31 = d['B1.txt']
        c32 = d['B2.txt']
        self.assertEqual(c31.otype, 'file')
        self.assertEqual(c32.otype, 'file')

        children = c4.get_children()
        self.assertEqual(len(children), 2)
        d = self.make_child_dict(children)
        c41 = d['C.txt']
        c42 = d['empty_dir']
        self.assertEqual(c41.otype, 'file')
        self.assertEqual(c42.otype, 'directory')

    def get_base_local_test_dir(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'test_upload_data')
        return test_path

    def setup_test_directory_path(self, dir_name):
        test_path = self.get_base_local_test_dir()
        self.assertTrue(os_path.isdir(test_path))
        return os_path.join(test_path, dir_name)

    def make_child_dict(self, child_list):
        ret = {}
        for child in child_list:
            ret[child.name] = child
        return ret

    def make_results_file_dictionary(self, file_list):
        ret = {}
        for f in file_list:
            name = f.name
            ret[name] = f
        return ret

    # Check that the empty dir, needed for the tests, exists.
    # Note - github does not save empty directories.
    def fix_empty_dir_if_needed(self):
        path = self.setup_test_directory_path(self.path_of_empty_dir)
        if not os_path.isdir(path):
            makedirs(path)

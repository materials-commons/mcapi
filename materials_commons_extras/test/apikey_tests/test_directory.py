import unittest
from random import randint

from materials_commons.api import create_project


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


# moved to File
# def add_file(self, file_name, local_input_path, verbose=False, limit=50):
# def add_directory_tree(dir_name, input_dir_path, verbose=False, limit=50):

# moved from Project
# def get_directory_list(self, path):
# def create_or_get_all_directories_on_path(self, path):
# def add_directory_list(self, path_list, top=None):
# - redundant to test with multiple directories
# def get_directory_by_id(self, directory_id):
# def get_all_directories(self):

class TestDirectory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"
        cls.project_name = fake_name("TestApikeyProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description, apikey=cls.apikey)
        cls.top_directory = cls.project.get_top_directory()
        cls.test_directory_path = "/A/B/C"

    def test_directory_create_list(self):
        directory_list = self.top_directory.create_descendant_list_by_path(self.test_directory_path)
        self.assertEqual(3, len(directory_list))
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[0].name)
        name = name + '/B'
        self.assertEqual(name, directory_list[1].name)
        name = name + '/C'
        self.assertEqual(name, directory_list[2].name)

        # additional create same as get - no problem
        directory_list = self.top_directory.create_descendant_list_by_path(self.test_directory_path)
        self.assertEqual(3, len(directory_list))
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[0].name)
        name = name + '/B'
        self.assertEqual(name, directory_list[1].name)
        name = name + '/C'
        self.assertEqual(name, directory_list[2].name)

    def test_directory_get_list(self):
        # make sure that they exist
        directory_list = self.top_directory.create_descendant_list_by_path(self.test_directory_path)
        self.assertEqual(3, len(directory_list))
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[0].name)
        name = name + '/B'
        self.assertEqual(name, directory_list[1].name)
        name = name + '/C'
        self.assertEqual(name, directory_list[2].name)

        directory_list = self.top_directory.get_descendant_list_by_path(self.test_directory_path)
        self.assertEqual(4, len(directory_list))
        name = self.project_name
        self.assertEqual(name, directory_list[0].path)
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[1].path)
        name = name + '/B'
        self.assertEqual(name, directory_list[2].path)
        name = name + '/C'
        self.assertEqual(name, directory_list[3].path)

        # attempt to get unknown path - docs say exception, but...
        directory_list = self.top_directory.get_descendant_list_by_path("/X/Y")
        self.assertEqual(1, len(directory_list))
        name = self.project_name
        self.assertEqual(name, directory_list[0].path)

    def test_directory_rename(self):
        directory_list = self.top_directory.create_descendant_list_by_path("/D/E")
        self.assertEqual(2, len(directory_list))
        name = self.project_name + '/D/E'
        directory = directory_list[1]
        self.assertEqual(name, directory.name)
        new_name = "Rename"
        renamed = directory.rename(new_name)
        self.assertEqual(new_name, renamed.name)
        updated = self.project.get_directory_by_id(directory.id)
        self.assertEqual(new_name, updated.name)

    def test_get_children(self):
        # make sure that they exist
        directory_list = self.top_directory.create_descendant_list_by_path(self.test_directory_path)
        self.assertEqual(3, len(directory_list))
        name = self.project_name + '/A/B/C'
        self.assertEqual(name, directory_list[2].name)
        child_list = directory_list[1].get_children()
        self.assertEqual(1, len(child_list))
        self.assertEqual(name, child_list[0].path)

    def test_directory_move(self):
        directory_list = self.top_directory.create_descendant_list_by_path("/F/G/H")
        self.assertEqual(3, len(directory_list))
        print('')
        directory_f = directory_list[0]
        directory_g = directory_list[1]
        directory_h = directory_list[2]

        # move H from G to F
        child_list = directory_f.get_children()
        self.assertEqual(1, len(child_list))
        name = self.project_name + "/F/G"
        self.assertEqual(name, child_list[0].path)

        child_list = directory_g.get_children()
        self.assertEqual(1, len(child_list))
        name = self.project_name + "/F/G/H"
        self.assertEqual(name, child_list[0].path)

        directory_h.move(directory_f)
        child_list = directory_f.get_children()
        self.assertEqual(2, len(child_list))

        child_list = directory_g.get_children()
        self.assertEqual(0, len(child_list))


class TestProjectDirectory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"
        cls.project_name = fake_name("TestApikeyProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description, apikey=cls.apikey)
        cls.top_directory = cls.project.get_top_directory()
        cls.test_directory_path = "/A/B/C"

    def test_project_create_directory(self):
        directory_list = self.project.create_or_get_all_directories_on_path(self.test_directory_path)
        self.assertEqual(3, len(directory_list))
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[0].name)
        name = name + '/B'
        self.assertEqual(name, directory_list[1].name)
        name = name + '/C'
        self.assertEqual(name, directory_list[2].name)

    def test_project_get_directory_list(self):
        # make sure that they exist
        directory_list = self.project.create_or_get_all_directories_on_path(self.test_directory_path)
        self.assertEqual(3, len(directory_list))
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[0].name)
        name = name + '/B'
        self.assertEqual(name, directory_list[1].name)
        name = name + '/C'
        self.assertEqual(name, directory_list[2].name)

        directory_list = self.project.get_directory_list(self.test_directory_path)
        self.assertEqual(4, len(directory_list))
        name = self.project_name
        self.assertEqual(name, directory_list[0].path)
        name = self.project_name + '/A'
        self.assertEqual(name, directory_list[1].path)
        name = name + '/B'
        self.assertEqual(name, directory_list[2].path)
        name = name + '/C'
        self.assertEqual(name, directory_list[3].path)

    def test_project_add_directory(self):
        directory = self.project.add_directory("/D/E")
        name = self.project_name + "/D/E"
        self.assertEqual(name, directory.name)

    def test_project_add_directory_list(self):
        path11 = "/F/G1/H1"
        path12 = "/F/G1/H2"
        path23 = "/F/G2/H3"
        path3n = "/F/G3"
        path_list = [path11, path12, path23, path3n]
        directory_path_table = self.project.add_directory_list(path_list)
        for path in path_list:
            self.assertTrue(path in directory_path_table)

    def test_project_get_directory_by_id(self):
        directory = self.project.add_directory("/I1/I2")
        name = self.project_name + "/I1/I2"
        directory = self.project.get_directory_by_id(directory.id)
        self.assertEqual(name, directory.path)


class TestProjectDirectoryIsolated(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"
        cls.project_name = fake_name("TestApikeyProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description, apikey=cls.apikey)

    def test_get_all_directories(self):
        path11 = "/F/G1/H1"
        path12 = "/F/G1/H2"
        path23 = "/F/G2/H3"
        path3n = "/F/G3"
        path_list = [path11, path12, path23, path3n]
        directory_path_table = self.project.add_directory_list(path_list)
        for path in path_list:
            self.assertTrue(path in directory_path_table)

        default_path_list = ['/Literature', '/Presentations', '/Project Documents']
        path_list = [str(key) for key in directory_path_table.keys()] + default_path_list
        path_list = [self.project_name + path for path in path_list]
        path_list.append(self.project_name)
        directory_list = self.project.get_all_directories()
        self.assertEqual(11, len(directory_list))
        self.assertEqual(11, len(path_list))
        actual_path_list = [d.name for d in directory_list]
        for path in actual_path_list:
            self.assertTrue(path in path_list, "path, {}, not in path list".format(path))

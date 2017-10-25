import unittest
import os
import re
import materials_commons.api as mcapi
from extras.test.cli_tests.cli_test_functions import working_dir, captured_output, print_string_io
from materials_commons.cli.init import init_subcommand
from materials_commons.cli.up import up_subcommand
from materials_commons.cli.functions import make_local_project


def mkdir_if(path):
    if not os.path.exists(path):
        os.mkdir(path)


def remove_if(path):
    if os.path.exists(path):
        os.remove(path)


def rmdir_if(path):
    if os.path.exists(path):
        os.rmdir(path)


def make_file(path, text):
    with open(path, 'w') as f:
        f.write(text)


class TestMCUp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if 'TEST_DATA_DIR' not in os.environ:
            raise Exception("No TEST_DATA_DIR environment variable")
        cls.cli_test_project_path = os.path.join(os.environ['TEST_DATA_DIR'], 'cli_test_project')
        cls.proj_path = os.path.join(cls.cli_test_project_path, 'CLITest')
        cls.dirs = [
            os.path.join(cls.proj_path, "level_1"),
            os.path.join(cls.proj_path, "level_1", "level_2")
        ]
        cls.files = [
            (os.path.join(cls.proj_path, "file_A.txt"), "This is file A, level 0"),
            (os.path.join(cls.proj_path, "file_B.txt"), "This is file B, level 0"),
            (os.path.join(cls.proj_path, "level_1", "file_A.txt"), "This is file A, level 1"),
            (os.path.join(cls.proj_path, "level_1", "file_B.txt"), "This is file B, level 1"),
            (os.path.join(cls.proj_path, "level_1", "level_2", "file_A.txt"), "This is file A, level 2"),
            (os.path.join(cls.proj_path, "level_1", "level_2", "file_B.txt"), "This is file B, level 2")
        ]

    @classmethod
    def init(cls):
        mkdir_if(cls.cli_test_project_path)
        mkdir_if(cls.proj_path)
        testargs = ['mc', 'init']
        with captured_output(wd=cls.proj_path) as (sout, serr):
            init_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()

        cls.make_test_files()

    @classmethod
    def clean_files(cls):
        cls.remove_test_files()
        mc = os.path.join(cls.proj_path, ".mc")
        config = os.path.join(mc, "config.json")
        remove_if(config)
        rmdir_if(mc)
        rmdir_if(cls.proj_path)

    @classmethod
    def clean_proj(cls):
        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        if 'CLITest' in proj_dict:
            proj_dict['CLITest'].delete()

    @classmethod
    def clean(cls):
        cls.clean_proj()
        cls.clean_files()

    @classmethod
    def make_test_files(cls):
        for dir in cls.dirs:
            mkdir_if(dir)
        for val in cls.files:
            make_file(val[0], val[1])

    @classmethod
    def remove_test_files(cls):
        for val in cls.files:
            remove_if(val[0])
        for dir in reversed(cls.dirs):
            rmdir_if(dir)

    def setUp(self):
        self.clean()
        self.init()

    def tearDown(self):
        self.clean()

    def get_proj(self):
        return make_local_project(self.proj_path)

    def test_one_in_top(self):
        # upload 1 file (in top directory)
        testargs = ['mc', 'up', self.files[0][0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        proj = self.get_proj()

        file = proj.get_by_local_path(self.files[0][0])
        self.assertTrue(isinstance(file, mcapi.File))
        self.assertEqual(file.name, os.path.basename(self.files[0][0]))
        self.assertEqual(file._directory_id, proj.get_top_directory().id)

    def test_one_with_intermediate(self):
        # upload 1 file (in level_2 directory)
        testargs = ['mc', 'up', self.files[4][0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        proj = self.get_proj()

        file = proj.get_by_local_path(self.files[4][0])
        parent = proj.get_directory_by_id(file._directory_id)
        self.assertTrue(isinstance(file, mcapi.File))
        self.assertEqual(file.name, os.path.basename(self.files[4][0]))
        self.assertEqual(file._directory_id, parent.id)
        self.assertEqual(parent.path, "CLITest/level_1/level_2")

    def test_recursive_all(self):
        # upload everything
        testargs = ['mc', 'up', '-r', '.']
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        proj = self.get_proj()

        for d in self.dirs:
            dir = proj.get_by_local_path(d)
            self.assertTrue(isinstance(dir, mcapi.Directory))

        for f in self.files:
            file = proj.get_by_local_path(f[0])
            self.assertTrue(isinstance(file, mcapi.File))

    def test_recursive(self):
        # upload files in level_1 and level_2
        testargs = ['mc', 'up', '-r', self.dirs[0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        proj = self.get_proj()

        for d in self.dirs:
            dir = proj.get_by_local_path(d)
            self.assertTrue(isinstance(dir, mcapi.Directory))

        for f in self.files[2:]:
            file = proj.get_by_local_path(f[0])
            self.assertTrue(isinstance(file, mcapi.File))

    @classmethod
    def tearDownClass(cls):
        cls.clean()

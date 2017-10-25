import unittest
import os
import re
import materials_commons.api as mcapi
from .cli_test_functions import captured_output
from materials_commons.cli.init import init_subcommand
from materials_commons.cli.up import up_subcommand
from materials_commons.cli.ls import ls_subcommand
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


i_mo = 0
i_yr = 1
i_day = 2
i_time = 3
i_l_size = 4
i_l_type = 5
i_r_mtime = 6
i_r_size = 7
i_r_type = 8
i_eq = 9
i_name = 10
i_id = 11


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

    def test_one_file(self):
        # ls 1 file (in top directory)
        testargs = ['mc', 'ls', self.files[2][0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[1].split()[i_l_type], 'file')
        self.assertEqual(out[1].split()[i_r_size], '-')
        self.assertEqual(out[1].split()[i_r_type], '-')
        self.assertEqual(out[1].split()[i_name], 'level_1/file_A.txt')
        self.assertEqual(out[1].split()[i_id], '-')

        testargs = ['mc', 'up', self.files[2][0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)

        testargs = ['mc', 'ls', self.files[2][0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[1].split()[i_l_type], 'file')
        self.assertNotEqual(out[1].split()[i_r_size], '-')
        self.assertEqual(out[1].split()[i_r_type], 'file')
        self.assertEqual(out[1].split()[i_name], 'level_1/file_A.txt')
        self.assertNotEqual(out[1].split()[i_id], '-')

    def test_one_dir(self):
        # ls directory
        testargs = ['mc', 'ls', self.dirs[0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[2].split()[i_l_type], 'file')
        self.assertEqual(out[2].split()[i_r_type], '-')
        self.assertEqual(out[3].split()[i_l_type], 'file')
        self.assertEqual(out[3].split()[i_r_type], '-')
        self.assertEqual(out[4].split()[i_l_type], 'dir')
        self.assertEqual(out[4].split()[i_r_type], '-')

        testargs = ['mc', 'up', self.files[2][0], self.files[3][0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)

        testargs = ['mc', 'ls', self.dirs[0]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[2].split()[i_l_type], 'file')
        self.assertNotEqual(out[2].split()[i_r_type], '-')
        self.assertEqual(out[3].split()[i_l_type], 'file')
        self.assertNotEqual(out[3].split()[i_r_type], '-')
        self.assertEqual(out[4].split()[i_l_type], 'dir')
        self.assertEqual(out[4].split()[i_r_type], '-')

    def test_two_dir(self):
        # ls two directories
        testargs = ['mc', 'ls', self.dirs[0], self.dirs[1]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[2].split()[i_l_type], 'file')
        self.assertEqual(out[2].split()[i_r_type], '-')
        self.assertEqual(out[3].split()[i_l_type], 'file')
        self.assertEqual(out[3].split()[i_r_type], '-')
        self.assertEqual(out[4].split()[i_l_type], 'dir')
        self.assertEqual(out[4].split()[i_r_type], '-')
        self.assertEqual(out[8].split()[i_l_type], 'file')
        self.assertEqual(out[8].split()[i_r_type], '-')
        self.assertEqual(out[9].split()[i_l_type], 'file')
        self.assertEqual(out[9].split()[i_r_type], '-')

        testargs = ['mc', 'up', self.dirs[1]]
        with captured_output(wd=self.proj_path) as (sout, serr):
            up_subcommand(testargs)
        # print_stringIO(sout)

        testargs = ['mc', 'ls', self.dirs[0], self.dirs[1], '--checksum']
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[2].split()[i_l_type], 'file')
        self.assertEqual(out[2].split()[i_r_type], '-')
        self.assertEqual(out[3].split()[i_l_type], 'file')
        self.assertEqual(out[3].split()[i_r_type], '-')
        self.assertEqual(out[4].split()[i_l_type], 'dir')
        self.assertNotEqual(out[4].split()[i_r_size], '-')
        self.assertEqual(out[4].split()[i_r_type], 'dir')

        self.assertEqual(out[8].split()[i_l_type], 'file')
        self.assertNotEqual(out[8].split()[i_r_size], '-')
        self.assertEqual(out[8].split()[i_r_type], 'file')
        self.assertEqual(out[8].split()[i_eq], 'True')
        self.assertEqual(out[9].split()[i_l_type], 'file')
        self.assertNotEqual(out[9].split()[i_r_size], '-')
        self.assertEqual(out[9].split()[i_r_type], 'file')

        # test equivalence check
        with open(self.files[4][0], 'w') as f:
            f.write("changed")

        testargs = ['mc', 'ls', self.dirs[0], self.dirs[1], '--checksum']
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertEqual(out[8].split()[i_eq], 'False')

        # test json
        testargs = ['mc', 'ls', self.dirs[0], self.dirs[1], '--checksum']
        with captured_output(wd=self.proj_path) as (sout, serr):
            ls_subcommand(testargs)
        # print_stringIO(sout)
        self.assertTrue(True)

    @classmethod
    def tearDownClass(cls):
        cls.clean()

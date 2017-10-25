import unittest
import os
import re
import materials_commons.api as mcapi
from materials_commons.api import _use_remote as mcapi_use_remote
from .cli_test_functions import captured_output
from materials_commons.cli.init import init_subcommand
from materials_commons.cli.clone import clone_subcommand


def mkdir_if(path):
    if not os.path.exists(path):
        os.mkdir(path)


class TestMCClone(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if 'TEST_DATA_DIR' not in os.environ:
            raise Exception("No TEST_DATA_DIR environment variable")
        cls.cli_test_project_path = os.path.join(os.environ['TEST_DATA_DIR'], 'cli_test_project')
        cls.proj_path = os.path.join(cls.cli_test_project_path, 'CLITest')
        cls.clean()

    @classmethod
    def clean_files(cls):
        mc = os.path.join(cls.proj_path, ".mc")
        config = os.path.join(mc, "config.json")
        if os.path.exists(config):
            os.remove(config)
        if os.path.exists(mc):
            os.rmdir(mc)
        if os.path.exists(cls.proj_path):
            os.rmdir(cls.proj_path)

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

    def test_mc_clone(self):
        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        self.assertFalse('CLITest' in proj_dict)

        mkdir_if(self.cli_test_project_path)
        mkdir_if(self.proj_path)
        testargs = ['mc', 'init']
        with captured_output(wd=self.proj_path) as (sout, serr):
            init_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        remote = mcapi_use_remote()
        url = remote.config.mcurl
        self.assertEqual(out[0], "Created new project at: " + url)

        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}

        self.clean_files()
        mkdir_if(self.cli_test_project_path)
        testargs = ['mc', 'clone', proj_dict['CLITest'].id]
        with captured_output(wd=self.cli_test_project_path) as (sout, serr):
            clone_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertTrue(re.match("Cloned project", out[0]))
        self.assertEqual('CLITest', out[3].split()[0])

    @classmethod
    def tearDownClass(cls):
        cls.clean()

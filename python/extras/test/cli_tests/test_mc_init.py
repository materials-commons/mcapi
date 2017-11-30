import unittest
import os
import re
import materials_commons.api as mcapi
from materials_commons.api import _use_remote as mcapi_use_remote
from .cli_test_functions import working_dir, captured_output
from materials_commons.cli.init import init_subcommand
from materials_commons.cli.functions import make_local_project


class TestMCInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if 'TEST_DATA_DIR' not in os.environ:
            raise Exception("No TEST_DATA_DIR environment variable")
        cli_test_project_path = os.path.join(os.environ['TEST_DATA_DIR'], 'cli_test_project')
        cls.proj_path = os.path.join(cli_test_project_path, 'CLITest')
        cls.clean()
        if not os.path.exists(cli_test_project_path):
            os.mkdir(cli_test_project_path)
        if not os.path.exists(cls.proj_path):
            os.mkdir(cls.proj_path)

    @classmethod
    def clean(cls):
        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        if 'CLITest' in proj_dict:
            proj_dict['CLITest'].delete()
        mc = os.path.join(cls.proj_path, ".mc")
        config = os.path.join(mc, "config.json")
        if os.path.exists(config):
            os.remove(config)
        if os.path.exists(mc):
            os.rmdir(mc)
        if os.path.exists(cls.proj_path):
            os.rmdir(cls.proj_path)

    def test_mc_init(self):
        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        self.assertFalse('CLITest' in proj_dict)

        testargs = ['mc', 'init']
        with captured_output(wd=self.proj_path) as (sout, serr):
            init_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        remote = mcapi_use_remote()
        url = remote.config.mcurl
        self.assertEqual(out[0], "Created new project at: " + url)

        testargs = ['mc', 'init']
        with captured_output(wd=self.proj_path) as (sout, serr):
            init_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertTrue(re.match('Already in project.  name: CLITest', out[0]))

        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        self.assertTrue('CLITest' in proj_dict)

        with working_dir(self.proj_path):
            proj = make_local_project()
            self.assertEqual(proj.name, 'CLITest')

    @classmethod
    def tearDownClass(cls):
        cls.clean()

import unittest
import os
import re
import materials_commons.api as mcapi
from materials_commons.api import _use_remote as mcapi_use_remote
from .cli_test_functions import captured_output
from materials_commons.cli.init import init_subcommand
from materials_commons.cli.expt import expt_subcommand


def mkdir_if(path):
    if not os.path.exists(path):
        os.mkdir(path)


def remove_if(path):
    if os.path.exists(path):
        os.remove(path)


def rmdir_if(path):
    if os.path.exists(path):
        os.rmdir(path)


class TestMCExpt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if 'TEST_DATA_DIR' not in os.environ:
            raise Exception("No TEST_DATA_DIR environment variable")
        cli_test_project_path = os.path.join(os.environ['TEST_DATA_DIR'], 'cli_test_project')
        cls.proj_path = os.path.join(cli_test_project_path, 'CLITest')
        cls.clean()
        mkdir_if(cli_test_project_path)
        mkdir_if(cls.proj_path)

    @classmethod
    def clean(cls):
        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        if 'CLITest' in proj_dict:
            proj_dict['CLITest'].delete()
        mc = os.path.join(cls.proj_path, ".mc")
        config = os.path.join(mc, "config.json")
        remove_if(config)
        rmdir_if(mc)
        rmdir_if(cls.proj_path)

    def test_mc_expt(self):
        testargs = ['mc', 'init']
        with captured_output(wd=self.proj_path) as (sout, serr):
            init_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        remote = mcapi_use_remote()
        url = remote.config.mcurl
        self.assertEqual(out[0], "Created new project at: " + url)

        testargs = ['mc', 'expt', '-c', 'test_A']
        with captured_output(wd=self.proj_path) as (sout, serr):
            expt_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertTrue(re.match("Created experiment: test_A", out[0]))
        self.assertTrue(re.match("Set current experiment: 'test_A'", out[1]))

        testargs = ['mc', 'expt', '-c', 'test_B']
        with captured_output(wd=self.proj_path) as (sout, serr):
            expt_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        self.assertTrue(re.match("Created experiment: test_B", out[0]))
        self.assertTrue(re.match("Set current experiment: 'test_B'", out[1]))

        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        expts_list = proj_dict['CLITest'].get_all_experiments()
        expts_dict = {e.name: e for e in expts_list}
        self.assertEqual(len(expts_list), 2)
        self.assertTrue('test_A' in expts_dict)
        self.assertTrue('test_B' in expts_dict)

        # dry-run is no longer an option on delete (e.g can not use -n)
        # testargs = ['mc', 'expt', '-d', 'test_B', '-n']
        # with captured_output(wd=self.proj_path) as (sout, serr):
        #    expt_subcommand(testargs)
        # print_stringIO(sout)
        # out = sout.getvalue().splitlines()

        # proj_list = mcapi.get_all_projects()
        # proj_dict = {p.name:p for p in proj_list}
        # expts_list = proj_dict['CLITest'].get_all_experiments()
        # expts_dict = {e.name:e for e in expts_list}
        # self.assertEqual(len(expts_list), 2)
        # self.assertTrue('test_A' in expts_dict)
        # self.assertTrue('test_B' in expts_dict)

        testargs = ['mc', 'expt', '-d', 'test_B']
        with captured_output(wd=self.proj_path) as (sout, serr):
            expt_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()

        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        expts_list = proj_dict['CLITest'].get_all_experiments()
        expts_dict = {e.name: e for e in expts_list}
        self.assertEqual(len(expts_list), 1)
        self.assertTrue('test_A' in expts_dict)

    @classmethod
    def tearDownClass(cls):
        cls.clean()

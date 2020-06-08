import argparse
import unittest
import os
from .cli_test_functions import captured_output, print_string_io
from materials_commons2 import models
from materials_commons2_cli.subcommands.proj import ProjSubcommand
import materials_commons2_cli.user_config as user_config


class TestMCProj(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_failure = None
        cls.proj_subcommand = ProjSubcommand()

        # ensure there are at least three projects
        client = user_config.Config().default_remote.make_client()
        client.create_project("__clitest__proj_1")
        client.create_project("__clitest__proj_2")
        client.create_project("__clitest__proj_3")
        result = client.get_all_projects()
        if len(result) < 3:
            cls.setup_failure = "project creation failure"

    def setUp(self):
        if self.setup_failure:
            self.fail(self.setup_failure)

    @classmethod
    def tearDownClass(cls):
        client = user_config.Config().default_remote.make_client()
        result = client.get_all_projects()
        for proj in result:
            try:
                client.delete_project(proj.id)
            except:
                pass

    def test_project_api(self):
        # test the basis api project commands independently of the ProjSubcommand

        # test "get_all_projects"
        client = user_config.Config().default_remote.make_client()
        result = client.get_all_projects()
        init_project_ids = [proj.id for proj in result]
        n_projects_init = len(init_project_ids)
        self.assertEqual(len(result) - n_projects_init, 0)

        project_names = [
            "__clitest__test_project_api_1",
            "__clitest__test_project_api_2",
            "__clitest__test_project_api_3"]

        # test "create_project"
        for name in project_names:
            client.create_project(name)
        result = client.get_all_projects()
        self.assertEqual(len(result) - n_projects_init, 3)

        # test "get_project"
        for proj in result:
            tmp_proj = client.get_project(proj.id)
            self.assertEqual(isinstance(tmp_proj, models.Project), True)
            self.assertEqual(tmp_proj._data, proj._data)

        # test "update_project"
        for proj in result:
            if proj.name in project_names:
                attrs = {
                    "description": "<new description>"
                }
                tmp_proj = client.update_project(proj.id, attrs)
                self.assertEqual(tmp_proj.description, attrs["description"])
                break

        # test "delete_project"
        for proj in result:
            if proj.name in project_names:
                try:
                    client.delete_project(proj.id)
                except:
                    # print("can't delete:", proj.id)
                    pass

        result = client.get_all_projects()
        self.assertEqual(len(result) - n_projects_init, 0)

    def test_parse_args(self):
        testargs = ['mc', 'proj']
        args = self.proj_subcommand.parse_args(testargs)
        self.assertEqual(isinstance(args, argparse.Namespace), True)

    def test_get_all_from_experiment(self):
        print(os.getcwd())
        self.assertEqual(1, 1)

        # TODO:
        # proj = clifuncs.make_local_project()
        # expt = clifuncs.make_local_expt(proj)
        # with pytest.raises(MCCLIException):
        #     result = self.proj_subcommand.get_all_from_experiment(expt)

    def test_get_all_from_project(self):
        print(os.getcwd())
        self.assertEqual(1, 1)

        # TODO:
        # proj = clifuncs.make_local_project()
        # with pytest.raises(MCCLIException):
        #     result = self.proj_subcommand.get_all_from_project(proj)

    def test_get_all_from_remote(self):
        """Get all from remote should succeed and not require an existing local project"""

        # setUpClass ensures at least 3 projects should exist
        testargs = ['mc', 'proj']
        args = self.proj_subcommand.parse_args(testargs)
        client = self.proj_subcommand.get_remote(args)
        result = self.proj_subcommand.get_all_from_remote(client)
        self.assertEqual(isinstance(result, list), True)
        for obj in result:
            self.assertEqual(isinstance(obj, models.Project), True)

    def test_mc_proj_output(self):
        testargs = ['mc', 'proj']
        with captured_output() as (sout, serr):
            self.proj_subcommand(testargs)
        print_string_io(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()

        headers = out[0].split()
        self.assertEqual(headers[0], "name")
        self.assertEqual(headers[1], "owner")
        self.assertEqual(headers[2], "id")
        self.assertEqual(headers[3], "uuid")
        self.assertEqual(headers[4], "mtime")
        self.assertEqual(len(headers), 5)

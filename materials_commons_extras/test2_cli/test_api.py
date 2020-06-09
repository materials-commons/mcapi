import unittest
import os

import materials_commons2 as mcapi

import materials_commons2_cli.user_config as user_config

class TestAPI(unittest.TestCase):

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
        """Test the basic API project commands independently of the CLI"""
        # test "get_all_projects"
        mcurl = os.environ.get("MC_API_URL")
        email = os.environ.get("MC_API_EMAIL")
        password = os.environ.get("MC_API_PASSWORD")
        client = mcapi.Client.login(email, password, base_url=mcurl)

        project_names = [
            "__clitest__test_project_api_1",
            "__clitest__test_project_api_2",
            "__clitest__test_project_api_3"]

        # make sure test projects do not already exist
        result = client.get_all_projects()
        for proj in result:
            if proj.name in project_names:
                try:
                    client.delete_project(proj.id)
                except:
                    # print("can't delete:", proj.id)
                    pass

        # get currently existing projects
        result = client.get_all_projects()
        init_project_ids = [proj.id for proj in result]
        n_projects_init = len(init_project_ids)
        self.assertEqual(len(result) - n_projects_init, 0)

        # test "create_project"
        for name in project_names:
            client.create_project(name)
        result = client.get_all_projects()
        self.assertEqual(len(result) - n_projects_init, 3)

        # test "get_project"
        for proj in result:
            tmp_proj = client.get_project(proj.id)
            self.assertEqual(isinstance(tmp_proj, mcapi.Project), True)
            self.assertEqual(tmp_proj._data, proj._data)

        # test "update_project"
        for proj in result:
            if proj.name in project_names:
                update_request = mcapi.UpdateProjectRequest(
                    proj.name,
                    description="<new description>")
                tmp_proj = client.update_project(proj.id, update_request)
                self.assertEqual(tmp_proj.description, "<new description>")
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

    def test_experiment_api(self):
        """Test the basic API experiment commands independently of the CLI"""
        # test "get_all_projects"
        mcurl = os.environ.get("MC_API_URL")
        email = os.environ.get("MC_API_EMAIL")
        password = os.environ.get("MC_API_PASSWORD")
        client = mcapi.Client.login(email, password, base_url=mcurl)

        proj = client.create_project("__clitest__experiment_api")
        experiment_request = mcapi.CreateExperimentRequest(description="<experiment description>")
        experiment_1 = client.create_experiment(proj.id, "<experiment name 1>", experiment_request)
        experiment_2 = client.create_experiment(proj.id, "<experiment name 2>", experiment_request)
        experiment_3 = client.create_experiment(proj.id, "<experiment name 3>", experiment_request)
        self.assertEqual(experiment_1.name, "<experiment name 1>")
        self.assertEqual(experiment_1.description, "<experiment description>")

        all_experiments = client.get_all_experiments(proj.id)
        self.assertEqual(len(all_experiments), 3)
        for experiment in all_experiments:
            self.assertEqual(isinstance(experiment, mcapi.Experiment), True)
            expt = client.get_experiment(experiment.id)
            self.assertEqual(expt.id, experiment.id)
            experiment_request = mcapi.CreateExperimentRequest(description="<new description>")
            updated_expt = client.update_experiment(expt.id, experiment_request)
            self.assertEqual(updated_expt.description, "<new description>")
            success = client.delete_experiment(proj.id, expt.id)
            self.assertEqual(success, None) # TODO: update, expecting bool from docs

        all_experiments = client.get_all_experiments(proj.id)
        self.assertEqual(len(all_experiments), 0)

import unittest
import pytest
from os import environ
from os import path as os_path
from random import randint
from materials_commons.api import get_project_by_id, get_all_projects
from materials_commons.api import _use_remote as use_remote, _set_remote as set_remote, get_all_users
from materials_commons.api import get_remote_config_url
import extras.demo_project.demo_project as demo
from .assert_helper import AssertHelper


def _fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestProjectDelete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mcapikey = "totally-bogus"
        cls.host = get_remote_config_url()

    def test_delete(self):
        self.helper = AssertHelper(self)

        project = self._build_project()
        project_name = self.test_project_name
        experiment = project.get_all_experiments()[0]
        self.helper.confirm_demo_project_content(project, project_name, 1)

        deleted_project_id = project.delete()

        self.assertEqual(deleted_project_id, project.id)
        with pytest.raises(Exception):
            get_project_by_id(project.id)

        with pytest.raises(Exception):
            project.get_all_experiments()

        self.assertIsNone(project.get_experiment_by_id(experiment.id))

    @pytest.mark.skip(reason="failing - need to review")
    def test_delete_all_projects(self):
        self.helper = AssertHelper(self)

        self._build_project()

        projects = get_all_projects()
        self.assertTrue(len(projects) > 0)

        for project in projects:
            project.delete()

        projects = get_all_projects()
        self.assertEqual(len(projects), 0)

    def test_only_owner_can_delete(self):
        self.helper = AssertHelper(self)

        project = self._build_project()

        another_user_id = 'another@test.mc'
        another_user_key = 'another-bogus-account'

        users = get_all_users()
        user = None
        for probe in users:
            if probe.id == another_user_id:
                user = probe
        self.assertIsNotNone(user)

        project.add_user_to_access_list(another_user_id)
        self.assertTrue(user.can_access(project))

        self._set_up_remote_for(another_user_key)

        results = project.delete()
        self.assertIsNone(results)

        self._set_up_remote_for(self.mcapikey)

    def _set_up_remote_for(self, key):
        remote = use_remote()
        remote.config.mcapikey = key
        remote.config.params = {'apikey': key}
        set_remote(remote)

    def _build_project(self):
        project_name = _fake_name("ProjectDeleteTest")
        print("")
        print("Project name: " + project_name)

        self.test_project_name = project_name

        builder = demo.DemoProject(self._make_test_dir_path())

        table = builder._make_template_table()
        self.assertIsNotNone(builder._template_id_with(table, 'Create'))
        self.assertIsNotNone(builder._template_id_with(table, 'Sectioning'))
        self.assertIsNotNone(builder._template_id_with(table, 'EBSD SEM'))
        self.assertIsNotNone(builder._template_id_with(table, 'EPMA'))

        project = builder.build_project()

        name = 'Demo Project'
        self.helper.confirm_demo_project_content(project, name, 1)

        project = project.rename(project_name)
        self.assertEqual(project.name, project_name)

        return project

    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path

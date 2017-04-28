import unittest
import pytest
from os import environ
from os import path as os_path
from random import randint
from mcapi import set_remote_config_url, fetch_project_by_id, list_projects
from mcapi import use_remote as use_remote, set_remote, get_all_users
import demo_project as demo
import assert_helper as aid

url = 'http://mctest.localhost/api'


def _fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestProjectDelete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.mcapikey = "totally-bogus"
        cls.host = "http://mctest.localhost"

    def test_delete(self):
        self.helper = aid.AssertHelper(self)

        project = self._build_project()

        project_name = self.test_project_name

        self.helper.confirm_demo_project_content(project, project_name, 1)

        deleted_project = project.delete()

        self.assertEqual(deleted_project.id, project.id)
        self.assertEqual(deleted_project.delete_tally.project['id'], project.id)

        self.assertEqual(len(deleted_project.delete_tally.files), 16)
        self.assertEqual(len(deleted_project.delete_tally.processes), 5)
        self.assertEqual(len(deleted_project.delete_tally.datasets), 0)
        self.assertEqual(len(deleted_project.delete_tally.experiments), 1)
        self.assertEqual(len(deleted_project.delete_tally.samples), 7)

        with pytest.raises(Exception):
            fetch_project_by_id(project.id)

    def test_delete_dry_run(self):
        self.helper = aid.AssertHelper(self)

        project = self._build_project()

        project_name = self.test_project_name

        self.helper.confirm_demo_project_content(project, project_name, 1)

        deleted_project = project.delete(dryRun=True)

        self.assertEqual(deleted_project.id, project.id)
        self.assertEqual(deleted_project.delete_tally.project['id'], project.id)

        self.assertEqual(len(deleted_project.delete_tally.files), 16)
        self.assertEqual(len(deleted_project.delete_tally.processes), 5)
        self.assertEqual(len(deleted_project.delete_tally.datasets), 0)
        self.assertEqual(len(deleted_project.delete_tally.experiments), 1)
        self.assertEqual(len(deleted_project.delete_tally.samples), 7)

        self.helper.confirm_demo_project_content(project, project_name, 1)

    def test_delete_all_projects(self):
        self.helper = aid.AssertHelper(self)

        self._build_project()

        projects = list_projects()
        self.assertTrue(len(projects) > 0)

        for project in projects:
            project.delete()

        projects = list_projects()
        self.assertEqual(len(projects), 0)

    @pytest.mark.skip("server for get_all_users not availble on Travis for testing - change .travis.yml")
    def test_only_owner_can_delete(self):
        self.helper = aid.AssertHelper(self)

        project = self._build_project()

        another_user_id = 'another@test.mc'
        another_user_key = 'another-bogus-account'

        users = get_all_users()
        user = None
        for probe in users:
            if probe.id == another_user_id:
                user = probe
        self.assertIsNotNone(user)

        user.canAccess(project)

        self._set_up_remote_for(another_user_key)

        with pytest.raises(Exception):
            deleted_project = project.delete()

        self._set_up_remote_for(self.mcapikey)

    def _set_up_remote_for(self, key):
        remote = use_remote()
        remote.config.mcapikey = key
        remote.config.params = {'apikey': key}
        set_remote(remote)

    def _build_project(self):
        project_name = _fake_name("ProjectDeleteTest")
        print ""
        print "Project name: " + project_name

        self.test_project_name = project_name

        builder = demo.DemoProject(self.host, self._make_test_dir_path(), self.mcapikey)

        table = builder._make_template_table()
        self.assertIsNotNone(builder._template_id_with(table, 'Create'))
        self.assertIsNotNone(builder._template_id_with(table, 'Sectioning'))
        self.assertIsNotNone(builder._template_id_with(table, 'EBSD SEM'))
        self.assertIsNotNone(builder._template_id_with(table, 'EPMA'))

        project = builder.build_project()

        name = 'Demo Project'
        self.helper.confirm_demo_project_content(project, name, 1)

        project = project.update(project_name)
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

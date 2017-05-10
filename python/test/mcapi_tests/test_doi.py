import unittest
import pytest
from os import environ
from os import path as os_path
from random import randint
from mcapi import set_remote_config_url, get_project_by_id, get_all_projects
from mcapi import use_remote as use_remote, set_remote, get_all_users
import demo_project as demo
import assert_helper as aid

url = 'http://mctest.localhost/api'


def _fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number

class TestDoi(unittest.TestCase):

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

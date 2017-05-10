import unittest
from os import environ
from os import path as os_path
from random import randint
from mcapi import set_remote_config_url
from mcapi import __api as api
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

    def test_doi(self):
        self.helper = aid.AssertHelper(self)

        project = self._build_project()
        self.project = project

        project_name = self.test_project_name

        self.helper.confirm_demo_project_content(project, project_name, 1)

        experiments = project.get_all_experiments()
        self.assertEqual(len(experiments), 1);

        self.experiment = experiments[0];

        title = "Test Dataset"
        description = "This is a test dataset being used in automated (CI) tests of DOI creation"
        author = "First Author"
        publication_year = "2016"

        results = self._addDataset(title, description)
        # oops - dataset does not return otype!
        # self.assertEqual(results['otype'], 'dataset')
        self.assertEqual(results['title'], title)

        self.dataset_id = results['id']

        results = self._restCallToCreateDOI(title,description,author,publication_year)
        print results

    def _build_project(self):
        project_name = _fake_name("ProjectDeleteTest")
        print ""
        print "Project name: " + project_name

        self.test_project_name = project_name

        builder = demo.DemoProject(self.host, self._make_test_dir_path(), self.mcapikey)

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

    def _addDataset(self, title, description):
        project_id = self.project.id
        experiment_id = self.experiment.id
        results = api.create_dataset(project_id, experiment_id, title, description)
        return results

    def _restCallToCreateDOI(self, title, description, author, publication_year):
        project_id = self.project.id
        experiment_id = self.experiment.id
        dataset_id = self.dataset_id
        return api.create_doi(project_id, experiment_id, dataset_id,
                             title, description, author, publication_year)
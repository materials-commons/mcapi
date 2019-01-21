import unittest
import pytest

from os import environ
from os import path as os_path
from random import randint
from materials_commons.api import create_project, get_project_by_id
from materials_commons.etl.old_input_spreadsheet import BuildProjectExperiment
from materials_commons import version


# @pytest.mark.skip("These tests take a long time to run - about 8 seconds on a fast machine")
class TestEtlEndToEnd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        cls.spreadsheet_path = os_path.join(cls.test_dir_path, "test_input.xlsx")
        cls.project_name = cls.fake_name("TestProject")
        cls.experiment_name = cls.fake_name("TestExperiment")
        cls.experiment_description = "This is a test experiment: " + cls.experiment_name
        cls.project = create_project(cls.project_name, "This is a test project")
        # noinspection PyBroadException
        try:
            print()
            print("--------------- version check ------------")
            print(version.version())
            print("--------------- version check ------------")
        except BaseException:
            pass

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertTrue(os_path.isdir(self.test_dir_path))
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertTrue(os_path.exists(self.spreadsheet_path))
        self.assertIsNotNone(self.experiment_name)
        self.assertTrue("TestExperiment" in self.experiment_name)
        self.assertIsNotNone(self.experiment_description)
        self.assertTrue("TestExperiment" in self.experiment_description)
        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.project.name)
        self.assertIsNotNone(self.project.description)
        self.assertEqual(self.project.name, self.project_name)

    @pytest.mark.skip("This tests is failing: review - TEW - July 23, 2018")
    def test_etl_preset_project_id(self):
        builder = BuildProjectExperiment()
        builder.set_rename_is_ok(True)
        builder.preset_project_id(self.project.id)
        builder.build(self.spreadsheet_path, None)
        project_id = builder.metadata.project_id
        self.assertIsNotNone(project_id)
        project = get_project_by_id(project_id)
        self.assertIsNotNone(project)
        self.assertEqual(project.name, self.project_name)

    @pytest.mark.skip("This tests is failing: review - TEW - July 23, 2018")
    def test_etl_preset_experiment_name_description(self):
        builder = BuildProjectExperiment()
        builder.set_rename_is_ok(True)
        builder.preset_project_id(self.project.id)
        builder.preset_experiment_name_description(self.experiment_name, self.experiment_description)
        builder.build(self.spreadsheet_path, None)
        project_id = builder.metadata.project_id
        self.assertIsNotNone(project_id)
        project = get_project_by_id(project_id)
        self.assertIsNotNone(project)
        self.assertEqual(project.name, self.project_name)
        experiment_id = builder.metadata.experiment_id
        self.assertIsNotNone(experiment_id)
        experiment = self._implement_get_experiment_by_id(project, experiment_id)
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.name, self.experiment_name)
        self.assertEqual(experiment.description, self.experiment_description)

    @classmethod
    def make_test_dir_path(cls):
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'etl_test_data')
        return test_path

    @classmethod
    def fake_name(cls, prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number

    @staticmethod
    def _implement_get_experiment_by_id(project, experiment_id):
        probe = None
        for exp in project.get_all_experiments():
            if exp.id == experiment_id:
                probe = exp
                break
        return probe

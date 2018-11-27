import unittest

from os import environ
from os import path as os_path
from random import randint
from materials_commons.api import create_project
from materials_commons.etl.old_input_spreadsheet import BuildProjectExperiment


class TestEtlStagingExcelFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        cls.spreadsheet_path = os_path.join(cls.test_dir_path, "test_input.xlsx")
        cls.project_name = cls.fake_name("TestProject")
        cls.experiment_name = cls.fake_name("TestExperiment")
        cls.experiment_description = "This is a test experiment: " + cls.experiment_name
        cls.project = create_project(cls.project_name, "This is a test project")

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

    def test_etl_staging_test_in_parts(self):
        builder = BuildProjectExperiment()
        data_dir = os_path.join(self.test_dir_path, "test_data", "data")
        builder.set_source_from_path(self.spreadsheet_path)
        builder._set_row_positions()
        builder._set_col_positions()
        builder._determine_start_attribute_row(1)
        desired_file_dir_list = builder._get_source_file_dir_list()
        print("\nTestEtlEndToEnd::test_etl_staging_test_in_parts")
        print(desired_file_dir_list)
        missing_set = set()
        for entry in desired_file_dir_list:
            path = os_path.join(data_dir, entry)
            if not os_path.isdir(path) and not os_path.isfile(path):
                missing_set.add(entry)
        print(missing_set)
        self.assertIsNotNone(missing_set)
        self.assertEqual(1, len(missing_set))
        self.assertTrue('NoDir' in missing_set)

    def test_etl_staging_test(self):
        builder = BuildProjectExperiment()
        data_dir = os_path.join(self.test_dir_path, "test_data", "data")
        missing_set = builder.stage(self.spreadsheet_path, data_dir)
        self.assertIsNotNone(missing_set)
        self.assertEqual(1, len(missing_set))
        self.assertTrue('NoDir' in missing_set)

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
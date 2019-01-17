import unittest

import tempfile
from os import environ
from os import path as os_path
from random import randint

from materials_commons.etl.common.worksheet_data import ExcelIO
# from materials_commons.etl.


class TestInput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        cls.spreadsheet_path = os_path.join(cls.test_dir_path, "test_input.xlsx")

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertTrue(os_path.exists(self.spreadsheet_path))

        probe = self.fake_name("Probe")
        self.assertTrue("Probe" in probe)

    def test_read_worksheet_data(self):
        project_name = self.fake_name("TestProject")
        experiment_name = self.fake_name("TestExperiment")
        interface = ExcelIO()
        self.assertIsNone(interface.workbook)
        interface.read_workbook(self.spreadsheet_path)
        self.assertIsNotNone(interface.workbook)
        interface.set_current_worksheet_by_index(0)
        interface.force_project_name_for_testing(project_name)
        interface.force_experiment_name_for_testing(experiment_name)
        data = interface.read_entire_data_from_current_sheet()
        self.assertIsNotNone(data)
        self.assertEquals(len(data), 10)
        self.assertEquals(data[0][0], "PROJ: " + project_name)
        self.assertEquals(data[1][0], "EXP: " + experiment_name)
        interface.close()


    @classmethod
    def make_test_dir_path(cls):
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'etl_test_data')
        return test_path

    @classmethod
    def fake_name(cls, prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number

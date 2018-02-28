import unittest
from os import environ
from os import path as os_path
from random import randint
from materials_commons.etl.common.worksheet_data import ExcelIO


class TestInput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        cls.spreadsheet_path = os_path.join(cls.test_dir_path, "test_input.xlsx")
        cls.project_name = cls.fake_name("TestProject")
        cls.experiment_name = cls.fake_name("TestExperiment")

    def test_is_setup_correctly(self):
        print("---")
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertTrue(os_path.exists(self.spreadsheet_path))

        self.assertIsNotNone(self.project_name)
        self.assertTrue("TestProject" in self.project_name)
        self.assertIsNotNone(self.experiment_name)
        self.assertTrue("TestExperiment" in self.experiment_name)

    def test_read_workbook(self):
        interface = ExcelIO()
        self.assertIsNone(interface.workbook)
        interface.read_workbook(self.spreadsheet_path)
        self.assertIsNotNone(interface.workbook)
        interface.close()

    def test_read_worksheet_date(self):
        interface = ExcelIO()
        self.assertIsNone(interface.workbook)
        interface.read_workbook(self.spreadsheet_path)
        self.assertIsNotNone(interface.workbook)
        interface.set_current_worksheet_by_index(0)
        data = interface.read_entire_data_from_current_sheet()
        self.assertIsNotNone(data)
        self.assertEquals(len(data), 10)
        self.assertEquals(data[0][0], "PROJ: Generic Testing")
        self.assertEquals(data[1][0], "EXP: Test1")
        interface.close()

    def test_set_program_in_worksheet_data(self):
        interface = ExcelIO()
        self.assertIsNone(interface.workbook)
        interface.read_workbook(self.spreadsheet_path)
        self.assertIsNotNone(interface.workbook)
        interface.set_current_worksheet_by_index(0)
        interface.set_project_name_for_testing(self.project_name)
        data = interface.read_entire_data_from_current_sheet()
        self.assertIsNotNone(data)
        self.assertEquals(len(data), 10)
        self.assertEquals(data[0][0], "PROJ: " + self.project_name)
        self.assertEquals(data[1][0], "EXP: Test1")
        interface.close()

    def test_set_experiment_in_worksheet_data(self):
        interface = ExcelIO()
        self.assertIsNone(interface.workbook)
        interface.read_workbook(self.spreadsheet_path)
        self.assertIsNotNone(interface.workbook)
        interface.set_current_worksheet_by_index(0)
        interface.set_experiment_name_for_testing(self.experiment_name)
        data = interface.read_entire_data_from_current_sheet()
        self.assertIsNotNone(data)
        self.assertEquals(len(data), 10)
        self.assertEquals(data[0][0], "PROJ: Generic Testing")
        self.assertEquals(data[1][0], "EXP: " + self.experiment_name)
        interface.close()

    def test_write_data_to_worksheet(self):
        pass
        # get temp file path for worksheet
        # make dummy data for worksheet
        # write dummy data to worksheet
        # read dummy data and confirm


    @classmethod
    def make_test_dir_path(cls):
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'etl_test_data')
        return test_path

    @classmethod
    def fake_name(cls, prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number

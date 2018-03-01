import unittest
from os import environ
from os import path as os_path
from random import randint
from materials_commons.etl.common.metadata import Metadata


class TestMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir_path = cls.make_test_dir_path()
        cls.random_name = cls.fake_name("test")

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.test_dir_path)
        self.assertIsNotNone(self.random_name)
        self.assertTrue("test" in self.random_name)

    def test_metadata_class(self):
        pass
        # most direct way to create metadata is input an excel spreadsheet
        # So, testing input first

    @classmethod
    def make_test_dir_path(cls):
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'demo_project_data')
        return test_path

    @classmethod
    def fake_name(cls, prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number

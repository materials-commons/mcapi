import unittest
import pytest
from os import environ
from os import path as os_path
import demo_project as demo


class TestDemoProject(unittest.TestCase):
    def test_build_demo_project(self):
        with pytest.raises(Exception) as exception_info:
            mcapikey = "totally-bogus"
            host = "http://noda.host"

            builder = demo.DemoProject(host, self._make_test_dir_path(), mcapikey)

            builder.build_project()
        self.assertTrue(str(exception_info.type).find("ConnectionError") > 0)
        self.assertTrue(str(exception_info.value).find("host='noda.host'") > 0)

    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path

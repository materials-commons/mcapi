import unittest
from os import environ
from os import path as os_path
import demo_project as demo

class TestDemoProjectBasic(unittest.TestCase):

    def test_build_demo_project(self):
        builder = demo.DemoProject(self._make_test_dir_path())

        project, experiment = builder.build_project()

        self.assertIsNotNone(project)
        self.assertIsNotNone(experiment)
        self.assertIsNotNone(experiment.project)
        self.assertIsNotNone(experiment.processes)

    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'test_upload_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path


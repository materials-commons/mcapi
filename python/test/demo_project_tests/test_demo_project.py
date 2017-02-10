import unittest
from os import environ
from os import path as os_path
import demo_project as demo

class TestDemoProject(unittest.TestCase):

    def test_build_demo_project(self):

        # Expected test values
        expected = {
            'project_name': 'Demo Project',
            'experiment_name': 'Microsegregation in HPDC L380',
            'process_names': [],
            'sample_names': [],
        }

        builder = demo.DemoProject(self._make_test_dir_path())

        table = builder._make_template_table()
        self.assertIsNotNone(builder._template_id_with(table,'Create'))
        self.assertIsNotNone(builder._template_id_with(table,'Sectioning'))
        self.assertIsNotNone(builder._template_id_with(table,'EBSD SEM'))
        self.assertIsNotNone(builder._template_id_with(table,'EPMA'))

        project, experiment = builder.build_project()
        self.assertIsNotNone(project)
        self.assertIsNotNone(experiment)
        self.assertIsNotNone(experiment.project)
        self.assertIsNotNone(experiment.processes)
        self.assertEqual(project.id,experiment.project.id)
        self.assertEqual(project.name,expected['project_name'])
        self.assertEqual(experiment.name,expected['experiment_name'])
        #self.assertEqual(len(experiment.processes),len(expected['process_names']))
        #self.assertEqual(len(experiment.samples), len(expected['sample_names']))


    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path


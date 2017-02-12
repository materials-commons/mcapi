import unittest
from os import environ
from os import path as os_path
import demo_project as demo

class TestDemoProject(unittest.TestCase):

    def test_build_demo_project(self):

        # Expected test values
        sample_names = [
            'l380', 'L124', 'L124 - 2mm plate', 'L124 - 3mm plate',
            'L124 - 5mm plate', 'L124 - 5mm plate - 3ST', 'L124 - tensil bar, gage'
        ]
        process_names = [
            'Lift 380 Casting Day  # 1','Casting L124','Sectioning of Casting L124',
            'EBSD SEM Data Collection - 5 mm plate','EPMA Data Collection - 5 mm plate - center'
        ]
        expected = {
            'project_name': 'Demo Project',
            'experiment_name': 'Microsegregation in HPDC L380',
            'process_names': process_names,
            'sample_names': sample_names,
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
        self.assertEqual(len(experiment.processes),len(expected['process_names']))
        print ""
        print "----"
        for sample in experiment.samples:
            print sample.name
        print "----"
        self.assertEqual(len(experiment.samples), len(expected['sample_names']))


    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path


import unittest
from os import environ
from os import path as os_path
import demo_project as demo

class TestDemoProject(unittest.TestCase):

    def test_build_demo_project(self):

        # Expected test values
        project_name = 'Demo Project'
        experiment_name = 'Microsegregation in HPDC L380'
        sample_names = [
            'l380', 'L124', 'L124 - 2mm plate', 'L124 - 3mm plate',
            'L124 - 5mm plate', 'L124 - 5mm plate - 3ST', 'L124 - tensil bar, gage'
        ]
        process_names = [
            'Lift 380 Casting Day  # 1','Casting L124','Sectioning of Casting L124',
            'EBSD SEM Data Collection - 5 mm plate','EPMA Data Collection - 5 mm plate - center'
        ]

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
        self.assertEqual(project.name,project_name)
        self.assertEqual(experiment.name,experiment_name)

        self.assertEqual(len(experiment.processes),len(process_names))
        for name in process_names:
            found_process = None
            for process in experiment.processes:
                if name == process.name:
                    found_process = process
            self.assertIsNotNone(found_process,"Expecting to find process.name == " + name)

        self.assertEqual(len(experiment.samples),len(sample_names))
        for name in sample_names:
            found_sample = None
            for sample in experiment.samples:
                if name == sample.name:
                    found_sample = sample
            self.assertIsNotNone(found_sample, "Expecting to find sample.name == " + name)

    def _make_test_dir_path(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_path = os_path.join(test_path, 'demo_project_data')
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        return test_path


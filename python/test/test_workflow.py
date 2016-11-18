import unittest
from random import randint
from os import environ
from os import path as os_path
from mcapi import create_project, Template
from mcapi import set_remote_config_url, get_remote_config_url
from mcapi import get_process_from_id

url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url(), url)

    def test_workflow(self):
        project_name = "Workflow Project - test001"
        project_description = "a test project generated from api"
        experiment_name = fake_name("Experiment-")
        experiment_description = "a test experiment generated from api"
        sample_name = 'Test Sample 1'
        # process1_name = "Create Simulation Sample"
        # process2_name = "Monte Carlo Simulation"
        # filepath_for_sample = 'test/test_upload_data/sem.tif'
        # filepath_for_compute = 'test/test_upload_data/fractal.jpg'
        filepath_for_sample = self.make_test_dir_path('sem.tif')
        filepath_for_compute = self.make_test_dir_path('fractal.jpg')
        filename_for_sample = "SampleFile.tif"
        filename_for_compute = "ResultsFile.jpg"

        # #-# the workflow #-#
        project = create_project(
            name=project_name,
            description=project_description)

        experiment = project.create_experiment(
            name=experiment_name,
            description=experiment_description)

        create_sample_process = experiment.create_process_from_template(Template.create)
        sample = create_sample_process.create_samples(
            sample_names=[sample_name]
        )[0]

        sample_file = project.add_file_using_directory(
            project.add_directory("/FilesForSample"),
            filename_for_sample,
            filepath_for_sample
        )
        create_sample_process.add_files([sample_file])
        create_sample_process = get_process_from_id(project,experiment,create_sample_process.id)

        compute_process = experiment. \
            create_process_from_template(Template.compute). \
            add_samples_to_process([sample])

        compute_file = project.add_file_using_directory(
            project.add_directory("/FilesForCompute"),
            filename_for_compute,
            filepath_for_compute
        )
        compute_process.add_files([compute_file])
        compute_process = get_process_from_id(project,experiment,compute_process.id)

        # -# tests #-#
        self.assertIsNotNone(project.id)
        self.assertEqual(project_name, project.name)
        self.assertTrue(project_description in project.description)

        self.assertIsNotNone(experiment.id)
        self.assertEqual(experiment_name, experiment.name)
        self.assertEqual(experiment_description, experiment.description)

        self.assertIsNotNone(create_sample_process)
        self.assertIsNotNone(create_sample_process.id)
        self.assertIsNotNone(create_sample_process.process_type)
        self.assertEqual(create_sample_process.process_type, 'create')
        self.assertTrue(create_sample_process.does_transform)

        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertEqual(sample.name, sample_name)

        self.assertIsNotNone(sample_file)
        self.assertIsNotNone(sample_file.name)
        self.assertEqual(sample_file.name, filename_for_sample)

        self.assertIsNotNone(create_sample_process.files)
        self.assertEqual(len(create_sample_process.files), 1)
        file1 = create_sample_process.files[0]
        self.assertIsNotNone(file1)
        self.assertIsNotNone(file1.id)
        self.assertEqual(file1.id,sample_file.id)


        self.assertIsNotNone(compute_process)
        self.assertIsNotNone(compute_process.id)
        self.assertIsNotNone(compute_process.process_type)
        self.assertEqual(compute_process.process_type, 'analysis')
        self.assertFalse(compute_process.does_transform)

        self.assertIsNotNone(compute_file)
        self.assertIsNotNone(compute_file.name)
        self.assertEqual(compute_file.name, filename_for_compute)

        self.assertIsNotNone(compute_process.files)
        self.assertEqual(len(compute_process.files), 1)
        file2 = compute_process.files[0]
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file2.id)
        self.assertEqual(file2.id, compute_file.id)

    def make_test_dir_path(self, file_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        self.assertTrue(os_path.isfile(test_file))
        return test_file

    def setup_test_file(self):
        if not hasattr(self, 'filepath1'):
            self.filepath1 = self.make_test_dir_path('fractal.jpg')
            self.filepath2 = self.make_test_dir_path('sem.tif')
            self.assertTrue(Path(self.filepath1).is_file())
            self.assertTrue(Path(self.filepath2).is_file())

import unittest
from random import randint
from mcapi import create_project, Template
from mcapi import set_remote_config_url, get_remote_config_url

url = 'http://mctest.localhost/api'

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        set_remote_config_url(url)

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url(), url)

    def test_workflow(self):

        project_name = "Project - test001"
        project_description = "is amazing"
        experiment_name = fake_name("Experiment-")
        experiment_description = "a test experiment generated from api"
        sample_name = 'Test Sample 1'
        process1_name = "Create Simulation Sample"
        process2_name = "Monte Carlo Simulation"

        ## the workflow ##
        project = create_project(
            name = project_name,
            description = project_description)

        experiment = project.create_experiment(
            name = experiment_name,
            description = experiment_description)

        create_sample_process = experiment.create_process_from_template(Template.create)
        sample = create_sample_process.create_samples(
            sample_names = [sample_name]
            )[0]

        compute_process = experiment.\
            create_process_from_template(Template.compute).\
            add_samples_to_process([sample])

        ## tests ##
        self.assertIsNotNone(project.id)
        self.assertEqual(project_name,project.name)
        self.assertEqual(project_description,project.description)

        self.assertIsNotNone(experiment.id)
        self.assertEqual(experiment_name,experiment.name)
        self.assertEqual(experiment_description,experiment.description)

        self.assertIsNotNone(create_sample_process)
        self.assertIsNotNone(create_sample_process.id)
        self.assertIsNotNone(create_sample_process.process_type)
        self.assertEqual(create_sample_process.process_type, 'create')
        self.assertTrue(create_sample_process.does_transform)

        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertEqual(sample.name, sample_name)

import unittest
from random import randint
from mcapi import set_remote_config_url
from mcapi import create_project, Template


url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number


class TestSampleCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.project_name = fake_name("TestSampleCreateProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description)
        cls.project_id = cls.project.id
        name = "Test Experiment - basic"
        description = "Test experiment generated by automated test"
        cls.experiment = cls.project.create_experiment(name, description)
        cls.experiment_id = cls.experiment.id

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.project.name)
        self.assertEqual(self.project_name, self.project.name)
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_id, self.project.id)
        self.assertIsNotNone(self.experiment)
        self.assertIsNotNone(self.experiment.id)
        self.assertEqual(self.experiment_id, self.experiment.id)

    def test_create_samples_basic(self):
        process_name = "Create Samples for basic test"
        process = self.experiment.create_process_from_template(Template.create)
        process.rename(process_name)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.category)
        self.assertEqual(process.category,'create_sample')
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'create')
        self.assertTrue(process.does_transform)
        self.assertEqual(process.experiment, self.experiment)
        sample_names = ['Test Sample 1', 'Test Sample 2']
        samples = process.create_samples(sample_names)
        self.assertIsNotNone(samples)
        self.assertEqual(len(samples),2)
        sample = samples[0]
        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.otype)
        self.assertIsNotNone(sample.name)
        self.assertEqual(sample.name, sample_names[0])
        self.assertEqual(sample.project.id, self.project_id)
        self.assertEqual(sample.experiment.id, self.experiment_id)
        experiment_samples = process.experiment.samples
        self.assertTrue(len(experiment_samples) == 2, "The experiment now has 2 samples")
        found_sample = None
        for es in experiment_samples:
            if es.id == sample.id:
                found_sample = es
        self.assertIsNotNone(found_sample,"The original sample is in the experiment")
        self.assertEqual(found_sample.project.id, self.project_id)
        self.assertEqual(found_sample.experiment.id, self.experiment_id)
        self.assertEqual(len(found_sample.processes),1)
        found_process = found_sample.processes[0]
        found_process.project = found_sample.project
        found_process.experiment = found_sample.experiment
        process = found_process.decorate_with_output_samples()
        self.assertIsNotNone(process.output_samples)
        self.assertEqual(len(process.output_samples),2)


    def test_create_samples_multiple(self):
        process_name = "Create Samples for double-add test"
        process = self.experiment.create_process_from_template(Template.create)
        process.rename(process_name)
        sample_names = ['Test Sample 3', 'Test Sample 4','Test Sample 5', 'Test Sample 6']
        samples_a = process.create_samples(sample_names[0:2])
        samples_b = process.create_samples(sample_names[2:4])
        samples = samples_a + samples_b
        self.assertEqual(len(sample_names),len(samples))
        self.assertIsNotNone(process.output_samples)
        self.assertEqual(len(process.output_samples),len(sample_names))

        index = 0
        while index < len(sample_names):
            error = "for index=" + str(index) + ", " + \
                sample_names[index] + " != " + samples[index].name
            self.assertEqual(sample_names[index],samples[index].name,error)
            index += 1
        for sample in samples:
            found_sample = None
            for s in self.experiment.samples:
                if s == sample:
                    found_sample = s
            error = "Cannot fine example in experiment: " + sample.name
            self.assertIsNotNone(found_sample, error)

    def test_create_samples_process_update(self):
        name = "Test Experiment - update"
        description = "Test experiment generated by automated test"
        experiment = self.project.create_experiment(name, description)

        process_name = "Create Samples with process update"
        process = experiment.create_process_from_template(Template.create)
        sample_names = ['Test Sample 7', 'Test Sample 8']
        samples = process.create_samples(sample_names)
        process.decorate_with_output_samples()
        self.assertIsNotNone(samples)
        self.assertEqual(len(samples),2)
        self.assertIsNotNone(process.output_samples)
        self.assertTrue(len(process.output_samples) == 2)

        updated_experiment = experiment.decorate_with_processes()
        self.assertEqual(experiment,updated_experiment)
        self.assertTrue(len(experiment.processes) == 1)
        updated_process = experiment.processes[0]
        self.assertTrue(len(updated_process.output_samples) == 2)


        self.assertTrue(len(experiment.samples) == 2)

        experiment = experiment.decorate_with_samples()
        self.assertTrue(len(experiment.processes) == 1)
        updated_process = experiment.processes[0]

        self.assertTrue(len(experiment.samples) == 2)

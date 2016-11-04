import unittest
from test_object_create_input_examples import data_examples
from mcapi import mc

class TestObjectFactory(unittest.TestCase):

    def test_experiment(self):
        name = 'TestExperiment-from-data'
        description = 'Test experiment from data'
        experiment_data = data_examples['experiment']
        experiment = mc.make_object(experiment_data)
        self.assertIsNotNone(experiment.id)
        self.assertIsNotNone(experiment.name)
        self.assertEqual(name, experiment.name)
        self.assertIsNotNone(experiment.description)
        self.assertEqual(description, experiment.description)
        self.assertEqual(len(experiment.tasks),1)
        self.assertEqual(experiment.tasks[0].note,'Notes here...')
        self.assertFalse(experiment.tasks[0].flags.done)

    def test_process_create(self):
        process_create_data = data_examples['process_create']
        process = mc.make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'create')
        self.assertTrue(process.does_transform)
        self.assertEqual(process.setup[0].process_id,process.id)


    def test_process_compute(self):
        process_create_data = data_examples['process_compute']
        process = mc.make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'analysis')
        self.assertFalse(process.does_transform)
        self.assertEqual(process.setup[0].process_id,process.id)

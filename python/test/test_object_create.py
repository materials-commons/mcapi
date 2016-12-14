import unittest
import datetime
from test_object_create_input_examples import data_examples
from mcapi import mc


class TestObjectFactory(unittest.TestCase):

    def test_timestamp(self):
        timestamp_data = data_examples['timestamp']
        timestamp = mc.make_object(timestamp_data)
        self.assertIsNotNone(timestamp)
        self.assertTrue(isinstance(timestamp,datetime.datetime))

    def test_settings(self):
        settings_data = data_examples['settings']
        settings = mc.make_object(settings_data)
        self.assertIsNotNone(settings)

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
        self.assertEqual(len(experiment.tasks), 1)
        self.assertEqual(experiment.tasks[0].note, 'Notes here...')
        self.assertFalse(experiment.tasks[0].flags.done)

    def test_process_create(self):
        process_create_data = data_examples['process_create']
        process = mc.make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'create')
        self.assertTrue(process.does_transform)
        self.assertEqual(process.setup[0].process_id, process.id)

    def test_process_compute(self):
        process_create_data = data_examples['process_compute']
        process = mc.make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'analysis')
        self.assertFalse(process.does_transform)
        self.assertEqual(process.setup[0].process_id, process.id)

    def test_process_fetch_results(self):
        process_create_data = data_examples['process_create_from_fetch']
        process = mc.make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'analysis')
        self.assertFalse(process.does_transform)
        self.assertEqual(process.setup[0].process_id, process.id)
        self.assertIsNotNone(process.measurements)

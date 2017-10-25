import unittest
import datetime
from .test_object_create_input_examples import data_examples
from materials_commons.api import mc


class TestObjectFactory(unittest.TestCase):

    def test_timestamp(self):
        timestamp_data = data_examples['timestamp']
        timestamp = mc.make_object(timestamp_data)
        self.assertIsNotNone(timestamp)
        self.assertTrue(isinstance(timestamp, datetime.datetime))

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

    def test_process_fetch_create_process(self):
        process_create_data = data_examples['process_create_from_fetch']
        process = mc.make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'create')
        self.assertTrue(process.does_transform)
        self.assertIsNotNone(process.mtime)
        self.assertTrue(isinstance(process.mtime, datetime.datetime))
        self.assertIsNotNone(process.setup)
        self.assertIsNotNone(process.setup[0])
        self.assertEqual(process.setup[0].attribute, 'instrument')
        self.assertEqual(process.setup[0].name, 'Instrument')
        self.assertEqual(len(process.setup[0].properties), 4)
        self.assertEqual(process.setup[0].properties[0].otype, 'string')
        self.assertEqual(process.setup[0].properties[0].attribute, 'manufacturer')
        self.assertEqual(process.setup[0].properties[1].otype, 'string')
        self.assertEqual(process.setup[0].properties[1].attribute, 'supplier')
        self.assertEqual(process.setup[0].properties[2].otype, 'date')
        self.assertEqual(process.setup[0].properties[2].attribute, 'manufacturing_date')
        self.assertEqual(process.setup[0].properties[3].otype, 'selection')
        self.assertEqual(process.setup[0].properties[3].attribute, 'production_method')

#    @pytest.mark.xfail(run=False, reason="test currently failing due to failure to correctly map measure values")

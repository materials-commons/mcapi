import unittest
from object_factory_examples import data_examples
from mcapi import make_object
from mcapi import Project

class TestImportProblem(unittest.TestCase):

    def test_process_create(self):
        process_create_data = data_examples['process_create']
        process = make_object(process_create_data)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'create')
        self.assertTrue(process.does_transform)
        self.assertEqual(process.setup[0].process_id, process.id)

    def test_fake_create_project(self):
        project = Project(name="test", description="test description", id="1234")

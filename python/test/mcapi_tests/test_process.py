import unittest
from random import randint
from mcapi import api
from mcapi import set_remote_config_url, get_remote_config_url
from mcapi import create_project
from mcapi import Template


url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number


class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.base_project_name = fake_name("TestProject-")
        description = "Test project generated by automated test"
        cls.base_project = create_project(cls.base_project_name, description)
        cls.base_project_id = cls.base_project.id
        name = fake_name("TestExperiment-")
        description = "Test experiment generated by automated test"
        cls.base_experiment = cls.base_project.create_experiment(name, description)
        cls.base_experiment_id = cls.base_experiment.id

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.base_project)
        self.assertIsNotNone(self.base_project.name)
        self.assertEqual(self.base_project_name, self.base_project.name)
        self.assertIsNotNone(self.base_project.id)
        self.assertEqual(self.base_project_id, self.base_project.id)
        self.assertIsNotNone(self.base_experiment)
        self.assertIsNotNone(self.base_experiment.id)
        self.assertEqual(self.base_experiment_id, self.base_experiment.id)

    def test_process_from_template_for_create_sample(self):
        process = self.base_experiment.create_process_from_template(Template.create)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'create')
        self.assertTrue(process.does_transform)

    def test_process_from_template_for_computation(self):
        process = self.base_experiment.create_process_from_template(Template.compute)
        self.assertIsNotNone(process)
        self.assertIsNotNone(process.id)
        self.assertIsNotNone(process.process_type)
        self.assertEqual(process.process_type, 'analysis')
        self.assertFalse(process.does_transform)

    def test_rename_process(self):
        new_name = "Procees Test Rename"
        process = self.base_experiment.create_process_from_template(Template.compute)
        undated_process = process.rename(new_name)
        self.assertEqual(undated_process.name, new_name)

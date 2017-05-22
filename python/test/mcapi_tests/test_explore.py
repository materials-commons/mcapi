import unittest
from random import randint
from mcapi import set_remote_config_url
from mcapi import create_project, Template

url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class Explorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.project_name = fake_name("ExperimentalProject-")
        description = "Test project for experimental testing"
        cls.project = create_project(cls.project_name, description)
        cls.project_id = cls.project.id
        name = fake_name("PlayingExperiment-")
        description = "Using experiment this experiment to explore..."
        cls.experiment = cls.project.create_experiment(name, description)
        cls.experiment_id = cls.experiment.id
        cls.process = cls.experiment.create_process_from_template(
            Template.primitive_crystal_structure)
        cls.sample_name = "pcs-sample-1"
        cls.sample = cls.process.create_samples(
            sample_names=[cls.sample_name]
        )[0]

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.project.name)
        self.assertEqual(self.project_name, self.project.name)
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_id, self.project.id)
        self.assertIsNotNone(self.experiment)
        self.assertIsNotNone(self.experiment.id)
        self.assertEqual(self.experiment_id, self.experiment.id)
        self.assertIsNotNone(self.process)
        self.assertIsNotNone(self.process.id)
        self.assertIsNotNone(self.process.process_type)
        self.assertEqual(self.process.process_type, 'create')
        self.assertTrue(self.process.does_transform)

        sample = self.sample
        samples = self.process.output_samples
        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertEqual(sample.name, self.sample_name)
        self.assertEqual(sample.name, samples[0].name)

    def test_set_number_measurement(self):
        attribute = "scale"
        value = 7
        name = "Scaling Factor"

        process = self.process
        process = process.add_number_measurement(attribute, value, name=name)

        print "Again..."
        process = process.add_number_measurement(attribute, value, name=name)

        print "And Again..."
        process = process.add_number_measurement(attribute, value, name=name)
        sample_out = process.output_samples[0]
        sample_with_details = self.project.fetch_sample_by_id(sample_out.id)
        print "-->"
        sample_with_details.pretty_print()

    def make_properties_dictionary(self, properties):
        ret = {}
        for the_property in properties:
            name = the_property.name
            ret[name] = the_property
        return ret

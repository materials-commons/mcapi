import unittest
from random import randint
from materials_commons.api import create_project, Template


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestMultipleMeasuresForSample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        self.assertIsNotNone(self.process.project)
        self.assertEqual(self.process.project.id, self.project.id)
        self.assertIsNotNone(self.process.experiment)
        self.assertEqual(self.process.experiment.id, self.experiment.id)

        sample = self.sample
        samples = self.process.output_samples
        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertIsNotNone(sample.project)
        self.assertEqual(sample.project.id, self.project.id)
        self.assertIsNotNone(sample.experiment)
        self.assertEqual(sample.experiment.id, self.experiment.id)
        self.assertEqual(sample.name, self.sample_name)
        self.assertEqual(sample.name, samples[0].name)

        self.assertIsNotNone(sample.experiment.project)
        self.assertEqual(sample.experiment.project.id, self.project.id)

    def test_set_number_measurement_multiple_times(self):
        attribute = "number"
        name = "Test Measurement"
        process = self.process

        value = 0.1
        process = process.add_number_measurement(attribute, value, name=name)
        value = 1.0
        process = process.add_number_measurement(attribute, value, name=name)
        value = 10.0
        process = process.add_number_measurement(attribute, value, name=name)
        self.assertIsNotNone(self.process.project)
        self.assertEqual(self.process.project.id, self.project.id)
        self.assertIsNotNone(self.process.experiment)
        self.assertEqual(self.process.experiment.id, self.experiment.id)

        sample_out = process.output_samples[0]
        self.assertIsNotNone(sample_out.project)
        self.assertEqual(sample_out.project.id, self.project.id)
        self.assertIsNotNone(sample_out.experiment)
        self.assertEqual(sample_out.experiment.id, self.experiment.id)

        sample_with_details = sample_out.update_with_details()
        self.assertIsNotNone(sample_with_details.project)
        self.assertEqual(sample_with_details.project.id, self.project.id)
        self.assertIsNotNone(sample_with_details.experiment)
        self.assertEqual(sample_with_details.experiment.id, self.experiment.id)

        self.assertIsNotNone(sample_with_details.processes[0])
        measurements = sample_with_details.processes[0].measurements
        self.assertIsNotNone(measurements)

        sample_property = sample_out.properties[0]
        best_measurement = sample_property.best_measure[0]
        self.assertIsNotNone(best_measurement)

        self.assertEqual(sample_out.name, self.sample_name)
        self.assertEqual(sample_out.direction, "out")
        self.assertEqual(sample_property.attribute, attribute)
        self.assertEqual(best_measurement.attribute, attribute)
        self.assertEqual(best_measurement.property_id, sample_property.id)

        found = None
        for measurement in measurements:
            if measurement.id == best_measurement.id:
                found = measurement
        self.assertIsNotNone(found, "Expected best_measurement to be in measurements")

        # print("")
        # print("Process -->")
        # process.pretty_print()
        # print("Sample -->")
        # sample_with_details.pretty_print()
        # print("Measurements...")
        # for measurement in measurements:
        #    print("  --->")
        #    measurement.pretty_print(shift=2)

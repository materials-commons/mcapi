import unittest
import pytest
from random import randint
from mcapi import set_remote_config_url
from mcapi import create_project, Template


url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number


class TestMeasurementComposition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        cls.project_name = fake_name("TestProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description)
        cls.project_id = cls.project.id
        name = fake_name("TestExperiment-")
        description = "Test experiment generated by automated test"
        cls.experiment = cls.project.create_experiment(name, description)
        cls.experiment_id = cls.experiment.id
        cls.process = cls.experiment.create_process_from_template(Template.create)
        cls.sample_name = "Test Sample 1"
        cls.sample = cls.process.create_samples(
            sample_names=[cls.sample_name]
        )[0]
        cls.process = cls.process.add_samples_to_process([cls.sample])

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

    def test_composition(self):
        data = {"name":"Composition",
            "attribute":"composition",
            "otype":"composition",
            "unit":"at%",
            "value":[
                {"element":"Al","value":94},
                {"element":"Ca","value":1},
                {"element":"Zr","value":5}],
            "is_best_measure":True}
        composition = self.process.create_measurement(data=data)
        self.assertEqual(composition.name,"Composition")
        self.assertEqual(composition.attribute,"composition")
        self.assertEqual(composition.otype,"composition")
        self.assertEqual(composition.unit,"at%")
        self.assertTrue(composition.is_best_measure)
        value_list = composition.value
        self.assertEqual(value_list[0]['element'],"Al")
        self.assertEqual(value_list[0]['value'],94)
        self.assertEqual(value_list[1]['element'],"Ca")
        self.assertEqual(value_list[1]['value'],1)
        self.assertEqual(value_list[2]['element'],"Zr")
        self.assertEqual(value_list[2]['value'],5)


#    @pytest.mark.xfail(run=False, reason="test currently failing due to failure to correctly map measure values")
    def test_add_or_update_composition_for_process(self):
        data = {
            "name":"Composition",
            "attribute":"composition",
            "otype":"composition",
            "unit":"at%",
            "value":[
                {"element":"Al","value":94},
                {"element":"Ca","value":1},
                {"element":"Zr","value":5}],
            "is_best_measure":True
        }
        property = {
            "name":"Composition",
            "attribute":"composition"
        }
        measurement = self.process.create_measurement(data=data)
        process_out = self.process.set_measurements_for_process_samples(\
                property, [measurement])
        measurement_out = process_out.measurements[0]
        self.assertEqual(measurement_out.name,measurement.name)
        composition = measurement_out
        self.assertEqual(composition.name,"Composition")
        self.assertEqual(composition.attribute,"composition")
        self.assertEqual(composition.otype,"composition")
        self.assertEqual(composition.unit,"at%")
        self.assertTrue(composition.is_best_measure)
        value_list = composition.value
        self.assertEqual(value_list[0]['element'],"Al")
        self.assertEqual(value_list[0]['value'],94)
        self.assertEqual(value_list[1]['element'],"Ca")
        self.assertEqual(value_list[1]['value'],1)
        self.assertEqual(value_list[2]['element'],"Zr")
        self.assertEqual(value_list[2]['value'],5)
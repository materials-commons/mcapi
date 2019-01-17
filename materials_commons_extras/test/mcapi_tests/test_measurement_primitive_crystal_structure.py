import unittest
from random import randint
from materials_commons.api import create_project, Template


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestMeasurementPrimitiveCrystalStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_name = fake_name("TestProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(cls.project_name, description)
        cls.project_id = cls.project.id
        name = fake_name("TestExperiment-")
        description = "Test experiment generated by automated test"
        cls.experiment = cls.project.create_experiment(name, description)
        cls.experiment_id = cls.experiment.id
        cls.process = cls.experiment.create_process_from_template(Template.primitive_crystal_structure)
        cls.sample_name = "pcs-sample-1"
        cls.samples = cls.process.create_samples(sample_names=[cls.sample_name])
        cls.sample = cls.samples[0]

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

        list = self.process.make_list_of_samples_for_measurement(self.samples)
        self.assertTrue(len(list), 1)
        self.assertIsNotNone(list[0]['property_set_id'])
        self.assertIsNotNone(list[0]['sample'])
        self.assertIsNotNone(list[0]['sample'].id)
        self.assertIsNotNone(list[0]['sample'].name)
        self.assertEqual(list[0]['sample'].id, self.sample.id)
        self.assertEqual(list[0]['sample'].name, self.sample.name)

        samples = self.process.output_samples
        self.assertIsNotNone(samples)
        self.assertEqual(len(samples), 1)
        output_sample = samples[0]
        self.assertIsNotNone(output_sample)
        self.assertIsNotNone(output_sample.id)
        self.assertIsNotNone(output_sample.name)
        self.assertEqual(output_sample.id, self.sample.id)
        self.assertEqual(output_sample.name, self.sample.name)

    def test_measurement_attribute_name(self):
        value = "Test Primitive Crystal Structure"
        data = {"name": "Name",
                "attribute": "name",
                "otype": "string",
                "unit": "",
                "units": [],
                "value": value,
                "is_best_measure": True}
        measurement = self.process.create_measurement(data=data)
        self.assertEqual(measurement.name, "Name")
        self.assertEqual(measurement.attribute, "name")
        self.assertEqual(measurement.otype, "string")
        self.assertEqual(measurement.unit, "")
        self.assertEqual(measurement.value, value)

    def test_add_or_update_attribute_name(self):
        value = "Test Primitive Crystal Structure"
        data = {"name": "Name",
                "attribute": "name",
                "otype": "string",
                "unit": "",
                "units": [],
                "value": value,
                "is_best_measure": True}
        property = {
            "name": "Name",
            "attribute": "name"
        }
        measurement = self.process.create_measurement(data=data)
        process_out = self.process.set_measurements_for_process_samples(
            property, [measurement])
        sample_out = process_out.output_samples[0]
        properties_out = sample_out.properties
        table = self.make_properties_dictionary(properties_out)
        property = table["Name"]
        self.assertEqual(len(property.best_measure), 1)
        measurement_out = property.best_measure[0]
        self.assertEqual(measurement_out.name, measurement.name)
        self.assertEqual(measurement_out.name, "Name")
        self.assertEqual(measurement_out.attribute, "name")
        self.assertEqual(measurement_out.otype, "string")
        self.assertEqual(measurement_out.unit, "")
        self.assertEqual(measurement_out.value, value)

    def test_measurement_attribute_lattice(self):
        value = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        data = {"name": "Lattice",
                "attribute": "lattice",
                "otype": "matrix",
                "unit": "",
                "units": [],
                "value": {
                    "dimensions": [3, 3],
                    "otype": "float",
                    "value": value
                },
                "is_best_measure": True}
        measurement = self.process.create_measurement(data=data)
        self.assertEqual(measurement.name, "Lattice")
        self.assertEqual(measurement.attribute, "lattice")
        self.assertEqual(measurement.otype, "matrix")
        self.assertEqual(measurement.unit, "")
        self.assertEqual(measurement.value['value'], value)

    def test_add_or_update_attribute_lattice(self):
        value = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        data = {"name": "Lattice",
                "attribute": "lattice",
                "otype": "matrix",
                "unit": "",
                "units": [],
                "value": {
                    "dimensions": [3, 3],
                    "otype": "float",
                    "value": value
                },
                "is_best_measure": True}
        property = {
            "name": "Lattice",
            "attribute": "lattice"
        }
        measurement = self.process.create_measurement(data=data)
        process_out = self.process.set_measurements_for_process_samples(
            property, [measurement])
        sample_out = process_out.output_samples[0]
        properties_out = sample_out.properties
        table = self.make_properties_dictionary(properties_out)
        property = table["Lattice"]
        self.assertEqual(len(property.best_measure), 1)
        measurement_out = property.best_measure[0]
        self.assertEqual(measurement_out.name, measurement.name)
        self.assertEqual(measurement_out.name, "Lattice")
        self.assertEqual(measurement_out.attribute, "lattice")
        self.assertEqual(measurement_out.otype, "matrix")
        self.assertEqual(measurement_out.unit, "")
        self.assertEqual(measurement_out.value['value'], value)

    def test_measurement_attribute_parameters(self):
        value = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        data = {"name": "Parameters",
                "attribute": "parameters",
                "otype": "vector",
                "unit": "",
                "units": [],
                "value": {
                    "dimensions": 6,
                    "otype": "float",
                    "value": value
                },
                "is_best_measure": True}
        measurement = self.process.create_measurement(data=data)
        self.assertEqual(measurement.name, "Parameters")
        self.assertEqual(measurement.attribute, "parameters")
        self.assertEqual(measurement.otype, "vector")
        self.assertEqual(measurement.unit, "")
        self.assertEqual(measurement.value['value'], value)

    def test_add_or_update_attribute_parameters(self):
        value = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        data = {"name": "Parameters",
                "attribute": "parameters",
                "otype": "vector",
                "unit": "",
                "units": [],
                "value": {
                    "dimensions": 6,
                    "otype": "float",
                    "value": value
                },
                "is_best_measure": True}
        property = {
            "name": "Parameters",
            "attribute": "parameters"
        }
        measurement = self.process.create_measurement(data=data)
        process_out = self.process.set_measurements_for_process_samples(
            property, [measurement])
        sample_out = process_out.output_samples[0]
        properties_out = sample_out.properties
        table = self.make_properties_dictionary(properties_out)
        property = table["Parameters"]
        self.assertEqual(len(property.best_measure), 1)
        measurement_out = property.best_measure[0]
        self.assertEqual(measurement_out.name, measurement.name)
        self.assertEqual(measurement_out.name, "Parameters")
        self.assertEqual(measurement_out.attribute, "parameters")
        self.assertEqual(measurement_out.otype, "vector")
        self.assertEqual(measurement_out.unit, "")
        self.assertEqual(measurement_out.value['value'], value)

    def test_measurement_attribute_lattice_system(self):
        # noinspection SpellCheckingInspection
        choices = \
            [
                {"name": "Triclinic", "value": "triclinic"},        # 0
                {"name": "Monoclinic", "value": "monoclinic"},      # 1
                {"name": "Orthorhombic", "value": "orthorhombic"},   # 2
                {"name": "Tetragonal", "value": "tetragonal"},       # 3
                {"name": "Hexagonal", "value": "hexagonal"},         # 4
                {"name": "Rhombohedral", "value": "rhombohedral"},   # 5
                {"name": "Cubic", "value": "cubic"}                  # 6
            ]
        value = choices[4]['value']
        data = {"name": "Lattice System",
                "attribute": "lattice_system",
                "otype": "selection",
                "unit": "",
                "units": [],
                "value": value,
                "is_best_measure": True}
        measurement = self.process.create_measurement(data=data)
        self.assertEqual(measurement.name, "Lattice System")
        self.assertEqual(measurement.attribute, "lattice_system")
        self.assertEqual(measurement.otype, "selection")
        self.assertEqual(measurement.unit, "")
        self.assertEqual(measurement.value, value)

    # noinspection SpellCheckingInspection
    def test_add_or_update_attribute_lattice_system(self):
        choices = \
            [
                {"name": "Triclinic", "value": "triclinic"},        # 0
                {"name": "Monoclinic", "value": "monoclinic"},      # 1
                {"name": "Orthorhombic", "value": "orthorhombic"},   # 2
                {"name": "Tetragonal", "value": "tetragonal"},       # 3
                {"name": "Hexagonal", "value": "hexagonal"},         # 4
                {"name": "Rhombohedral", "value": "rhombohedral"},   # 5
                {"name": "Cubic", "value": "cubic"}                  # 6
            ]
        value = choices[4]['value']
        data = {"name": "Lattice System",
                "attribute": "lattice_system",
                "otype": "selection",
                "unit": "",
                "units": [],
                "value": value,
                "is_best_measure": True}
        property = {
            "name": "Lattice System",
            "attribute": "lattice_system"
        }
        measurement = self.process.create_measurement(data=data)
        process_out = self.process.set_measurements_for_process_samples(
            property, [measurement])
        sample_out = process_out.output_samples[0]
        properties_out = sample_out.properties
        table = self.make_properties_dictionary(properties_out)
        property = table["Lattice System"]
        self.assertEqual(len(property.best_measure), 1)
        measurement_out = property.best_measure[0]
        self.assertEqual(measurement_out.name, measurement.name)
        self.assertEqual(measurement_out.name, "Lattice System")
        self.assertEqual(measurement_out.attribute, "lattice_system")
        self.assertEqual(measurement_out.otype, "selection")
        self.assertEqual(measurement_out.unit, "")
        self.assertEqual(measurement_out.value, value)

    def test_measurement_attribute_symmetry(self):
        value = "Test Primitive Crystal Structure"
        data = {"name": "Symmetry",
                "attribute": "symmetry",
                "otype": "string",
                "unit": "",
                "units": [],
                "value": value,
                "is_best_measure": True}
        measurement = self.process.create_measurement(data=data)
        self.assertEqual(measurement.name, "Symmetry")
        self.assertEqual(measurement.attribute, "symmetry")
        self.assertEqual(measurement.otype, "string")
        self.assertEqual(measurement.unit, "")
        self.assertEqual(measurement.value, value)

    def test_add_or_update_attribute_symmetry(self):
        value = ""
        data = {"name": "Name",
                "attribute": "name",
                "otype": "string",
                "unit": "",
                "units": [],
                "value": value,
                "is_best_measure": True}
        property = {
            "name": "Name",
            "attribute": "name"
        }
        measurement = self.process.create_measurement(data=data)
        process_out = self.process.set_measurements_for_process_samples(
            property, [measurement])
        sample_out = process_out.output_samples[0]
        properties_out = sample_out.properties
        table = self.make_properties_dictionary(properties_out)
        property = table["Name"]
        self.assertEqual(len(property.best_measure), 1)
        measurement_out = property.best_measure[0]
        self.assertEqual(measurement_out.name, measurement.name)
        self.assertEqual(measurement_out.name, "Name")
        self.assertEqual(measurement_out.attribute, "name")
        self.assertEqual(measurement_out.otype, "string")
        self.assertEqual(measurement_out.unit, "")
        self.assertEqual(measurement_out.value, value)

    def make_properties_dictionary(self, properties):
        ret = {}
        for property in properties:
            name = property.name
            ret[name] = property
        return ret

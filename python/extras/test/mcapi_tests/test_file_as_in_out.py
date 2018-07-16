import unittest
from random import randint
from os import environ
from os import path as os_path
from os.path import getsize
# noinspection PyCompatibility
from pathlib import Path
from materials_commons.api import create_project
from materials_commons.api import Template, get_all_templates


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestFileAsInOut(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_name = fake_name("TestRenameProject-")
        description = "Test project generated by automated test"
        project = create_project(cls.project_name, description)
        cls.project_id = project.id
        cls.project = project
        print()
        print("-----------")
        print(project.name)
        print("-----------")
        name = fake_name("TestExperiment-")
        description = "Test experiment generated by automated test"
        cls.experiment = cls.project.create_experiment(name, description)
        cls.experiment_id = cls.experiment.id

        cls.process_create1 = cls.experiment.create_process_from_template(Template.create)
        cls.sample_name1 = "setup-sample"
        cls.samples1 = cls.process_create1.create_samples(sample_names=[cls.sample_name1])
        cls.sample1 = cls.samples1[0]

        cls.process_create2 = cls.experiment.create_process_from_template(Template.create)
        cls.sample_name2 = "derived-sample"
        cls.samples2 = cls.process_create2.create_samples(sample_names=[cls.sample_name2])
        cls.sample2 = cls.samples2[0]

        cls.helper = TestFileProcessSampleHelper()
        cls.filepath = cls.helper.filepath
        cls.top_directory = project.get_top_directory()

        cls.directory_name_for_test = "/FilesBeingTested"
        cls.directory_for_test = project.add_directory(cls.directory_name_for_test)

        cls.process_compute = cls.experiment.create_process_from_template(Template.compute)

        cls.measurement_process_name = "Generic Measurement"
        cls.process_measure = cls.helper.create_measurement_process(cls.experiment)

        path = Path(cls.filepath)
        cls.filename = path.parts[-1]
        cls.filepath = str(path.absolute())
        cls.byte_count = getsize(path)
        cls.file = project.add_file_using_directory(cls.directory_for_test, cls.filename, cls.filepath)
        cls.process_measure.rename(cls.measurement_process_name)
        cls.process_measure.add_files([cls.file])

        cls.process_create2.add_input_samples_to_process([cls.sample1])
        cls.process_create2.decorate_with_input_samples()
        cls.process_create2.decorate_with_output_samples()
        output_sample = cls.process_create2.output_samples[0]
        cls.process_compute.add_input_samples_to_process([output_sample])
        cls.process_compute.decorate_with_input_samples()
        cls.process_compute.decorate_with_output_samples()
        cls.process_measure.add_input_samples_to_process([output_sample])
        cls.process_measure.decorate_with_input_samples()
        cls.process_measure.decorate_with_output_samples()

    def test_is_setup_correctly(self):
        self.assertTrue('TEST_DATA_DIR' in environ)
        self.assertIsNotNone(self.filepath)
        self.assertTrue(os_path.isfile(self.filepath))
        self.assertIsNotNone(self.file)
        self.assertEqual(self.file.size, self.byte_count)
        self.assertEqual(self.file.name, self.filename)

        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.project.name)
        self.assertEqual(self.project_name, self.project.name)
        self.assertIsNotNone(self.project.id)
        self.assertEqual(self.project_id, self.project.id)
        self.assertEqual(self.top_directory.name, self.project.name)
        self.assertIsNotNone(self.experiment)
        self.assertIsNotNone(self.experiment.id)
        self.assertEqual(self.experiment_id, self.experiment.id)
        self.assertIsNotNone(self.process_compute)
        self.assertIsNotNone(self.process_compute.id)
        self.assertIsNotNone(self.process_compute.process_type)
        self.assertEqual(self.process_compute.process_type, 'analysis')
        self.assertFalse(self.process_compute.does_transform)
        self.assertEqual(len(self.process_compute.setup), 1)
        self.assertEqual(len(self.process_compute.setup[0].properties), 4)
        self.assertEqual(self.process_compute.setup[0].properties[0].otype, 'string')

        directory_list = self.project.get_all_directories()
        self.assertIsNotNone(directory_list)
        self.assertEqual(len(directory_list), 5)
        self.assertEqual(directory_list[0].name, self.project.name)
        self.assertEqual(directory_list[1].name, self.project.name + self.directory_name_for_test)
        self.assertEqual(self.file.name, self.filename)

    def test_file_as_in(self):
        self.process_compute.pretty_print()
        self.process_measure.pretty_print()


class TestFileProcessSampleHelper:
    def __init__(self):
        filename = 'fractal.jpg'
        self.test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.filepath = os_path.join(self.test_path, 'test_upload_data', filename)

    def create_measurement_process(self, experiment):
        template_table = self.make_template_table()
        template_id = self.template_id_with(template_table, 'Generic Measurement')
        epma_process = experiment.create_process_from_template(template_id)
        return epma_process

    @staticmethod
    def make_template_table():
        template_list = get_all_templates()
        table = {}
        for template in template_list:
            table[template.id] = template
        return table

    @staticmethod
    def template_id_with(table, match):
        found_id = None
        for key in table:
            if match in key:
                found_id = key
        return found_id
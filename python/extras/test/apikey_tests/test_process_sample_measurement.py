import unittest
import pytest
from random import randint
from materials_commons.api import create_project, get_all_templates, Template
from .apikey_helper_utils import make_template_table, find_template_id_from_match


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestProcessSampleMeasurement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"
        cls.another_user = "test@test.mc"
        cls.another_apikey = "totally-bogus"
        cls.templates = make_template_table(get_all_templates())
        project_name = fake_name("TestApikeyProject-")
        description = "Test project generated by automated test"
        cls.project = create_project(project_name, description, apikey=cls.apikey)
        experiment_name = fake_name("TestApikeyExperiment-")
        description = "Test experiment generated by automated test"
        cls.experiment = cls.project.create_experiment(experiment_name, description)
        cls.create_process = cls.experiment.create_process_from_template(Template.create)
        ht_template = find_template_id_from_match(cls.templates, "Heat Treatment")
        cls.ht_process = cls.experiment.create_process_from_template(ht_template)

    @pytest.mark.skip("TestProcessSampleMeasurement")
    def any_test(self):
        pass

# def make_list_of_samples_for_measurement(self, samples):
# def create_measurement(self, data):
# def set_measurements_for_process_samples(self, measurement_property, measurements):
# def set_measurement(self, attribute, measurement_data, name=None):
# def add_integer_measurement(self, attrname, value, name=None):
# def add_number_measurement(self, attrname, value, name=None):
# def add_boolean_measurement(self, attrname, value, name=None):
# def add_string_measurement(self, attrname, value, name=None):
# def add_file_measurement(self, attrname, file, name=None):
# def add_sample_measurement(self, attrname, sample, name=None):
# def add_list_measurement(self, attrname, value, value_type, name=None):
# def add_numpy_matrix_measurement(self, attrname, value, name=None):
# def add_selection_measurement(self, attrname, value, name=None):
# def add_vector_measurement(self, attrname, value, name=None):
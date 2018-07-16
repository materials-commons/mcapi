import unittest
import pytest
from random import randint
from materials_commons.api import api


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestApiSampleRaw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"
        cls.access_user = "test@test.mc"

    @pytest.mark.skip("later")
    def test_get_project_sample_by_id_raw(self):
        # get_project_sample_by_id(project_id, sample_id, remote=None)
        pass

    @pytest.mark.skip("later")
    def test_get_project_samples_raw(self):
        # get_project_samples(project_id, remote=None)
        pass

    @pytest.mark.skip("later")
    def test_fetch_experiment_samples_raw(self):
        # fetch_experiment_samples(project_id, experiment_id, apikey=self.apikey)
        pass

# def delete_sample_created_by_process(project_id, process_id, sample_id, property_set_id, remote=None):
# def get_sample_by_id(project_id, sample_id, remote=None):
# def create_samples_in_project(project_id, process_id, sample_names, remote=None):
# def add_samples_to_experiment(project_id, experiment_id, sample_id_list, remote=None):
# def fetch_sample_details(project_id, sample_id, remote=None):


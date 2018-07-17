import unittest
import pytest
from random import randint
from materials_commons.api import api


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


@pytest.mark.skip("Unimplemented - TestApiFileProcessSampleRaw")
class TestApiFileProcessSampleRaw(unittest.TestCase):

    def test_add_files_to_process(self):
        # def add_files_to_process(project_id, experiment_id, process, files, remote=None):
        pass

    def test_get_all_files_for_process_raw(self):
        # def get_all_files_for_process(project_id, experiment_id, process_id, remote=None):
        pass

    def test_link_files_to_sample_raw(self):
        # def link_files_to_sample(project_id, sample_id, file_id_list, remote=None):
        pass

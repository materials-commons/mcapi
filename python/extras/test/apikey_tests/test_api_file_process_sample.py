import unittest
import pytest
from random import randint
from materials_commons.api import api


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestApiFileProcessSampleRaw(unittest.TestCase):

    @pytest.mark.skip("Unimplemented - TestApiFileProcessSampleRaw - test_add_files_to_process")
    def test_add_files_to_process(self):
        # def add_files_to_process(project_id, experiment_id, process, files, remote=None):
        pass

    @pytest.mark.skip("Unimplemented - TestApiFileProcessSampleRaw - test_get_all_files_for_process_raw")
    def test_get_all_files_for_process_raw(self):
        # def get_all_files_for_process(project_id, experiment_id, process_id, remote=None):
        pass

    @pytest.mark.skip("Unimplemented - TestApiFileProcessSampleRaw - test_link_files_to_sample_raw")
    def test_link_files_to_sample_raw(self):
        # def link_files_to_sample(project_id, sample_id, file_id_list, remote=None):
        pass

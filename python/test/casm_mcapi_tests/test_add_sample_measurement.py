import unittest
import pytest
from random import randint
from mcapi import set_remote_config_url
from mcapi import create_project, Template
from casm_mcapi import _add_file_measurement


url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number

class TestAddSampleMeasurements(unittest.TestCase):

    @pytest.mark.skip("No tests for _add_sample_measurement: no API for property_set")
    def test(self):
        pass
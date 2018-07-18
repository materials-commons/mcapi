import unittest
from materials_commons.api.config import Config
from materials_commons.api.remote import RemoteWithApikey
from materials_commons.api.api import configure_remote


class TestProcessPropMeasRaw(unittest.TestCase):

    def test__raw(self):
        self.assertTrue(False)

# def set_measurement_for_process_samples(project_id, experiment_id, process_id,
#                                        samples, measurement_property, measurements, remote=None):
# def update_process_setup_properties(project_id, experiment_id, process, properties, remote=None):
# def update_additional_properties_in_process(project_id, experiment_id, process_id, properties, remote=None):


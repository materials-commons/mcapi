import unittest
import pytest
from random import randint
from materials_commons.api import api


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


@pytest.mark.skip("Unimplemented - TestApiFileBasicRaw")
class TestApiFileBasicRaw(unittest.TestCase):

    def test_file_rename_raw(self):
        # def file_rename(project_id, file_id, new_file_name, apikey=self.apikey)
        pass

    def test_file_move_raw(self):
        # def file_move(project_id, old_directory_id, new_directory_id, file_id, apikey=self.apikey
        pass



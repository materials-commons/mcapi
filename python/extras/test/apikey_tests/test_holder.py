import unittest
import pytest
from random import randint


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


@pytest.mark.skip("Defered")
class TestHolder(unittest.TestCase):

    def test(self):
        self.assertEqual(" ", "api/EtlMetadata.py")
        self.assertEqual(" ", "api/for_testing_backend.py")
        self.assertEqual(" ", "api/Experiment.py")
        self.assertEqual(" ", "api/File.py")
        self.assertEqual(" ", "api/Sample.py")
        self.assertEqual(" ", "api/Process.py")
        self.assertEqual(" ", "api/Directory.py")

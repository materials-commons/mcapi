import unittest
import pytest
from random import randint


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestHolder(unittest.TestCase):

    @pytest.mark.skip("TestHolder - check this")
    def test1(self):
        self.assertEqual(" ", "extras/test/apikey_tests/test_process_sample_measurement.py")

# measurement in Process.py

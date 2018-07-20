import unittest
import pytest
from random import randint


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


@pytest.mark.skip("TestHolder - check this")
class TestHolder(unittest.TestCase):

    def test(self):
        self.assertEqual(" ", "api/Sample.py")

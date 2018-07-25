import unittest
import pytest
from materials_commons import version
import pkg_resources

class TestVersion(unittest.TestCase):

    @pytest.mark.skip("This test only works in the context of the module - TestVersion")
    def test_version(self):
        print("Code version is ",version.version())
        with open(pkg_resources.resource_filename('materials_commons', 'VERSION.txt')) as f:
            self.assertEqual(f.read().strip(),version.version())
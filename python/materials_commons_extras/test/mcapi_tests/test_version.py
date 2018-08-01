import unittest
import pytest
from materials_commons import version
import pkg_resources


class TestVersion(unittest.TestCase):

    @pytest.mark.skip("Skipping TestVersion::test_version - does not work when materials_commons is not installed")
    def test_version(self):
        print("Code version is ",version.version())
        with open(pkg_resources.resource_filename('materials_commons', 'VERSION.txt')) as f:
            self.assertEqual(f.read().strip(),version.version())
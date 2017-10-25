import pip
import unittest
import sys


class TestModules(unittest.TestCase):
    def test_modules(self):
        print("")
        print("----")
        print(sys.path)
        print("----")

        for entry in sorted(["%s==%s" % (i.key, i.version) for i in pip.get_installed_distributions()]):
            print(entry)

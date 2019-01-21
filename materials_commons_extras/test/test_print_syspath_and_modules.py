import pkg_resources
import unittest
import sys


class TestModules(unittest.TestCase):
    def test_modules(self):
        print("")
        print("----")
        print("")
        print("Output from extras/test/test_print_syspath_and_modules.py")
        print("")
        print("---- sys.path ----")
        for entry in sorted(sys.path):
            print(entry)
        print("----")
        print("")
        print("---- modules ----")
        for entry in sorted([d for d in pkg_resources.working_set]):
            print(entry)
        print("----")

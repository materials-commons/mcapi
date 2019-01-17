import unittest
from .cli_test_functions import captured_output, print_string_io
from materials_commons.cli.proj import ProjSubcommand


class TestMCProj(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proj_subcommand = ProjSubcommand()

    def test_mc_proj(self):
        testargs = ['mc', 'proj']
        with captured_output() as (sout, serr):
            self.proj_subcommand(testargs)
        print_string_io(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()

        headers = out[0].split()
        self.assertEqual(headers[0], "name")
        self.assertEqual(headers[1], "owner")
        self.assertEqual(headers[2], "id")

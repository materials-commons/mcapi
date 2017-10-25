import unittest
from .cli_test_functions import captured_output, print_string_io
from materials_commons.cli.remote import remote_subcommand
from materials_commons.api import _use_remote as use_remote


class TestMCRemote(unittest.TestCase):

    def test_mc_remote(self):
        testargs = ['mc', 'remote']
        with captured_output() as (sout, serr):
            remote_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        remote = use_remote()
        url = remote.config.mcurl
        self.assertEqual(url, out[1].split()[1])

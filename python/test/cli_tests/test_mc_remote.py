import unittest
from .cli_test_functions import captured_output, print_stringIO
from mcapi.cli.remote import remote_subcommand
from mcapi import use_remote

class TestMCRemote(unittest.TestCase):

    def test_mc_remote(self):
        testargs = ['mc', 'remote']
        with captured_output() as (sout, serr):
            remote_subcommand(testargs)
        #print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        remote = use_remote()
        url = remote.config.mcurl
        self.assertEqual(url, out[1].split()[1])

import unittest
from mcapi import set_remote_config_url
from cli_test_functions import captured_output, print_stringIO
from mcapi.cli.remote import remote_subcommand

url = 'http://mctest.localhost/api'

class TestMCRemote(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
    
    def test_mc_remote(self):
        testargs = ['mc', 'remote']
        with captured_output(testargs) as (sout, serr):
            remote_subcommand()
        #print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        self.assertEqual(url, out[1].split()[1])
            
            

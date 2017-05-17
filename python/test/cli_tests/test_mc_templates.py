import unittest
import string
import json
from mcapi import set_remote_config_url
from cli_test_functions import captured_output, print_stringIO
from mcapi.cli.templates import templates_subcommand

url = 'http://mctest.localhost/api'

class TestMCTemplates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
    
    def test_mc_templates_all(self):
        testargs = ['mc', 'templates']
        with captured_output(testargs) as (sout, serr):
            templates_subcommand()
        #print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        
        headers = out[0].split()
        self.assertEqual(headers[0], "name")
        self.assertEqual(headers[1], "id")
        
        
        name = [x.split("global_")[0].strip() for x in out if "global_" in x]
        id = [x.split("global_")[1].strip() for x in out if "global_" in x]
        
        for n in name:
            self.assertEqual(name.index(n), id.index(n))
    
    def test_mc_templates_all_json(self):
        testargs = ['mc', 'templates', '--json']
        with captured_output(testargs) as (sout, serr):
            templates_subcommand()
        #print_stringIO(sout)
        templates = json.loads(sout.getvalue())
        self.assertTrue(True)
        
     
    def test_mc_templates_by_name(self):
        testargs = ['mc', 'templates', 'Create Samples']
        with captured_output(testargs) as (sout, serr):
            templates_subcommand()
        #print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        self.assertTrue(True)
    
    def test_mc_templates_by_name_json(self):
        testargs = ['mc', 'templates', '--json', 'Create Samples']
        with captured_output(testargs) as (sout, serr):
            templates_subcommand()
        #print_stringIO(sout)
        template = json.loads(sout.getvalue())
        self.assertTrue(True)
    
    def test_mc_templates_by_id(self):
        testargs = ['mc', 'templates', '--id', 'global_Create Samples']
        with captured_output(testargs) as (sout, serr):
            templates_subcommand()
        #print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        self.assertTrue(True)
    
    def test_mc_templates_by_id_json(self):
        testargs = ['mc', 'templates', '--json', '--id', 'global_Create Samples']
        with captured_output(testargs) as (sout, serr):
            templates_subcommand()
        #2print_stringIO(sout)
        template = json.loads(sout.getvalue())
        self.assertTrue(True)
    
